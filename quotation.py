import asyncio
import hashlib
import imaplib
import json
import os
import ssl
import time
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

ACCOUNTS = {"rfcomercialnovo@gmail.com": "imap.gmail.com",
            "suportetec@rf-offshore.com": "imap.hostinger.com"}
TARGET = "suportetec@rf-offshore.com"


def mailbox(value):
    return '"' + modified_utf7(value) + '"'


def modified_utf7(value):
    import base64
    result, buffer = [], []
    def flush():
        if buffer:
            result.append("&" + base64.b64encode("".join(buffer).encode("utf-16be")).decode().rstrip("=").replace("/", ",") + "-")
            buffer.clear()
    for char in value:
        if 32 <= ord(char) <= 126:
            flush()
            result.append("&-" if char == "&" else char)
        else:
            buffer.append(char)
    flush()
    return "".join(result)


def price(cost, quantity):
    cost, quantity = Decimal(str(cost)), Decimal(str(quantity))
    if not cost.is_finite() or not quantity.is_finite() or cost < 0 or quantity <= 0:
        raise ValueError("Invalid cost or quantity")
    sale = (cost / Decimal("0.80") * 2).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
    return str(sale), str((sale * quantity).quantize(Decimal(".01"), rounding=ROUND_HALF_UP))


def triggered(subject, body):
    value = unicodedata.normalize("NFKD", subject + " " + body)
    value = "".join(c for c in value if not unicodedata.combining(c)).casefold()
    return any(word in value for word in ("cotacao", "orcamento", "oceanica"))


def connect(address):
    if address not in ACCOUNTS:
        raise ValueError("Mailbox not allowed")
    client = imaplib.IMAP4_SSL(ACCOUNTS[address], ssl_context=ssl.create_default_context(), timeout=30)
    prefix = "GMAIL" if address.endswith("@gmail.com") else "HOSTINGER"
    client.login(address, os.environ[prefix + "_APP_PASSWORD"])
    return client


async def lookup(description):
    import sys
    from pathlib import Path
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).with_name("catalog_mcp.py"))],
        env={"SUPABASE_SERVICE_ROLE_KEY": os.environ["SUPABASE_SERVICE_ROLE_KEY"]})
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("search_products", {"query": description})
            if result.isError:
                raise ValueError("Supabase catalog lookup failed")
            data = result.structuredContent
            if data is None:
                data = json.loads("".join(c.text for c in result.content if c.type == "text"))
            products = data["products"]
            if len(products) != 1:
                raise ValueError("Missing or ambiguous Supabase catalog match")
            return products[0]

async def poll():
    destination = connect(TARGET)
    folder = mailbox("orçamentos")
    try:
        if destination.select(folder)[0] != "OK":
            if destination.create(folder)[0] != "OK":
                raise RuntimeError("Cannot create review folder")
            if destination.select(folder)[0] != "OK":
                raise RuntimeError("Cannot select review folder")
        for address in ACCOUNTS:
            source = connect(address)
            try:
                if source.select("INBOX", readonly=True)[0] != "OK":
                    raise RuntimeError("Cannot select inbox")
                validity = source.response("UIDVALIDITY")[1][0].decode()
                status, values = source.uid("search", None, "ALL")
                if status != "OK":
                    raise RuntimeError("Search failed")
                for uid in values[0].split():
                    key = hashlib.sha256((address + validity + ":" + uid.decode()).encode()).hexdigest()
                    status, existing = destination.uid("search", None, "HEADER", "X-RF-Automation-Key", key)
                    if status != "OK":
                        raise RuntimeError("Deduplication failed")
                    if existing[0]:
                        continue
                    status, fetched = source.uid("fetch", uid, "(BODY.PEEK[])")
                    if status != "OK":
                        raise RuntimeError("Fetch failed")
                    raw = next(part[1] for part in fetched if isinstance(part, tuple))
                    incoming = BytesParser(policy=policy.default).parsebytes(raw)
                    body = incoming.get_body(preferencelist=("plain", "html"))
                    text = body.get_content() if body else ""
                    subject = str(incoming.get("Subject", ""))
                    if not triggered(subject, text):
                        continue
                    from supplier_research import images_from, build_researched
                    message = await build_researched(subject, text, key, images_from(incoming), lookup, price)
                    status, _ = destination.append(folder, None, None, message.as_bytes(policy=policy.SMTP))
                    if status != "OK":
                        raise RuntimeError("APPEND failed")
            finally:
                source.logout()
    finally:
        destination.logout()


def main():
    import logging
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).with_name(".env"), override=False)
    required = ("HOSTINGER_APP_PASSWORD", "GMAIL_APP_PASSWORD", "OPENAI_API_KEY",
                "OPENAI_MODEL", "SUPABASE_SERVICE_ROLE_KEY")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise SystemExit("Configure as variáveis: " + ", ".join(missing))
    while True:
        try:
            asyncio.run(poll())
        except Exception as error:
            logging.error("Polling failed: %s", type(error).__name__)
        time.sleep(60)


if __name__ == "__main__":
    main()
