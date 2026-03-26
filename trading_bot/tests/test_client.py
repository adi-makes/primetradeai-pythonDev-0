import unittest
from unittest.mock import Mock, patch
from bot.client import BinanceClient
from requests.exceptions import HTTPError


class TestBinanceClient(unittest.TestCase):
    def setUp(self):
        self.client = BinanceClient("dummy_key", "dummy_secret")

    @patch("bot.client.requests.Session.get")
    def test_get_server_time_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"serverTime": 1618239081234}
        mock_get.return_value = mock_response

        server_time = self.client.get_server_time()
        self.assertEqual(server_time, 1618239081234)

    @patch("bot.client.requests.Session.get")
    def test_get_account_balance(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "assets": [{"asset": "USDT", "availableBalance": "1000.00"}]
        }
        mock_get.return_value = mock_response

        # Patch get_server_time to not interfere
        self.client.get_server_time = Mock(return_value=123)

        balance = self.client.get_account_balance()
        self.assertEqual(len(balance), 1)
        self.assertEqual(balance[0]["asset"], "USDT")

    @patch("bot.client.requests.Session.post")
    def test_place_order_success(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"orderId": 12345, "status": "NEW"}
        mock_post.return_value = mock_response

        self.client.get_server_time = Mock(return_value=123)
        self.client._sign = Mock(return_value="signature")

        res = self.client.place_order(
            {"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": 0.001}
        )
        self.assertEqual(res["orderId"], 12345)
        self.assertEqual(res["status"], "NEW")

    @patch("bot.client.requests.Session.post")
    def test_place_order_http_error(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("400 Bad Request")
        mock_response.status_code = 400
        mock_response.json.return_value = {"msg": "Margin is insufficient."}
        mock_post.return_value = mock_response

        self.client.get_server_time = Mock(return_value=123)
        self.client._sign = Mock(return_value="signature")

        with self.assertRaises(RuntimeError) as context:
            self.client.place_order(
                {"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": 100}
            )

        self.assertIn("Bad Request", str(context.exception))


if __name__ == "__main__":
    unittest.main()
