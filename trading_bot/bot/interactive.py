"""Interactive CLI mode for the Binance Futures Testnet Trading Bot."""

import questionary
from bot.client import BinanceClient
from bot.orders import place_order
from bot.validators import (
    validate_symbol,
    validate_symbol_against_exchange,
    validate_quantity,
    validate_quantity_precision,
    validate_price,
    validate_stop_price,
)

__all__ = ["run_interactive_mode"]


def run_interactive_mode(client: BinanceClient) -> None:
    """Run the interactive CLI mode."""
    # Step 1: Welcome banner
    print("========================================")
    print("    BINANCE FUTURES TESTNET BOT")
    print("========================================")

    while True:
        # Step 2: Symbol selection
        symbol = None
        while True:
            raw_symbol = questionary.text("Enter trading symbol (e.g. BTCUSDT):").ask()
            if raw_symbol is None:  # User pressed Ctrl+C
                print("Order cancelled.")
                return

            try:
                sym = validate_symbol(raw_symbol)
                sym = validate_symbol_against_exchange(sym, client)
                symbol = sym
                break
            except ValueError as e:
                print(f"❌ Error: {e}")

        # Step 3: Side selection
        side = questionary.select("Select order side:", choices=["BUY", "SELL"]).ask()
        if side is None:
            print("Order cancelled.")
            return

        # Step 4: Order type selection
        order_type = questionary.select(
            "Select order type:",
            choices=["MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT"],
        ).ask()
        if order_type is None:
            print("Order cancelled.")
            return

        # Step 5: Quantity
        quantity = None
        while True:
            raw_qty = questionary.text("Enter quantity:").ask()
            if raw_qty is None:
                print("Order cancelled.")
                return

            try:
                qty = validate_quantity(raw_qty)
                qty = validate_quantity_precision(qty, symbol, client)
                quantity = qty
                break
            except ValueError as e:
                print(f"❌ Error: {e}")

        # Step 6: Price (conditional)
        price = None
        if order_type in ["LIMIT", "STOP_LIMIT"]:
            while True:
                raw_price = questionary.text("Enter limit price:").ask()
                if raw_price is None:
                    print("Order cancelled.")
                    return
                try:
                    price = validate_price(raw_price)
                    break
                except ValueError as e:
                    print(f"❌ Error: {e}")

        stop_price = None
        if order_type in ["STOP_MARKET", "STOP_LIMIT"]:
            while True:
                raw_stop = questionary.text("Enter stop price:").ask()
                if raw_stop is None:
                    print("Order cancelled.")
                    return
                try:
                    stop_price = validate_stop_price(raw_stop)
                    break
                except ValueError as e:
                    print(f"❌ Error: {e}")

        # Step 7: Confirmation
        print("\n----------------------------------------")
        print("📋  ORDER REQUEST SUMMARY")
        print("----------------------------------------")
        print(f"  Symbol   : {symbol}")
        print(f"  Side     : {side}")
        print(f"  Type     : {order_type}")
        print(f"  Quantity : {quantity}")

        price_str = (
            price
            if price
            else (
                "N/A" if order_type in ["STOP_MARKET", "STOP_LIMIT"] else "N/A (MARKET)"
            )
        )
        print(f"  Price    : {price_str}")
        if order_type in ["STOP_MARKET", "STOP_LIMIT"]:
            print(f"  Stop Prc : {stop_price}")
        print("----------------------------------------\n")

        confirm = questionary.confirm("Confirm and place order?").ask()
        if not confirm:
            print("Order cancelled.")
            return

        # Step 8: Place order and show result
        try:
            response = place_order(
                client=client,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
            )

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
            print(f"❌ Validation Error: {e}")
        except RuntimeError as e:
            print(f"❌ API Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")

        # Step 9: Ask "Place another order?"
        print("")
        place_another = questionary.confirm("Place another order?").ask()
        if not place_another:
            print("Goodbye!")
            break
