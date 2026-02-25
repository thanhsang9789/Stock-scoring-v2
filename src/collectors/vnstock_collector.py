from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from vnstock import Listing, Quote, Trading, Company
import logging
import os
import time

class VNStockCollector:
    """
    Data collector using vnstock library for price and investor flows
    """
    
    def __init__(self, config: Dict):
        """
        Initialize collector with configuration
        
        Args:
            config: Configuration dict with:
                - source: Data source (e.g., 'VCI', 'KBS')
                - timeout: Request timeout
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.source = os.getenv('VNSTOCK_SOURCE', config.get('source', 'VCI'))
    
    def collect(self, ticker: str, days_back: int = 30) -> Dict:
        """
        Collect complete data for a ticker
        
        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to collect
            
        Returns:
            Dict containing ohlcv, flows, metadata and confidence metrics
        """
        data = {
            'ticker': ticker,
            'ohlcv': None,
            'flows': None,
            'sector': 'Unknown',
            'data_confidence': 1.0,
            'data_flags': []
        }
        
        # 1. Get OHLCV Data
        try:
            q = Quote(symbol=ticker, source=self.source, show_log=False)
            
            # Calculate start/end dates to avoid count_back TypeError
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back + 15)
            
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            ohlcv_df = q.history(start=start_str, end=end_str, interval='1D')
            
            if ohlcv_df is not None and not ohlcv_df.empty:
                data['ohlcv'] = ohlcv_df.tail(days_back).reset_index(drop=True)
                # Helper fields for easier access
                data['close'] = data['ohlcv']['close'].tolist()
                data['volume'] = data['ohlcv']['volume'].tolist()
                data['time'] = data['ohlcv']['time'].tolist() if 'time' in data['ohlcv'].columns else []
                
                # Calculate daily change pct
                data['change_pct'] = data['ohlcv']['close'].pct_change().fillna(0) * 100
                data['change_pct'] = data['change_pct'].tolist()
            else:
                raise ValueError(f"No price data for {ticker}")
        except Exception as e:
            self.logger.error(f"Failed to fetch price data for {ticker}: {e}")
            raise
            
        # 2. Get Investor Flow Data
        try:
            # v3.4.x: We check if we can get ANY real flow data
            c = Company(symbol=ticker, source=self.source, show_log=False)
            
            # Since historical pro/inst flows are restricted in open API, 
            # we rely on placeholders but drop confidence.
            flows = self._create_zero_flows(len(data['ohlcv']))
            
            # Check for foreign data consistency (sometimes available even if pro/inst isn't)
            # In a real environment, we'd try multiple sources here.
            
            self.logger.warning(f"Historical investor flows are restricted. Using placeholders for {ticker}.")
            data['flows'] = flows
            data['data_confidence'] -= 0.5 # Drop confidence by 50% if flows are missing
            data['data_flags'].append("MISSING_FLOW_DATA")
            
        except Exception as e:
            self.logger.warning(f"Flow data error for {ticker}: {e}. using zero flows")
            data['flows'] = self._create_zero_flows(len(data['ohlcv']))
            data['data_confidence'] = 0.5
            data['data_flags'].append("FLOW_DATA_ERROR")
            
        # 3. Get Sector Info
        try:
            ov = c.overview()
            if ov is not None and not ov.empty:
                if 'icb_name3' in ov.columns:
                    data['sector'] = ov['icb_name3'].iloc[0]
                elif 'icb_name4' in ov.columns:
                    data['sector'] = ov['icb_name4'].iloc[0]
        except Exception as e:
            error_msg = str(e)
            if "Rate limit exceeded" in error_msg or "GIỚI HẠN API" in error_msg:
                self.logger.warning(f"Rate limit hit for {ticker}. Waiting 20s...")
                time.sleep(20)
                return self.collect(ticker, days_back) # Retry once
            self.logger.debug(f"Non-critical sector info error for {ticker}: {e}")
            
        return data
    
    def _create_zero_flows(self, n_days: int) -> pd.DataFrame:
        """Create fallback zero flows"""
        return pd.DataFrame({
            'prop_net': [0.0] * n_days,
            'foreign_net': [0.0] * n_days,
            'inst_net': [0.0] * n_days,
            'retail_net': [0.0] * n_days
        })
