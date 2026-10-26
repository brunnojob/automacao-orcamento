import json
import os
import unicodedata
from decimal import Decimal

PROJECT_URL = "https://cdkbobyevlwxofvcoxcc.supabase.co"


def normalize(value):
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


async def search_products(query):
    import httpx
    query = query.strip()
    if not 1 <= len(query) <= 500:
        raise ValueError("Invalid product query")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
        response = await client.get(
            PROJECT_URL + "/rest/v1/rf_products",
            headers={"apikey": key, "Authorization": "Bearer " + key},
            params={"select": "id,sku,description,unit_cost,ca,photo_url",
                    "active": "eq.true", "description": "eq." + query, "limit": "2"})
        response.raise_for_status()
        products = json.loads(response.text, parse_float=Decimal)
    if len(products) != 1:
        return {"products": []}
    product = products[0]
    if normalize(product["description"]) != normalize(query):
        return {"products": []}
    product["unit_cost"] = str(product["unit_cost"])
    return {"products": products}


def main():
    from mcp.server.fastmcp import FastMCP
    server = FastMCP("rf-supabase-catalog")
    server.tool(name="search_products")(search_products)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
