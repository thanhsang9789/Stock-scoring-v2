# 🎨 DESIGN: Stock Score Backtest Engine

Ngày tạo: 2026-02-25
Dựa trên: [plans/260225-0015-backtest-engine/plan.md](../plans/260225-0015-backtest-engine/plan.md)

---

## 1. Cách Lưu Thông Tin (Data Architecture)

Hệ thống sử dụng cơ chế **File-based Caching** để tối ưu hóa hiệu năng và tránh lãng phí API calls.

### Sơ đồ thư mục dữ liệu:
- `data/historical/prices/`: Lưu file CSV giá `.history()` của vnstock (Date, OHLCV).
- `data/historical/flows/`: Lưu file CSV dòng tiền `.financial_flow()` (Date, NN, TD, TC, CN).
- `data/historical/results/`: Lưu kết quả chạy Backtest theo từng cấu hình.

### Quy tắc lưu trữ:
- Tên file: `{TICKER}_price.csv` và `{TICKER}_flow.csv`.
- Format ngày: `YYYY-MM-DD`.
- Encoding: `utf-8-sig` (để đọc tốt trên Excel Windows).

---

## 2. Các Module Chính (System Components)

| Module | Chức năng | Input | Output |
|---|---|---|---|
| **HistoricalSync** | Tải và đồng bộ hóa dữ liệu từ vnstock | Ticker List, Date Range | CSV files in `data/` |
| **BacktestSimulator** | Chạy vòng lặp thời gian & tính điểm | Cached CSVs, Scorer Modules | `signals_log.csv` |
| **PerformanceAnalyzer** | Tính toán lợi nhuận T+ | `signals_log.csv`, Price Data | `performance_metrics.json` |
| **ReportGenerator** | Xuất báo cáo trực quan | Metrics & Logs | `backtest_report.html` |

---

## 3. Luồng Hoạt Động (User Journey)

### Hành trình: Thực hiện Backtest cho chiến thuật hiện tại
1. **Config**: Người dùng định nghĩa `start_date`, `end_date`, `tickers` (mặc định VN100).
2. **Sync**: Hệ thống kiểm tra cache, tải phần dữ liệu còn thiếu từ vnstock.
3. **Run**: Hệ thống giả lập từng ngày giao dịch (ví dụ chạy 60 ngày):
   - Ngày 1: Lấy dữ liệu 20 ngày trước đó -> Tính điểm -> Lưu kết quả.
   - Ngày 2: Lấy dữ liệu 20 ngày trước đó -> Tính điểm -> Lưu kết quả.
4. **Eval**: Hệ thống "liếc" sang dữ liệu của 5, 10 ngày sau để tính % lãi lỗ.
5. **View**: Người dùng mở báo cáo để xem tỷ lệ thắng (Win Rate).

---

## 4. Checklist Kiểm Tra (Acceptance Criteria)

### Tính năng: Backtest Simulation
- [ ] Điểm số tính trong backtest phải giống 100% điểm tính thực tế tại cùng thời điểm.
- [ ] Không có hiện tượng "Look-ahead bias" (không dùng giá Close ngày T+1 để chấm điểm cho ngày T).
- [ ] Xử lý đúng các ngày nghỉ lễ/cuối tuần khi tính lợi nhuận T+.
- [ ] Tích hợp cơ chế pacing (1.1s - 2.5s) để bảo vệ API key.

### Chỉ số Performance:
- [ ] Win/Loss Ratio tính theo số lệnh có lãi (>0%).
- [ ] Profit Factor (Tổng lãi / Tổng lỗ).
- [ ] Average Return per Trade.

---

*Tạo bởi AWF 2.1 - Design Phase*
