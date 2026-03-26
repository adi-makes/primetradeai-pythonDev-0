# Binance Futures Trading Bot (USDT-M Testnet)

A small Python CLI for placing Binance Futures (USDT-M) testnet orders with input validation, useful logging, and a safe `--dry-run` mode.

## What it does
- Validates `symbol`, `side`, and `order type` (against Binance `exchangeInfo` on first use).
- Validates `quantity` against the exchange `LOT_SIZE` filters.
- Builds signed requests and places orders on the Binance Futures testnet.

## Setup
1. Install dependencies (from repo root):
   - `python3 -m pip install -r trading_bot/requirements.txt`
2. Configure credentials:
   - Copy `trading_bot/.env.example` to `trading_bot/.env`
   - Put your testnet `BINANCE_API_KEY` and `BINANCE_API_SECRET` there
   - `trading_bot/.env` is git-ignored (do not commit real credentials).

## Run (from repo root)
### Dry-run (no keys required)
Use `--dry-run` to validate inputs and display the request params without placing an order:
```bash
python3 -m trading_bot.cli --dry-run --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Place orders
`--type` options:
- `MARKET` (no `--price`, no `--stop-price`)
```bash
python3 -m trading_bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```
- `LIMIT` (requires `--price`)
```bash
python3 -m trading_bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 35000
```
- `STOP_MARKET` (requires `--stop-price`)
```bash
python3 -m trading_bot.cli --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 29000
```
- `STOP_LIMIT` (requires both `--price` and `--stop-price`)
```bash
python3 -m trading_bot.cli --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.001 --price 28900 --stop-price 29000
```

### Interactive mode
```bash
python3 -m trading_bot.cli --interactive
```
You will be prompted for symbol/side/type/amount, and for API credentials if they are not already available via env vars.

## Validation + Error Handling
- The bot validates the trading symbol via Binance `exchangeInfo` and rejects unknown symbols.
- The bot enforces `LOT_SIZE` step sizes for `quantity` using exact `Decimal` math.
- API errors from Binance are surfaced as `RuntimeError` with Binance's `msg` when available.
- Margin pre-check (`--check-margin`):
  - Optional and best-effort only.
  - Binance Futures margin requirements depend on leverage/margin mode, so this pre-check may reject valid orders.
  - For correctness, leave it off unless you need it.

## Logging
- Log file: `trading_bot/logs/trading_bot.log`
- Console output is informational; detailed request debugging is in the log file.
- Signatures are masked in logs for safety.

## Tests
```bash
python3 -m unittest discover -s trading_bot/tests -v
```
