"""
Real-time stock data streaming application using Interactive Brokers API.

This script connects to Interactive Brokers TWS/Gateway and streams real-time
5-second bar data for a predefined list of stock tickers. Data is saved to
individual CSV files for each ticker.

Requirements:
- ib_insync library
- Active Interactive Brokers TWS or Gateway connection
- Valid market data subscriptions

Usage:
    python candlestream.py

Configuration:
    Modify the connection parameters and ticker list as needed.
    Set output directory via OUTPUT_DIR environment variable or modify DEFAULT_OUTPUT_DIR.
"""

from ib_insync import IB, Stock
import csv
import os
import signal
import sys
from datetime import datetime

# Configuration
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 7496
DEFAULT_CLIENT_ID = 1
DEFAULT_OUTPUT_DIR = 'ibkr_candles'

# Get configuration from environment variables or use defaults
HOST = os.getenv('IB_HOST', DEFAULT_HOST)
PORT = int(os.getenv('IB_PORT', DEFAULT_PORT))
CLIENT_ID = int(os.getenv('IB_CLIENT_ID', DEFAULT_CLIENT_ID))
OUTPUT_DIR = os.getenv('OUTPUT_DIR', DEFAULT_OUTPUT_DIR)

# List of tickers to stream
TICKERS = [
    'SPY', 'QQQ', 'IWM',
    'AEM', 'AEP', 'AGI', 'AMAT', 'AMD', 'AMT', 'AMZN', 'ANET',
    'APH', 'APP', 'ATI', 'AVGO', 'AXP', 'CCJ', 'CDNS', 'CEG',
    'CELH', 'CL', 'CLS', 'CME', 'CNM', 'CNP', 'COST', 'CP',
    'CRBG', 'D', 'DOCS', 'DXCM', 'ETN', 'EXPE', 'FAST', 'FLEX',
    'FTNT', 'GEN', 'HLT', 'HON', 'HPE', 'HWM', 'IBKR', 'ICE',
    'KDP', 'KMI', 'KO', 'LIN', 'LNT', 'LRCX', 'MA', 'MDLZ',
    'MDT', 'META', 'MNST', 'MPC', 'MSFT', 'NDAQ', 'NEE', 'NFLX',
    'NI', 'NKE', 'NTNX', 'NUE', 'NVDA', 'NVT', 'NWSA', 'NXPI',
    'ORLY', 'OTIS', 'QSR', 'RCL', 'ROL', 'SCHW', 'SFM', 'SGI',
    'SMCI', 'TJX', 'TME', 'TPR', 'TSCO', 'UNP', 'USFD', 'V',
    'VLO', 'VST', 'WEC', 'WMB', 'WPM', 'WYNN', 'YUM',
    'TSLA', 'AAPL'
]

# Global variables
ib = None
bars_map = {}


def connect_to_ib():
    """Connect to Interactive Brokers TWS/Gateway."""
    global ib
    try:
        ib = IB()
        ib.connect(HOST, PORT, clientId=CLIENT_ID)
        print(f"Connected to IB at {HOST}:{PORT} with client ID {CLIENT_ID}")
        return True
    except Exception as e:
        print(f"Failed to connect to IB: {e}")
        return False


def setup_output_directory():
    """Create output directory if it doesn't exist."""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
        return True
    except Exception as e:
        print(f"Failed to create output directory: {e}")
        return False


def setup_streaming():
    """Set up real-time bar streaming for all tickers."""
    global bars_map
    
    print(f"Setting up streaming for {len(TICKERS)} tickers...")
    
    for symbol in TICKERS:
        try:
            # Create contract
            contract = Stock(symbol, 'SMART', 'USD')
            
            # Open CSV file
            csv_path = os.path.join(OUTPUT_DIR, f'{symbol}.csv')
            f = open(csv_path, 'a', newline='')
            writer = csv.writer(f)
            
            # Write header if file is empty
            if f.tell() == 0:
                writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Request 5-second bars
            bars = ib.reqRealTimeBars(contract, 5, 'TRADES', False)
            
            # Store context
            bars_map[bars] = {
                'symbol': symbol,
                'writer': writer,
                'file': f
            }
            
            print(f"✓ Set up streaming for {symbol}")
            
        except Exception as e:
            print(f"✗ Failed to set up streaming for {symbol}: {e}")


def on_bar(bars, hasNewBar):
    """Callback function for new bar data."""
    if not hasNewBar:
        return
    
    try:
        ctx = bars_map[bars]
        bar = bars[-1]
        timestamp = bar.time
        
        # Write bar data to CSV
        ctx['writer'].writerow([
            timestamp, bar.open_, bar.high, bar.low, bar.close, bar.volume
        ])
        ctx['file'].flush()
        
        # Optional: Print progress (comment out for less verbose output)
        # print(f"{ctx['symbol']}: {timestamp} - O:{bar.open_} H:{bar.high} L:{bar.low} C:{bar.close} V:{bar.volume}")
        
    except Exception as e:
        print(f"Error processing bar data: {e}")


def register_callbacks():
    """Register callback functions for all bar subscriptions."""
    for bars in bars_map:
        bars.updateEvent += on_bar


def shutdown(signal_num, frame):
    """Graceful shutdown handler."""
    print(f"\nReceived signal {signal_num}, shutting down...")
    
    # Close all files
    for ctx in bars_map.values():
        try:
            ctx['file'].close()
        except:
            pass
    
    # Disconnect from IB
    if ib:
        try:
            ib.disconnect()
        except:
            pass
    
    print("Shutdown complete.")
    sys.exit(0)


def main():
    """Main application entry point."""
    print("=" * 60)
    print("Interactive Brokers Real-Time Data Streamer")
    print("=" * 60)
    print(f"Start time: {datetime.now()}")
    print()
    
    # Setup signal handler
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    
    # Connect to IB
    if not connect_to_ib():
        sys.exit(1)
    
    # Setup output directory
    if not setup_output_directory():
        sys.exit(1)
    
    # Setup streaming
    setup_streaming()
    
    if not bars_map:
        print("No successful streaming setups. Exiting.")
        sys.exit(1)
    
    # Register callbacks
    register_callbacks()
    
    print(f"\nStreaming 5-second bars for {len(bars_map)} tickers")
    print("Press Ctrl+C to stop.")
    print("-" * 60)
    
    # Start the event loop
    try:
        ib.run()
    except KeyboardInterrupt:
        shutdown(signal.SIGINT, None)
    except Exception as e:
        print(f"Unexpected error: {e}")
        shutdown(signal.SIGTERM, None)


if __name__ == "__main__":
    main()
