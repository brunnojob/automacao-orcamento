import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from catalog_mcp import search_products


class CatalogTests(unittest.IsolatedAsyncioTestCase):
    async def run_query(self, rows, query="Luva"):
        response = SimpleNamespace(text=json.dumps(rows), raise_for_status=lambda: None)
        get = AsyncMock(return_value=response)
        client = AsyncMock()
        client.__aenter__.return_value = SimpleNamespace(get=get)
        with patch.dict(os.environ, {"SUPABASE_SERVICE_ROLE_KEY": "test-secret"}):
            with patch.dict(sys.modules, {"httpx": SimpleNamespace(AsyncClient=lambda **kw: client)}):
                result = await search_products(query)
        self.assertEqual(get.call_args.kwargs["params"]["description"], "eq." + query)
        self.assertNotIn("or", get.call_args.kwargs["params"])
        return result

    async def test_catalog_values(self):
        row = {"id": "id", "description": "Luva", "unit_cost": 12.34, "ca": None}
        result = await self.run_query([row])
        self.assertEqual(result["products"][0]["unit_cost"], "12.34")
        self.assertIsNone(result["products"][0]["ca"])

    async def test_missing_and_ambiguous(self):
        self.assertEqual(await self.run_query([]), {"products": []})
        self.assertEqual(await self.run_query([{}, {}]), {"products": []})

    async def test_mismatch(self):
        self.assertEqual(await self.run_query([{"description": "Outro"}]), {"products": []})

    async def test_invalid_query(self):
        with self.assertRaises(ValueError):
            await search_products("")
