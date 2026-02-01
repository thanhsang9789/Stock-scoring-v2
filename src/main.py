from datetime import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force UTF-8 encoding for standard output and error on Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

from src.collectors.vn100_scanner import VN100LiquidityScanner
from src.collectors.vnstock_collector import VNStockCollector
from src.signals.avg_vol_ratio import AvgVolRatioCalculator
from src.signals.smart_money import SmartMoneyCalculator
from src.signals.investor_type import InvestorTypeAnalyzer
from src.signals.price import PriceSignalCalculator
from src.scoring.scorer import ScoreCalculator
from src.scoring.ranker import StockRanker
from src.scoring.action_classifier import ActionClassifier
from src.detection.trap_detector import TrapDetector
from src.reporting.html_generator import HTMLReportGenerator
from src.utils.utils import load_config, setup_logger
from src.utils.models import Stock, ReportData

def main():
    # 1. Setup
    logger = setup_logger()
    
    # Register API key if provided in .env (and not the placeholder)
    api_key = os.getenv('VNSTOCK_API_KEY', '').strip()
    if api_key and not api_key.startswith('your_api_key'):
        try:
            from vnstock import change_api_key
            change_api_key(api_key)
            logger.info("VNStock API key registered successfully.")
        except Exception as e:
            logger.warning(f"Failed to register API key: {e}")

    try:
        config = load_config('config/config.yaml')
        # Ensure report directory exists
        os.makedirs(config['report'].get('output_dir', './reports'), exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    # 2. STEP 0: Stock Selection (VN100 Scanner)
    logger.info("STEP 0: Scanning VN100 for top liquid stocks...")
    scanner = VN100LiquidityScanner(config['stocks']['vn100_config'])
    try:
        if config['stocks']['selection_method'] == 'vn100_liquidity':
            stock_list = scanner.scan_and_select(
                top_n=config['stocks']['vn100_config']['top_n'],
                lookback_days=config['stocks']['vn100_config']['lookback_days']
            )
        else:
            stock_list = config['stocks']['custom_list']
        logger.info(f"Selected {len(stock_list)} stocks: {', '.join(stock_list)}")
    except Exception as e:
        logger.error(f"Selection failed: {e}. Using fallback.")
        stock_list = config['stocks']['fallback_list'][:15]

    # 3. STEP 1: Initialize Components
    collector = VNStockCollector(config['data_sources']['vnstock'])
    avg_vol_calc = AvgVolRatioCalculator(config['signals']['avg_vol_ratio'])
    sm_calc = SmartMoneyCalculator(config['signals']['sm_5d'])
    investor_type_analyzer = InvestorTypeAnalyzer(config['signals']['investor_type'])
    price_calc = PriceSignalCalculator(config['signals']['price'])
    scorer = ScoreCalculator(config['scoring'])
    ranker = StockRanker()
    classifier = ActionClassifier(config['actions'])
    trap_detector = TrapDetector(config['trap'])
    report_gen = HTMLReportGenerator(config['report'])

    # 4. STEP 2: Process Stocks
    processed_stocks = []
    for idx, ticker in enumerate(stock_list, 1):
        try:
            logger.info(f"[{idx}/{len(stock_list)}] Analyzing {ticker}...")
            
            # Collect data
            data = collector.collect(ticker)
            
            # Calculate signals
            avg_vol_signal = avg_vol_calc.calculate(data)
            sm_signal = sm_calc.calculate(data)
            investor_type_signal = investor_type_analyzer.analyze(data)
            price_signal = price_calc.calculate(data)
            
            # Scoring
            raw_score, multiplier, multiplier_label = scorer.calculate(
                avg_vol_signal, sm_signal, investor_type_signal, price_signal
            )
            final_score = round(raw_score * multiplier, 1)
            
            # Trap Detection
            trap = trap_detector.detect(avg_vol_signal, sm_signal, data)
            if trap.is_trap:
                final_score = 0.0
                
            # Action classification
            action_data = classifier.classify(final_score, trap.is_trap)
            
            # Create Model
            stock = Stock(
                ticker=ticker,
                date=data['time'][-1] if data['time'] else datetime.now(),
                sector=data['sector'],
                price=data['close'][-1],
                price_change_pct=data['change_pct'][-1],
                avg_vol_ratio_signal=avg_vol_signal,
                smart_money_signal=sm_signal,
                investor_type_signal=investor_type_signal,
                price_signal=price_signal,
                raw_score=raw_score,
                multiplier=multiplier,
                multiplier_label=multiplier_label,
                final_score=final_score,
                action=action_data['action'],
                position=action_data['position'],
                confidence=action_data['confidence'],
                color=action_data['color'],
                trap=trap,
                retail_status=sm_calc.get_retail_status(data)
            )
            processed_stocks.append(stock)
            
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")

    # 5. STEP 3: Rank
    ranked_stocks = ranker.rank(processed_stocks)

    # 6. STEP 4: Generate Report
    summary = {
        'total': len(ranked_stocks),
        'entry': len([s for s in ranked_stocks if 'ENTRY' in s.action]),
        'watch_neutral': len([s for s in ranked_stocks if any(x in s.action for x in ['WATCH', 'NEUTRAL'])]),
        'trap': len([s for s in ranked_stocks if 'TRAP' in s.action])
    }
    
    report_data = ReportData(
        date=datetime.now(),
        generated_at=datetime.now(),
        stocks=ranked_stocks,
        summary=summary
    )
    
    output_path = report_gen.generate(report_data)
    logger.info(f"SUCCESS! Report saved to: {output_path}")

if __name__ == "__main__":
    main()
