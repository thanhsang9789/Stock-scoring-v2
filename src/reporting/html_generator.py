import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import logging
from typing import Dict, List

class HTMLReportGenerator:
    """
    Generates HTML report from analysis results using Jinja2
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = config.get('output_dir', './reports')
        self.template_dir = 'templates'
        self.template_name = 'report_template.html'
        
        # Create output dir if not exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.env.get_template(self.template_name)

    def generate(self, report_data) -> str:
        """
        Generate HTML report
        
        Args:
            report_data: Report object containing all necessary data
            
        Returns:
            Path to the generated HTML file
        """
        try:
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')
            
            # Prepare data for template
            render_data = {
                'title': self.config.get('title', 'Stock Score V2'),
                'subtitle': self.config.get('subtitle', 'Deep Analysis'),
                'framework': self.config.get('framework', '4-Signal + TRAP'),
                'footer': self.config.get('footer', 'Stock Score V2'),
                'date': date_str,
                'timestamp': timestamp_str,
                'summary': report_data.summary,
                'stocks': report_data.stocks
            }
            
            # Add entry/watch/trap tickers to summary for dashboard
            render_data['summary']['entry_tickers'] = ", ".join([s.ticker for s in report_data.stocks if 'ENTRY' in s.action])
            render_data['summary']['watch_tickers'] = ", ".join([s.ticker for s in report_data.stocks if any(x in s.action for x in ['WATCH', 'NEUTRAL'])])
            render_data['summary']['trap_tickers'] = ", ".join([s.ticker for s in report_data.stocks if 'TRAP' in s.action])
            
            # Render
            html_content = self.template.render(render_data)
            
            # Save
            filename = self.config.get('filename_pattern', 'Stock_Score_V2_{date}.html').format(date=now.strftime('%Y%m%d'))
            output_path = os.path.join(self.output_dir, filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            self.logger.info(f"Report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")
            raise
