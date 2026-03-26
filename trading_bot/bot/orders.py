"""Order placement logic for Binance Futures."""

from .client import BinanceClient
from .logging_config import get_logger
from .validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
    validate_symbol_against_exchange,
    validate_quantity_precision,
    validate_stop_price,
)

__all__ = ["check_margin_balance", "place_order"]

logger = get_logger(__name__)


def check_margin_balance(client: BinanceClient, required_margin: float) -> bool:
    """Check if available USDT balance is >= required_margin."""
    assets = client.get_account_balance()
    for asset in assets:
        if asset["asset"] == "USDT":
            available = float(asset["availableBalance"])
            return available >= required_margin
    return False


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float = None,
    stop_price: float = None,
    *,
    dry_run: bool = False,
    check_margin: bool = False,
) -> dict:
    """Validate inputs and place a Futures order via the API client."""

    # Step 1: Validate all inputs
    symbol = validate_symbol(symbol)
    validate_symbol_against_exchange(symbol, client)

    side = validate_side(side)
    order_type = validate_order_type(order_type)

    quantity = validate_quantity(str(quantity))
    quantity = validate_quantity_precision(quantity, symbol, client)

    if price is not None:
        price = validate_price(str(price))

    if stop_price is not None:
        stop_price = validate_stop_price(str(stop_price))

    # Ensure required parameters exist for each order type.
    if order_type == "LIMIT" and price is None:
        raise ValueError("--price is required for LIMIT orders.")
    if order_type == "STOP_MARKET" and stop_price is None:
        raise ValueError("--stop-price is required for STOP_MARKET orders.")
    if order_type == "STOP_LIMIT":
        if price is None:
            raise ValueError("--price is required for STOP_LIMIT orders.")
        if stop_price is None:
            raise ValueError("--stop-price is required for STOP_LIMIT orders.")

    # Step 1.5: (Optional) Best-effort margin pre-check.
    # Note: Binance Futures margin depends on leverage and margin mode,
    # so this check can reject valid orders. Keep it opt-in for correctness.
    if check_margin and not dry_run:
        logger.warning("Margin pre-check enabled (best-effort). API is authoritative.")

        if order_type == "MARKET":
            response = client.session.get(
                f"{client.BASE_URL}/fapi/v1/ticker/price?symbol={symbol}"
            )
            response.raise_for_status()
            last_price = float(response.json()["price"])
        elif order_type == "LIMIT":
            last_price = float(price)
        elif order_type == "STOP_MARKET":
            last_price = float(stop_price)
        else:  # STOP_LIMIT
            last_price = float(stop_price)

        required_margin = quantity * last_price
        if not check_margin_balance(client, required_margin):
            raise ValueError("Insufficient margin balance.")

    # Step 2: Build params dict
    api_order_type = order_type
    if order_type == "STOP_LIMIT":
        # Binance Futures uses `type=STOP` for stop-limit (with `price` + `stopPrice`).
        api_order_type = "STOP"

    params = {
        "symbol": symbol,
        "side": side,
        "type": api_order_type,
        # Cast to string for stable signing/encoding.
        "quantity": str(quantity),
    }
    if order_type == "LIMIT":
        params["price"] = str(price)
        params["timeInForce"] = "GTC"
    elif order_type == "STOP_MARKET":
        params["stopPrice"] = str(stop_price)
    elif order_type == "STOP_LIMIT":
        params["price"] = str(price)
        params["stopPrice"] = str(stop_price)
        params["timeInForce"] = "GTC"
    # MARKET: no price or timeInForce

    # Step 3: Log before placing
    log_msg = (
        f"{'Dry-run:' if dry_run else 'Placing'} {order_type} {side} order | "
        f"Symbol: {symbol} | Qty: {quantity} | "
        f"Price: {price if price is not None else 'MARKET'} | Stop Price: {stop_price}"
    )
    if dry_run:
        logger.debug(log_msg)
    else:
        logger.info(log_msg)

    if dry_run:
        # Return request params so callers can display/inspect them.
        return {"dryRun": True, "params": params}

    # Step 4: Place order
    response = client.place_order(params)

    # Step 5: Log success
    logger.info(f"Order placed successfully | OrderId: {response.get('orderId')}")

    return response
