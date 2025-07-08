# CandleStream

Real-time stock data streaming from Interactive Brokers with automatic CSV storage.

## Features

- Streams 5-second bar data for 80+ popular stocks
- Automatic CSV file generation per ticker
- Configurable connection parameters
- Graceful shutdown with Ctrl+C
- Robust error handling

## Requirements

- Python 3.7+
- Interactive Brokers TWS or Gateway running
- Valid market data subscriptions

## Installation

```bash
pip install ib-insync
```

## Usage

### Basic Usage
```bash
python candlestream.py
```

### Custom Configuration
```bash
export IB_HOST=127.0.0.1
export IB_PORT=7496
export IB_CLIENT_ID=1
export OUTPUT_DIR=data
python candlestream.py
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `IB_HOST` | 127.0.0.1 | IB Gateway/TWS host |
| `IB_PORT` | 7496 | IB Gateway/TWS port |
| `IB_CLIENT_ID` | 1 | Client ID for connection |
| `OUTPUT_DIR` | ibkr_candles | Output directory for CSV storage |

## Output Format

Each ticker generates a CSV file with columns:
- `timestamp` - Bar timestamp
- `open` - Opening price
- `high` - High price
- `low` - Low price
- `close` - Closing price
- `volume` - Volume

## Supported Tickers

Works with any ticker included in your IBKR data subscription. The US Streaming Bundle (Network A, B, C) covers all US exchange-traded stocks. Default configuration includes 80+ popular tickers: SPY, QQQ, IWM, AAPL, TSLA, NVDA, META, MSFT, AMZN, and other major ETFs and blue-chip stocks.

## Interactive Brokers Setup

1. Install and run TWS or IB Gateway
2. Enable API connections: Configuration → API → Settings
3. Add your IP to trusted IPs if running remotely
4. Ensure you have appropriate market data subscriptions (US Streaming Bundle recommended for US stocks)

## License

MIT License