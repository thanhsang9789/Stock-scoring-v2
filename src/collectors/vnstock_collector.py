from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from vnstock import Listing, Quote, Trading, Company
import logging
import os

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
            Dict containing ohlcv, flows, and metadata
        """
        data = {
            'ticker': ticker,
            'ohlcv': None,
            'flows': None,
            'sector': 'Unknown'
        }
        
        # 1. Get OHLCV Data
        try:
            q = Quote(symbol=ticker, source=self.source, show_log=False)
            ohlcv_df = q.history(count_back=days_back + 10, interval='1D')
            
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
            # v3.4.x: financial_flow is not available. 
            # We try to get foreign data from company trading stats if available
            c = Company(symbol=ticker, source=self.source, show_log=False)
            stats = c.trading_stats()
            
            # Note: v3.4.x might not provide historical daily flows for Prop/Inst easily via open API
            # For now, we use a zero-filled DataFrame and fill Foreign if we have it
            flows = self._create_zero_flows(len(data['ohlcv']))
            
            # If we have current foreign volume, we could potentially estimate, 
            # but historical daily flow is what's needed for signals.
            # Since it's missing, we'll use placeholder data with a warning.
            self.logger.warning(f"Historical investor flows (Prop/Inst) are not supported in vnstock v3.4.x open API. Using placeholders.")
            data['flows'] = flows
            
        except Exception as e:
            self.logger.warning(f"Flow data error for {ticker}: {e}. using zero flows")
            data['flows'] = self._create_zero_flows(len(data['ohlcv']))
            
        # 3. Get Sector Info
        try:
            ov = c.overview()
            if 'icb_name3' in ov.columns:
                data['sector'] = ov['icb_name3'].iloc[0]
            elif 'icb_name4' in ov.columns:
                data['sector'] = ov['icb_name4'].iloc[0]
        except:
            pass
            
        return data
    
    def _create_zero_flows(self, n_days: int) -> pd.DataFrame:
        """Create fallback zero flows"""
        return pd.DataFrame({
            'prop_net': [0.0] * n_days,
            'foreign_net': [0.0] * n_days,
            'inst_net': [0.0] * n_days,
            'retail_net': [0.0] * n_days
        })
