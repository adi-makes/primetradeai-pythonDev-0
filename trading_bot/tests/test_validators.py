import unittest
from trading_bot.bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)


class TestValidators(unittest.TestCase):
    def test_validate_symbol(self):
        self.assertEqual(validate_symbol("BTCUSDT"), "BTCUSDT")
        self.assertEqual(validate_symbol(" btcusdt "), "BTCUSDT")
        with self.assertRaises(ValueError):
            validate_symbol("BTCBUSD")

    def test_validate_side(self):
        self.assertEqual(validate_side("buy"), "BUY")
        self.assertEqual(validate_side("SELL"), "SELL")
        with self.assertRaises(ValueError):
            validate_side("HOLD")

    def test_validate_order_type(self):
        self.assertEqual(validate_order_type("market"), "MARKET")
        self.assertEqual(validate_order_type("LIMIT"), "LIMIT")
        self.assertEqual(validate_order_type("stop_market"), "STOP_MARKET")
        self.assertEqual(validate_order_type("STOP_LIMIT"), "STOP_LIMIT")
        with self.assertRaises(ValueError):
            validate_order_type("INVALID")

    def test_validate_quantity(self):
        self.assertEqual(validate_quantity("1.5"), 1.5)
        with self.assertRaises(ValueError):
            validate_quantity("-1")
        with self.assertRaises(ValueError):
            validate_quantity("abc")

    def test_validate_price(self):
        self.assertEqual(validate_price("50000"), 50000.0)
        with self.assertRaises(ValueError):
            validate_price("0")
        with self.assertRaises(ValueError):
            validate_price("-500")

    def test_validate_stop_price(self):
        self.assertEqual(validate_stop_price("49000"), 49000.0)
        with self.assertRaises(ValueError):
            validate_stop_price("-100")


if __name__ == "__main__":
    unittest.main()
