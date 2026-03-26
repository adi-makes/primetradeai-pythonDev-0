"""Input validation functions for trading parameters."""

import re
from typing import Any

__all__ = [
    "validate_symbol_against_exchange",
    "validate_quantity_precision",
    "validate_symbol",
    "validate_side",
    "validate_order_type",
    "validate_quantity",
    "validate_price",
    "validate_stop_price",
]

_valid_symbols: set = set()
_symbol_filters_cache: dict = {}


def validate_symbol_against_exchange(symbol: str, client: Any) -> str:
    """Call the exchange info endpoint and validate symbol against it."""

    if not _valid_symbols:
        response = client.session.get(f"{client.BASE_URL}/fapi/v1/exchangeInfo")
        response.raise_for_status()
        data = response.json()
        for s in data.get("symbols", []):
            _valid_symbols.add(s["symbol"])
            _symbol_filters_cache[s["symbol"]] = s.get("filters", [])

    if symbol not in _valid_symbols:
        raise ValueError(f"Symbol '{symbol}' not found on Binance Futures Testnet.")

    return symbol


def validate_quantity_precision(quantity: float, symbol: str, client: Any) -> float:
    """Ensure quantity respects LOT_SIZE constraints of the symbol."""
    if not _valid_symbols:
        validate_symbol_against_exchange(symbol, client)

    filters = _symbol_filters_cache.get(symbol, [])
    lot_size = next((f for f in filters if f.get("filterType") == "LOT_SIZE"), None)

    if not lot_size:
        return quantity

    min_qty = float(lot_size["minQty"])
    step_size = float(lot_size["stepSize"])

    if quantity < min_qty:
        raise ValueError(
            f"Quantity {quantity} is less than minimum allowed ({min_qty})."
        )

    # Get decimal precision from step size
    step_str = lot_size["stepSize"].rstrip("0")
    precision = len(step_str.split(".")[1]) if "." in step_str else 0

    # Needs to be a multiple of step_size. Due to floats, use string comparison or rounding.
    q_decimal = round(quantity / step_size, 8)
    if not q_decimal.is_integer():
        raise ValueError(
            f"Quantity {quantity} is not a multiple of stepSize {step_size}."
        )

    return round(quantity, precision)


def validate_symbol(symbol: str) -> str:
    """Validate and normalize trading symbol."""
    symbol = symbol.strip().upper()
    if not re.match(r"^[A-Z]{2,10}USDT$", symbol):
        raise ValueError(f"Invalid symbol '{symbol}'. Must end in USDT (e.g. BTCUSDT).")
    return symbol


def validate_side(side: str) -> str:
    """Validate order side."""
    side = side.strip().upper()
    if side not in ("BUY", "SELL"):
        raise ValueError(f"Invalid side '{side}'. Must be BUY or SELL.")
    return side


def validate_order_type(order_type: str) -> str:
    """Validate order type."""
    order_type = order_type.strip().upper()
    if order_type not in ("MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT"):
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            "Must be MARKET, LIMIT, STOP_MARKET, or STOP_LIMIT."
        )
    return order_type


def validate_quantity(quantity: str) -> float:
    """Validate and convert quantity to float."""
    try:
        value = float(quantity)
    except ValueError:
        raise ValueError("Quantity must be a positive number.")
    if value <= 0:
        raise ValueError("Quantity must be a positive number.")
    return value


def validate_price(price: str) -> float:
    """Validate and convert price to float."""
    try:
        value = float(price)
    except ValueError:
        raise ValueError("Price must be a positive number.")
    if value <= 0:
        raise ValueError("Price must be a positive number.")
    return value


def validate_stop_price(stop_price: str) -> float:
    """Validate and convert stop price to float."""
    try:
        value = float(stop_price)
    except ValueError:
        raise ValueError("Stop price must be a positive number.")
    if value <= 0:
        raise ValueError("Stop price must be a positive number.")
    return value
