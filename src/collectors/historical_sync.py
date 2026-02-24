import os
import sys
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from vnstock import Quote, Listing
from src.collectors.vn100_scanner import VN100LiquidityScanner
from src.utils.utils import load_config, setup_logger

class HistoricalDataSync:
    """
    Syncs historical price and flow data for backtesting
    """
    def __init__(self, config: Dict):
        self.config = config
        self.logger = setup_logger()
        self.source = os.getenv('VNSTOCK_SOURCE', 'VCI')
        self.base_path = 'data/historical'
        self.price_path = os.path.join(self.base_path, 'prices')
        self.flow_path = os.path.join(self.base_path, 'flows')
        
        # Ensure directories exist
        os.makedirs(self.price_path, exist_ok=True)
        os.makedirs(self.flow_path, exist_ok=True)

    def sync_vn100(self, lookback_days: int = 180):
        """
        Sync all VN100 stocks
        """
        self.logger.info(f"Starting historical sync for VN100 ({lookback_days} days)...")
        
        # 1. Get VN100 List
        scanner = VN100LiquidityScanner(self.config['stocks']['vn100_config'])
        tickers = scanner.get_vn100_constituents()
        
        # 2. Sync each ticker
        for idx, ticker in enumerate(tickers, 1):
            self.logger.info(f"[{idx}/{len(tickers)}] Syncing {ticker}...")
            
            # Pacing to respect API limits (60 req/min)
            if idx > 1:
                time.sleep(1.5)
                
            self._sync_ticker(ticker, lookback_days)
            
        self.logger.info("Historical sync completed!")

    def _sync_ticker(self, ticker: str, days: int):
        """
        Sync price and flow for a single ticker
        """
        try:
            # 1. Price Data
            q = Quote(symbol=ticker, source=self.source, show_log=False)
            df_price = q.history(count_back=days, interval='1D')
            
            if df_price is not None and not df_price.empty:
                price_file = os.path.join(self.price_path, f"{ticker}_price.csv")
                df_price.to_csv(price_file, index=False, encoding='utf-8-sig')
                self.logger.info(f"  Saved price: {len(df_price)} rows")
            else:
                self.logger.warning(f"  No price data for {ticker}")
                
            # 2. Flow Data (Placeholder for now as v3.4.x limitations exist)
            # In a real scenario, we'd fetch flows here.
            # We create a zero-flow file if it doesn't exist to maintain structure
            flow_file = os.path.join(self.flow_path, f"{ticker}_flow.csv")
            if df_price is not None:
                df_flow = pd.DataFrame({
                    'time': df_price['time'] if 'time' in df_price.columns else [],
                    'prop_net': [0.0] * len(df_price),
                    'foreign_net': [0.0] * len(df_price),
                    'inst_net': [0.0] * len(df_price),
                    'retail_net': [0.0] * len(df_price)
                })
                df_flow.to_csv(flow_file, index=False, encoding='utf-8-sig')
                
        except Exception as e:
            error_msg = str(e)
            if "Rate limit exceeded" in error_msg or "GIỚI HẠN API" in error_msg:
                self.logger.warning(f"Rate limit hit for {ticker}. Waiting 30s...")
                time.sleep(30)
                return self._sync_ticker(ticker, days) # Retry
            self.logger.error(f"  Error syncing {ticker}: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    config = load_config('config/config.yaml')
    sync = HistoricalDataSync(config)
    
    # We can pass days via cmd line or default to 180
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 180
    sync.sync_vn100(lookback_days=days)
