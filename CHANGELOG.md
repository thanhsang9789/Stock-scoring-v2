# Changelog

All notable changes to this project will be documented in this file.

## [2026-02-25]
### Added
- **Security & Auth**: Completed Phase 03. Implemented a password protection layer for the Web App.
- **Interactive Scanning**: Completed Phase 02. Integrated real-time market scanning and scoring into the Streamlit UI with progress bars. 
- **Web Dashboard**: Completed Phase 01. Created `app.py` (Streamlit) and `requirements.txt`.
- **Backtest Reporting**: Completed Phase 04. Created `src/backtest/report_gen.py` and `templates/backtest_template.html`.
- **Final Report**: Generated first HTML Backtest Report with visual metrics and Win Rate analysis.
- **Backtest Analysis**: Completed Phase 03. Created `src/backtest/analyzer.py` to calculate Win Rates and T+3/T+5/T+10 returns.
- **Performance Report**: Generated statistical summary showing positive average returns (~1.5% at T+5) for Strong Entry signals.
- **Backtest Simulation**: Completed Phase 02. Built `src/backtest/simulator.py` to recreate historical scoring results day-by-day.
- **Simulation Data**: Generated `signals_log_full.csv` with daily signal logs for all VN100 tickers over the last 60 days.
- **Backtest Infrastructure**: Completed Phase 01. Created `data/historical` structure and `src/collectors/historical_sync.py`.
- **Historical Data**: Synchronized 60 days of price and flow data for 81 VN100 stocks.
- **Brain System**: Initialized `.brain/` for long-term project memory and session persistence.

### Changed
- **Scanner**: Switched to `Listing` and `Quote` classes from vnstock v3.4.x for better stability.
- **Main Flow**: Optimized the VN100 scanning process to handle all 100 symbols reliably.

### Fixed
- **Bugs**: Fixed `return_1m` attribute error and `UnicodeEncodeError` on Windows consoles.
- **Reporting**: Verified report generation for Feb 25, 2026.

## [2026-02-21]
### Added
- Daily report generated for Feb 21.
- Initial VN100 scanner implementation.
