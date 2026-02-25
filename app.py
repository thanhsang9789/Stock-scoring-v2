import os
import sys

# Add project root and local lib to path BEFORE any other imports
sys.path.append(os.getcwd())
sys.path.append('/tmp/st_lib')

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from dotenv import load_dotenv

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
from src.utils.utils import load_config, setup_logger
from src.utils.models import Stock

# Page Config
st.set_page_config(
    page_title="Stock Score V2 - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load context/env
load_dotenv()
config = load_config('config/config.yaml')

# --- STYLE ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #a855f7; color: white; font-weight: bold; }
    .status-box { padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    .entry-box { background-color: rgba(34, 197, 94, 0.1); border-left: 5px solid #22c55e; }
    .trap-box { background-color: rgba(239, 68, 68, 0.1); border-left: 5px solid #ef4444; }
    </style>
    """, unsafe_allow_html=True)

# --- APP LOGIC ---
def run_interactive_scan(top_n, lookback_days):
    logger = setup_logger()
    
    # Bridge for Streamlit progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Register API key
    api_key = os.getenv('VNSTOCK_API_KEY', '').strip()
    if api_key and not api_key.startswith('your_api_key'):
        try:
            from vnstock import change_api_key
            change_api_key(api_key)
        except: pass

    # 1. Scanner
    status_text.text("🔍 STEP 0: Đang quét thanh khoản VN100...")
    scanner = VN100LiquidityScanner(config['stocks']['vn100_config'])
    stock_list = scanner.scan_and_select(top_n=top_n, lookback_days=lookback_days)
    
    progress_bar.progress(10)
    status_text.text(f"✅ Đã chọn {len(stock_list)} mã. Đang chuẩn bị phân tích...")
    time.sleep(2) # Short cooldown
    
    # 2. Components
    collector = VNStockCollector(config['data_sources']['vnstock'])
    avg_vol_calc = AvgVolRatioCalculator(config['signals']['avg_vol_ratio'])
    sm_calc = SmartMoneyCalculator(config['signals']['sm_5d'])
    investor_type_analyzer = InvestorTypeAnalyzer(config['signals']['investor_type'])
    price_calc = PriceSignalCalculator(config['signals']['price'])
    scorer = ScoreCalculator(config['scoring'])
    ranker = StockRanker()
    classifier = ActionClassifier(config['actions'])
    trap_detector = TrapDetector(config['trap'])

    # 3. Process
    results = []
    for idx, ticker in enumerate(stock_list, 1):
        # Progress math: 10% to 90%
        p_val = 10 + int((idx / len(stock_list)) * 80)
        progress_bar.progress(p_val)
        status_text.text(f"⏳ [{idx}/{len(stock_list)}] Đang phân tích chuyên sâu mã: {ticker}...")
        
        try:
            if idx > 1: time.sleep(2.5) # API Pacing
            
            data = collector.collect(ticker)
            avg_vol_signal = avg_vol_calc.calculate(data)
            sm_signal = sm_calc.calculate(data)
            investor_type_signal = investor_type_analyzer.analyze(data)
            price_signal = price_calc.calculate(data)
            
            raw_score, multiplier, multiplier_label = scorer.calculate(
                avg_vol_signal, sm_signal, investor_type_signal, price_signal
            )
            final_score = round(raw_score * multiplier, 1)
            trap = trap_detector.detect(avg_vol_signal, sm_signal, data)
            if trap.is_trap: final_score = 0.0
            
            action_data = classifier.classify(final_score, trap.is_trap)
            
            results.append({
                'Rank': idx,
                'Ticker': ticker,
                'Price': data['close'][-1],
                'Change %': round(data['change_pct'][-1], 2),
                'Score': final_score,
                'Action': action_data['action'],
                'Trap': "🚨 TRAP" if trap.is_trap else "✅ Clear",
                'Color': action_data['color']
            })
        except Exception as e:
            st.error(f"Lỗi khi xử lý {ticker}: {e}")

    progress_bar.progress(100)
    status_text.text("✨ Hoàn tất quá trình quét!")
    return pd.DataFrame(results)

# --- AUTHENTICATION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == st.secrets["auth"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Mật khẩu truy cập", type="password", on_change=password_entered, key="password"
        )
        st.info("💡 Vui lòng nhập mật khẩu để tiếp tục.")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Mật khẩu truy cập", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Mật khẩu không đúng.")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()  # Do not continue if check_password is False

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://www.freeiconspng.com/uploads/stock-exchange-icon-png-13.png", width=80)
    st.title("Stock Score V2")
    st.markdown("---")
    st.header("⚙️ Settings")
    scan_limit = st.slider("Stocks to Analyze", 5, 30, 15)
    lookback = st.slider("Liquidity Lookback (Days)", 10, 60, 20)
    st.markdown("---")
    st.info("Phiên bản Web chính thức sử dụng vnstock v3.4.x")

# --- MAIN ---
st.title("🚀 Market Intelligence Dashboard")

tab1, tab2, tab3 = st.tabs(["🔍 Daily Scanner", "📈 Backtest Insights", "⚙️ System Logs"])

with tab1:
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        start_scan = st.button("🔥 START DAILY SCAN")
    with col_info:
        st.write("Nhấn nút để chạy bộ lọc 4 tín hiệu cho Top VN100.")

    if start_scan:
        df_results = run_interactive_scan(scan_limit, lookback)
        
        st.markdown("### 📊 Kết quả quét mới nhất")
        
        # High-level Summary
        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.metric("Tổng mã quét", len(df_results))
        s_col2.metric("Tín hiệu MUA", len(df_results[df_results['Action'].str.contains('ENTRY')]))
        s_col3.metric("Số bẫy (Trap)", len(df_results[df_results['Trap'].str.contains('TRAP')]))
        
        # Display Styled Table
        def color_row(row):
            if "ENTRY" in str(row['Action']): return ['background-color: rgba(34, 197, 94, 0.1)'] * len(row)
            if "TRAP" in str(row['Trap']): return ['background-color: rgba(239, 68, 68, 0.1)'] * len(row)
            return [''] * len(row)

        st.dataframe(df_results.style.apply(color_row, axis=1), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Báo cáo Kiểm thử quá khứ")
    results_file = 'data/historical/results/performance_results.csv'
    if os.path.exists(results_file):
        df_backtest = pd.read_csv(results_file)
        st.dataframe(df_backtest, use_container_width=True)
    else:
        st.warning("Vui lòng chạy Backtest để xem dữ liệu tại đây.")

with tab3:
    st.subheader("System Information")
    st.json(config)
