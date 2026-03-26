# Binance Futures Trading Bot

A Python-based trading bot for executing orders on the Binance Futures Testnet.

## Setup

- Prerequisites: Python 3.8+, pip
- Step 1: Clone repo
- Step 2: `pip install -r requirements.txt`
- Step 3: Register at https://testnet.binancefuture.com and get API credentials
- Step 4: (Optional) Create a `.env` file with:
  ```env
  BINANCE_API_KEY=your_key_here
  BINANCE_API_SECRET=your_secret_here
  ```

## How to Run

Provide copy-paste ready examples for ALL of these:

```bash
# Market Buy
python cli.py --symbol BTCUSDT --side BUY --type MARKET \
  --quantity 0.001 --api-key YOUR_KEY --api-secret YOUR_SECRET

# Limit Sell
python cli.py --symbol BTCUSDT --side SELL --type LIMIT \
  --quantity 0.001 --price 35000 --api-key YOUR_KEY --api-secret YOUR_SECRET

# Stop-Market Sell
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET \
  --quantity 0.001 --stop-price 29000 --api-key YOUR_KEY --api-secret YOUR_SECRET

# Stop-Limit Sell
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT \
  --quantity 0.001 --price 28900 --stop-price 29000 \
  --api-key YOUR_KEY --api-secret YOUR_SECRET

# Interactive mode
python cli.py --interactive --api-key YOUR_KEY --api-secret YOUR_SECRET
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BINANCE_API_KEY` | Your Binance Futures Testnet API Key | Yes |
| `BINANCE_API_SECRET` | Your Binance Futures Testnet API Secret | Yes |

## Project Structure

```text
trading_bot/
├── README.md               # Main project documentation
├── requirements.txt        # Python package dependencies
├── .gitignore              # Ignored files for git
├── .env.example            # Example file for environment variables
├── cli.py                  # Command-line interface entry point
├── logs/                   # Directory containing log files
│   ├── sample_market_order.log # Example logs for Market Buy
│   └── sample_limit_order.log  # Example logs for Limit Sell
└── bot/                    # Bot package
    ├── __init__.py         # Package initialization
    ├── client.py           # Handles Binance API requests
    ├── interactive.py      # Interactive command line wizard
    ├── logging_config.py   # Logging setup configuration
    ├── orders.py           # Order logic and placement execution
    └── validators.py       # Validation logic for CLI inputs
```

## Assumptions

- Testnet only (not for production)
- USDT-M perpetual futures only
- Quantities must respect exchange LOT_SIZE filters
- Server time is used to avoid clock sync issues

## Log File Location

- `trading_bot.log` is created in the project root on first run
