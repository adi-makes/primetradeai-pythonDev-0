"""CLI entry point for the Binance Futures trading bot."""

import argparse
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

from .bot.client import BinanceClient
from .bot.logging_config import get_logger
from .bot.orders import place_order

_dotenv_path = Path(__file__).with_name(".env")
# Load credentials from `trading_bot/.env` when it exists.
load_dotenv(dotenv_path=_dotenv_path, override=False)

log = get_logger(__name__)


def main() -> None:
    """Parse arguments, display summary, and execute the order."""
    parser = argparse.ArgumentParser(description="Binance Futures Testnet Trading Bot")
    parser.add_argument("--symbol", type=str, help="e.g. BTCUSDT")
    parser.add_argument("--side", type=str, help="BUY or SELL")
    parser.add_argument(
        "--type",
        type=str,
        dest="order_type",
        help="Order type: MARKET, LIMIT, STOP_MARKET, STOP_LIMIT",
    )
    parser.add_argument("--quantity", type=float)
    parser.add_argument("--price", type=float, required=False, default=None)
    parser.add_argument("--stop-price", type=float, required=False, default=None)
    parser.add_argument("--api-key", type=str, default=os.getenv("BINANCE_API_KEY"))
    parser.add_argument(
        "--api-secret", type=str, default=os.getenv("BINANCE_API_SECRET")
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Launch interactive CLI mode"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and show the request params without placing the order.",
    )
    parser.add_argument(
        "--check-margin",
        action="store_true",
        help="Enable a best-effort pre-check for margin (may reject valid orders with leverage).",
    )

    args = parser.parse_args()

    if args.interactive:
        import getpass
        from .bot.interactive import run_interactive_mode

        api_key = args.api_key
        api_secret = args.api_secret
        if not api_key:
            api_key = getpass.getpass("Enter Binance API Key: ")
        if not api_secret:
            api_secret = getpass.getpass("Enter Binance API Secret: ")

        try:
            client = BinanceClient(api_key, api_secret)
            run_interactive_mode(client)
        except Exception as e:
            log.exception("Error in interactive mode")
            print(f"❌ Error: {e}")
            sys.exit(1)
        return

    # Non-interactive mode validation
    missing_args = []
    if not args.symbol:
        missing_args.append("--symbol")
    if not args.side:
        missing_args.append("--side")
    if not args.order_type:
        missing_args.append("--type")
    if args.quantity is None:
        missing_args.append("--quantity")
    if not args.dry_run:
        if not args.api_key:
            missing_args.append("--api-key")
        if not args.api_secret:
            missing_args.append("--api-secret")

    if missing_args:
        parser.error(
            f"the following arguments are required in non-interactive mode: {', '.join(missing_args)}"
        )

    # Validate LIMIT requires price
    if args.order_type.upper() == "LIMIT" and args.price is None:
        print("❌ Error: --price is required for LIMIT orders.")
        sys.exit(1)

    if (
        args.order_type.upper() in ["STOP_MARKET", "STOP_LIMIT"]
        and args.stop_price is None
    ):
        print(
            "❌ Error: --stop-price is required for STOP_MARKET and STOP_LIMIT orders."
        )
        sys.exit(1)

    if args.order_type.upper() == "STOP_LIMIT" and args.price is None:
        print("❌ Error: --price is required for STOP_LIMIT orders.")
        sys.exit(1)

    # Print order request summary
    print("----------------------------------------")
    print("📋  ORDER REQUEST SUMMARY")
    print("----------------------------------------")
    print(f"  Symbol   : {args.symbol}")
    print(f"  Side     : {args.side}")
    print(f"  Type     : {args.order_type}")
    print(f"  Quantity : {args.quantity}")
    price_str = (
        args.price
        if args.price
        else (
            "N/A"
            if args.order_type.upper() in ["STOP_MARKET", "STOP_LIMIT"]
            else "N/A (MARKET)"
        )
    )
    print(f"  Price    : {price_str}")
    if args.order_type.upper() in ["STOP_MARKET", "STOP_LIMIT"]:
        print(f"  Stop Prc : {args.stop_price}")
    print("----------------------------------------")

    try:
        client = BinanceClient(args.api_key or "", args.api_secret or "")
        response = place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
            dry_run=args.dry_run,
            check_margin=args.check_margin,
        )

        if args.dry_run:
            print("🧪 Dry run only (order not placed).")
            print("----------------------------------------")
            print("📋 ORDER REQUEST PARAMS")
            print("----------------------------------------")
            print(response.get("params"))
            return

        print("✅ Order placed successfully!")
        print("----------------------------------------")
        print("📊  ORDER RESPONSE")
        print("----------------------------------------")
        print(f"  Order ID    : {response.get('orderId')}")
        print(f"  Status      : {response.get('status')}")
        print(f"  Executed Qty: {response.get('executedQty')}")
        print(f"  Avg Price   : {response.get('avgPrice', 'N/A')}")
        if "stopPrice" in response:
            print(f"  Stop Price  : {response.get('stopPrice')}")
        print("----------------------------------------")

    except ValueError as e:
        if "Insufficient margin balance" in str(e):
            print("⚠️ Margin check: insufficient")

        log.error(f"Validation error: {e}")
        print(f"❌ Validation Error: {e}")
        sys.exit(1)

    except RuntimeError as e:
        log.error(f"API error: {e}")
        print(f"❌ API Error: {e}")
        sys.exit(1)

    except Exception as e:
        log.exception("Unexpected error")
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
