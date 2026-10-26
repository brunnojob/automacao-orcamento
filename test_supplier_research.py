import json
import unittest
from email.message import EmailMessage
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from quotation import price
from supplier_research import images_from, source_urls, build_researched


class ResearchTests(unittest.IsolatedAsyncioTestCase):
    def test_images(self):
        msg = EmailMessage()
        msg.set_content("Cotação")
        msg.add_attachment(b"photo", maintype="image", subtype="png", filename="x.png")
        self.assertEqual(images_from(msg), [(b"photo", "image/png")])

    def test_image_limit(self):
        msg = EmailMessage()
        msg.set_content("Cotação")
        msg.add_attachment(b"x" * 5_000_001, maintype="image", subtype="png")
        with self.assertRaises(ValueError):
            images_from(msg)

    def test_sources(self):
        response = SimpleNamespace(output=[SimpleNamespace(action=SimpleNamespace(
            sources=[{"url": "https://supplier.test/item"}]), content=[])])
        self.assertEqual(source_urls(response), {"https://supplier.test/item"})

    async def test_provisional_price_and_original_photo(self):
        item = SimpleNamespace(description="Luva", quantity=3, identification_notes="Confirmar tamanho")
        research = {"offers": [{"supplier": "Supplier", "url": "https://supplier.test/item",
                               "unit_cost_brl": "10", "limitations": "Frete não incluído"}]}
        with patch("supplier_research.identify", AsyncMock(return_value=[item])):
            with patch("supplier_research.research", AsyncMock(return_value=research)):
                message = await build_researched("Cotação", "3 luvas", "key",
                    [(b"photo", "image/png")], AsyncMock(side_effect=ValueError()), price)
        document = json.loads(message.get_body().get_content())
        row = document["items"][0]
        self.assertEqual(row["ca"], "N/A")
        self.assertEqual(row["price_options"][0]["provisional_subtotal"], "75.00")
        self.assertEqual(document["status"], "pending_human_review")
        self.assertEqual(message["To"], "suportetec@rf-offshore.com")
        self.assertEqual(len(list(message.iter_attachments())), 2)

    async def test_unknown_quantity_has_no_price(self):
        item = SimpleNamespace(description="Luva", quantity=None, identification_notes="")
        with patch("supplier_research.identify", AsyncMock(return_value=[item])):
            with patch("supplier_research.research", AsyncMock(return_value={"offers": []})):
                msg = await build_researched("Cotação", "", "key", [],
                    AsyncMock(return_value={"ca": None, "id": "sku"}), price)
        self.assertEqual(json.loads(msg.get_body().get_content())["items"][0]["price_options"], [])
