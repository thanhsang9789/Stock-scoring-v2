import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.signals.avg_vol_ratio import AvgVolRatioCalculator
from src.signals.smart_money import SmartMoneyCalculator
from src.signals.investor_type import InvestorTypeAnalyzer
from src.signals.price import PriceSignalCalculator
from src.scoring.scorer import ScoreCalculator
from src.detection.trap_detector import TrapDetector
from src.utils.utils import load_config, setup_logger

class BacktestSimulator:
    """
    Simulates Stock Score V2 strategy over historical data
    """
    def __init__(self, config: Dict):
        self.config = config
        self.logger = setup_logger()
        self.base_path = 'data/historical'
        
        # Initialize components as in main.py
        self.avg_vol_calc = AvgVolRatioCalculator(config['signals']['avg_vol_ratio'])
        self.sm_calc = SmartMoneyCalculator(config['signals']['sm_5d'])
        self.investor_type_analyzer = InvestorTypeAnalyzer(config['signals']['investor_type'])
        self.price_calc = PriceSignalCalculator(config['signals']['price'])
        self.scorer = ScoreCalculator(config['scoring'])
        self.trap_detector = TrapDetector(config['trap'])

    def run_all(self, tickers: Optional[List[str]] = None):
        """
        Run backtest for all tickers in historical data
        """
        if tickers is None:
            price_dir = os.path.join(self.base_path, 'prices')
            tickers = [f.split('_')[0] for f in os.listdir(price_dir) if f.endswith('_price.csv')]

        results = []
        for idx, ticker in enumerate(tickers, 1):
            self.logger.info(f"[{idx}/{len(tickers)}] Simulating {ticker}...")
            ticker_results = self.simulate_ticker(ticker)
            if ticker_results is not None and not ticker_results.empty:
                results.append(ticker_results)

        if results:
            full_df = pd.concat(results)
            output_file = os.path.join(self.base_path, 'results', 'signals_log_full.csv')
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            full_df.to_csv(output_file, index=False)
            self.logger.info(f"Simulation completed! Saved to {output_file}")
            return full_df
        return None

    def simulate_ticker(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Simulate a single ticker day-by-day
        """
        try:
            # 1. Load Data
            price_file = os.path.join(self.base_path, 'prices', f"{ticker}_price.csv")
            flow_file = os.path.join(self.base_path, 'flows', f"{ticker}_flow.csv")
            
            if not os.path.exists(price_file) or not os.path.exists(flow_file):
                self.logger.warning(f"Data files missing for {ticker}")
                return None
                
            df_price = pd.read_csv(price_file)
            df_flow = pd.read_csv(flow_file)
            
            # Ensure time format
            if 'time' in df_price.columns:
                df_price['time'] = pd.to_datetime(df_price['time'])
            if 'time' in df_flow.columns:
                df_flow['time'] = pd.to_datetime(df_flow['time'])
            
            # 2. Daily Simulation Loop
            # We need at least 25 days (20 lookup + 5 padding) to start
            start_idx = 25 
            if len(df_price) < start_idx:
                return None
                
            daily_logs = []
            
            for i in range(start_idx, len(df_price)):
                curr_date = df_price.iloc[i]['time']
                
                # Slicing data up to day i (inclusive for signals)
                # Note: Signal calculation logic in calculators uses .tail() 
                # or absolute indexing.
                window_price = df_price.iloc[:i+1]
                window_flow = df_flow.iloc[:i+1]
                
                # Format data for calculators
                data = {
                    'ticker': ticker,
                    'ohlcv': window_price,
                    'close': window_price['close'].tolist(),
                    'volume': window_price['volume'].tolist(),
                    'time': window_price['time'].tolist(),
                    'change_pct': (window_price['close'].pct_change() * 100).fillna(0).tolist(),
                    'flows': window_flow,
                    'sector': 'Unknown'
                }
                
                # Calculate signals (Reuse main.py logic)
                avg_vol_signal = self.avg_vol_calc.calculate(data)
                sm_signal = self.sm_calc.calculate(data)
                investor_type_signal = self.investor_type_analyzer.analyze(data)
                price_signal = self.price_calc.calculate(data)
                
                # Scoring
                raw_score, multiplier, multiplier_label = self.scorer.calculate(
                    avg_vol_signal, sm_signal, investor_type_signal, price_signal
                )
                final_score = round(raw_score * multiplier, 1)
                
                # Trap Detection
                trap = self.trap_detector.detect(avg_vol_signal, sm_signal, data)
                if trap.is_trap:
                    final_score = 0.0
                    
                # Log entry
                log = {
                    'ticker': ticker,
                    'date': curr_date,
                    'price': df_price.iloc[i]['close'],
                    'vol_ratio': avg_vol_signal.value,
                    'sm_flow_5d': sm_signal.value,
                    'raw_score': raw_score,
                    'multiplier': multiplier,
                    'final_score': final_score,
                    'is_trap': trap.is_trap
                }
                daily_logs.append(log)
                
            return pd.DataFrame(daily_logs)
            
        except Exception as e:
            self.logger.error(f"Error simulating {ticker}: {e}")
            return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    config = load_config('config/config.yaml')
    simulator = BacktestSimulator(config)
    
    # Run for all
    simulator.run_all()
