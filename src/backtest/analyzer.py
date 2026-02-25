import os
import sys
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.utils import load_config, setup_logger

class PerformanceAnalyzer:
    """
    Analyzes backtest simulation logs to calculate performance metrics (Win Rate, Returns T+)
    """
    def __init__(self, config: Dict):
        self.config = config
        self.logger = setup_logger()
        self.results_path = 'data/historical/results'
        self.price_path = 'data/historical/prices'

    def analyze(self, signals_file: str = 'signals_log_full.csv'):
        """
        Main analysis entry point
        """
        input_path = os.path.join(self.results_path, signals_file)
        if not os.path.exists(input_path):
            self.logger.error(f"Signals file not found: {input_path}")
            return None

        # 1. Load signals
        df_sig = pd.read_csv(input_path)
        df_sig['date'] = pd.to_datetime(df_sig['date'])
        
        self.logger.info(f"Analyzing {len(df_sig)} generated signals...")

        # 2. Calculate Forward Returns for each signal
        # Map price data efficiently
        processed_data = []
        tickers = df_sig['ticker'].unique()
        
        for ticker in tickers:
            ticker_sigs = df_sig[df_sig['ticker'] == ticker]
            price_file = os.path.join(self.price_path, f"{ticker}_price.csv")
            
            if not os.path.exists(price_file):
                continue
                
            df_price = pd.read_csv(price_file)
            df_price['time'] = pd.to_datetime(df_price['time'])
            df_price = df_price.sort_values('time')
            
            # For each signal date, find close price at T+N
            for idx, row in ticker_sigs.iterrows():
                sig_date = row['date']
                
                # Find index of this date in price df
                price_match = df_price[df_price['time'] == sig_date]
                if price_match.empty:
                    continue
                    
                p_idx = price_match.index[0]
                entry_price = float(df_price.iloc[p_idx]['close'])
                
                # Calculate T+N returns
                for t in [3, 5, 10, 20]:
                    if p_idx + t < len(df_price):
                        exit_price = float(df_price.iloc[p_idx + t]['close'])
                        row[f'return_t{t}'] = round(((exit_price - entry_price) / entry_price) * 100, 2)
                    else:
                        row[f'return_t{t}'] = np.nan
                
                processed_data.append(row)

        df_results = pd.DataFrame(processed_data)
        
        # 3. Aggregate Statistics
        summary = self._generate_summary(df_results)
        
        # Save results
        output_file = os.path.join(self.results_path, 'performance_results.csv')
        df_results.to_csv(output_file, index=False)
        self.logger.info(f"Analysis completed and saved to {output_file}")
        
        return summary

    def _generate_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate statistical summary from returns
        """
        # Thresholds for analysis
        score_levels = [
            ('Strong Entry (>50)', df[df['final_score'] >= 50]),
            ('Entry (30-50)', df[(df['final_score'] >= 30) & (df['final_score'] < 50)]),
            ('Watch (15-30)', df[(df['final_score'] >= 15) & (df['final_score'] < 30)]),
            ('Trap (0.0 & is_trap)', df[df['is_trap'] == True])
        ]
        
        summary = {}
        for label, subset in score_levels:
            if subset.empty:
                continue
                
            metrics = {'count': len(subset)}
            for t in [3, 5, 10]:
                ret_col = f'return_t{t}'
                valid_rets = subset[subset[ret_col].notna()][ret_col]
                
                if not valid_rets.empty:
                    metrics[f'avg_ret_t{t}'] = round(valid_rets.mean(), 2)
                    metrics[f'win_rate_t{t}'] = round((valid_rets > 0).sum() / len(valid_rets) * 100, 1)
                    metrics[f'max_ret_t{t}'] = round(valid_rets.max(), 2)
                    metrics[f'min_ret_t{t}'] = round(valid_rets.min(), 2)
            
            summary[label] = metrics
            
        # Display Summary
        self.logger.info("\n" + "="*50)
        self.logger.info("BACKTEST PERFORMANCE SUMMARY")
        self.logger.info("="*50)
        for label, m in summary.items():
            self.logger.info(f"\n{label}: Samples={m['count']}")
            if 'avg_ret_t5' in m:
                self.logger.info(f"  T+5: Avg={m['avg_ret_t5']}% | WinRate={m['win_rate_t5']}% | Range=[{m['min_ret_t5']}%, {m['max_ret_t5']}%]")
            if 'avg_ret_t10' in m:
                self.logger.info(f"  T+10: Avg={m['avg_ret_t10']}% | WinRate={m['win_rate_t10']}%")
        self.logger.info("="*50)
        
        return summary

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    config = load_config('config/config.yaml')
    analyzer = PerformanceAnalyzer(config)
    analyzer.analyze()
