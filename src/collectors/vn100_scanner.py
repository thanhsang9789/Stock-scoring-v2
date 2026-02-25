from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime, timedelta
from vnstock import Listing, Quote
import logging
import os
import time

class VN100LiquidityScanner:
    """
    Scanner to identify most liquid stocks from VN100 index
    """
    
    def __init__(self, config: Dict):
        """
        Initialize scanner with configuration
        
        Args:
            config: Configuration dict with:
                - top_n: Number of stocks to select
                - lookback_days: Days for liquidity calculation
                - min_trading_value: Minimum daily value threshold (Billion VND)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.source = os.getenv('VNSTOCK_SOURCE', 'VCI')
        self.vn100_constituents = []
        self.liquidity_data = pd.DataFrame()
    
    def get_vn100_constituents(self) -> List[str]:
        """
        Fetch current VN100 constituent stocks
        
        Returns:
            List of ticker symbols in VN100
        """
        try:
            # v3.4.x API way
            l = Listing(source=self.source, show_log=False)
            tickers = l.symbols_by_group('VN100').tolist()
            if tickers:
                self.logger.info(f"Found {len(tickers)} stocks in VN100 group")
                return tickers
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch VN100 group: {e}")
            try:
                # Try all symbols
                df = l.symbols_by_exchange()
                hose_stocks = df[df['exchange'] == 'HOSE']
                if not hose_stocks.empty:
                    tickers = hose_stocks['symbol'].tolist()[:100]
                    self.logger.info(f"Selected first 100 HOSE stocks as backup")
                    return tickers
            except:
                pass
        
        # Method 3: Fallback to known VN100 list
        self.logger.warning("Using fallback VN100 list")
        return self._get_fallback_vn100()
    
    def _get_fallback_vn100(self) -> List[str]:
        """
        Fallback list of VN100 stocks
        """
        return [
            'VCB', 'BID', 'CTG', 'TCB', 'STB', 'MBB', 'VPB', 'ACB', 'HDB', 
            'TPB', 'EIB', 'LPB', 'SHB', 'VIB', 'VHM', 'VIC', 'VRE', 'NVL', 
            'DXG', 'PDR', 'KDH', 'DIG', 'BCM', 'HDG', 'NLG', 'IDC', 'DRH',
            'HPG', 'HSG', 'NKG', 'TLG', 'DCM', 'DGC', 'DPM', 'PHR', 'GVR',
            'GEX', 'HT1', 'CSV', 'AAA', 'VNM', 'MSN', 'MWG', 'FPT', 'PNJ', 
            'SAB', 'VHC', 'GMD', 'DBC', 'PHR', 'TSC', 'GAS', 'PLX', 'PVD', 
            'PVS', 'PVT', 'POW', 'BSR', 'SSI', 'VCI', 'VND', 'HCM', 'MBS', 
            'FTS', 'NT2', 'PC1', 'REE', 'BWE', 'VJC', 'HVN', 'VTP', 'HBC', 
            'CTD', 'FCN', 'LCG', 'VGC', 'DHC', 'KBC', 'PDN', 'BVH', 'SBT', 'KDC'
        ]
    
    def calculate_liquidity_metrics(
        self, 
        ticker: str, 
        lookback_days: int = 20
    ) -> Dict:
        """
        Calculate liquidity metrics for a stock
        """
        try:
            # v3.4.x API way
            q = Quote(symbol=ticker, source=self.source, show_log=False)
            
            # Calculate start/end dates to avoid count_back TypeError in some versions
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 15)
            
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            df = q.history(start=start_str, end=end_str, interval='1D')
            
            # Ensure we have data
            if df is None or len(df) == 0:
                raise ValueError(f"No data returned for {ticker}")
            
            # Take last N trading days
            df = df.tail(lookback_days)
            
            # Calculate trading value (price x volume)
            df['trading_value'] = df['close'] * df['volume']
            
            # Calculate metrics
            metrics = {
                'ticker': ticker,
                'avg_trading_value': df['trading_value'].mean(),
                'avg_volume': df['volume'].mean(),
                'avg_price': df['close'].mean(),
                'total_trading_value': df['trading_value'].sum(),
                'latest_price': df['close'].iloc[-1],
                'latest_volume': df['volume'].iloc[-1],
                'data_points': len(df),
                'date': df['time'].iloc[-1] if 'time' in df.columns else datetime.now()
            }
            
            return metrics
            
        except Exception as e:
            error_msg = str(e)
            if "Rate limit exceeded" in error_msg or "GIỚI HẠN API" in error_msg:
                self.logger.warning(f"Rate limit hit for {ticker}. Waiting 20s...")
                time.sleep(20)
                return self.calculate_liquidity_metrics(ticker, lookback_days) # Retry once
            
            self.logger.error(f"Failed to calculate liquidity for {ticker}: {e}")
            return None
    
    def scan_and_select(
        self, 
        top_n: int = 15, 
        lookback_days: int = 20
    ) -> List[str]:
        """
        Main method: Scan VN100 and select top N liquid stocks
        """
        self.logger.info("=" * 60)
        self.logger.info("VN100 LIQUIDITY SCANNER")
        self.logger.info("=" * 60)
        
        # Step 1: Get VN100 constituents
        self.vn100_constituents = self.get_vn100_constituents()
        
        # Step 2: Calculate liquidity for each stock
        liquidity_results = []
        for idx, ticker in enumerate(self.vn100_constituents, 1):
            # Community limit is 60 req/min. Let's pace it at ~1.1s per request to be safe
            if idx > 1:
                time.sleep(1.1)
                
            if idx % 10 == 0:
                self.logger.info(f"Scanning progress: {idx}/{len(self.vn100_constituents)} stocks...")
                
            metrics = self.calculate_liquidity_metrics(ticker, lookback_days)
            if metrics is not None:
                liquidity_results.append(metrics)
        
        # Step 3: Create DataFrame and rank
        self.liquidity_data = pd.DataFrame(liquidity_results)
        if len(self.liquidity_data) == 0:
            raise ValueError("No liquidity data collected")
        
        # Sort by average trading value
        self.liquidity_data = self.liquidity_data.sort_values(
            'avg_trading_value', 
            ascending=False
        )
        
        # Add rank
        self.liquidity_data['rank'] = range(1, len(self.liquidity_data) + 1)
        
        # Store for report
        self.selected_tickers = self.liquidity_data.head(top_n)['ticker'].tolist()
        
        return self.selected_tickers

    def get_liquidity_report(self) -> pd.DataFrame:
        return self.liquidity_data.copy()
