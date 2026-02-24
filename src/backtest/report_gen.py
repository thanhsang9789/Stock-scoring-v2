import os
import sys
import pandas as pd
from datetime import datetime
from jinja2 import Template
from typing import Dict

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.utils import load_config, setup_logger

class BacktestReportGenerator:
    """
    Generates HTML reports for Backtest results
    """
    def __init__(self, config: Dict):
        self.config = config
        self.logger = setup_logger()
        self.results_path = 'data/historical/results'
        self.template_path = 'templates/backtest_template.html'

    def generate(self, summary_data: Dict):
        """
        Create HTML report from summary metrics
        """
        try:
            # 1. Prepare data for template
            total_signals = sum(m['count'] for m in summary_data.values())
            
            # Extract some highlights
            strong_entry = summary_data.get('Strong Entry (>50)', {})
            avg_ret_t5 = strong_entry.get('avg_ret_t5', 0)
            
            # Find best category by win rate
            best_cat = "N/A"
            best_wr = 0
            for label, m in summary_data.items():
                if m.get('win_rate_t5', 0) > best_wr:
                    best_wr = m['win_rate_t5']
                    best_cat = label

            # 2. Render Template
            if not os.path.exists(self.template_path):
                self.logger.error("Backtest template not found!")
                return

            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = Template(f.read())

            html_out = template.render(
                total_signals=total_signals,
                avg_return_t5=avg_ret_t5,
                best_category=best_cat,
                summary=summary_data,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            # 3. Save Report
            report_file = os.path.join(self.results_path, f"Backtest_Report_{datetime.now().strftime('%Y%m%d')}.html")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_out)
            
            self.logger.info(f"HTML Backtest Report generated: {report_file}")
            return report_file

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return None

if __name__ == "__main__":
    # This part allows standalone test or call from analyzer
    from src.backtest.analyzer import PerformanceAnalyzer
    config = load_config('config/config.yaml')
    analyzer = PerformanceAnalyzer(config)
    summary = analyzer.analyze()
    
    if summary:
        gen = BacktestReportGenerator(config)
        gen.generate(summary)
