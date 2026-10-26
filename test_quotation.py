import unittest
from quotation import price, triggered, modified_utf7

class Rules(unittest.TestCase):
    def test_price(self):
        self.assertEqual(price("10", "3"), ("25.00", "75.00"))
    def test_invalid(self):
        for cost, qty in [("NaN", "1"), ("-1", "2"), ("1", "0")]:
            with self.assertRaises(ValueError):
                price(cost, qty)
    def test_triggers(self):
        self.assertTrue(triggered("COTAÇÃO", ""))
        self.assertTrue(triggered("", "Oceânica"))
        self.assertFalse(triggered("Reunião", "agenda"))
    def test_folder(self):
        self.assertEqual(modified_utf7("orçamentos"), "or&AOc-amentos")

if __name__ == "__main__":
    unittest.main()
