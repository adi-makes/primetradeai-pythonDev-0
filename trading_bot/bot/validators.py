"""Input validation functions for trading parameters."""

import re
from typing import Any
from decimal import Decimal

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

    min_qty = Decimal(str(lot_size["minQty"]))
    step_size = Decimal(str(lot_size["stepSize"]))

    q = Decimal(str(quantity))

    if q < min_qty:
        raise ValueError(
            f"Quantity {quantity} is less than minimum allowed ({min_qty})."
        )

    if step_size <= 0:
        return quantity

    # Needs to be a multiple of step_size.
    steps = q / step_size
    if steps != steps.to_integral_value():
        raise ValueError(
            f"Quantity {quantity} is not a multiple of stepSize {step_size}."
        )

    # Normalize to the step precision for stable encoding.
    precision = abs(step_size.as_tuple().exponent)
    if precision == 0:
        adjusted = q.to_integral_value()
    else:
        quant = Decimal("1").scaleb(-precision)  # 10^-precision
        adjusted = q.quantize(quant)

    return float(adjusted)


def validate_symbol(symbol: str) -> str:
    """Validate and normalize trading symbol."""
    symbol = symbol.strip().upper()
    # Allow digits/underscores because Binance uses symbols like `1000PEPEUSDT`.
    if not re.match(r"^[A-Z0-9_]{2,30}USDT$", symbol):
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
