# Phase 02: Simulation Engine

## Objective
Tái hiện lại quy trình chấm điểm Stock Score V2 cho từng ngày trong quá khứ một cách tự động.

## Requirements
### Functional
- [ ] Tạo vòng lặp thời gian (Backtest Window).
- [ ] Áp dụng logic từ `src/scoring` và `src/signals` cho dữ liệu tại từng thời điểm T trong quá khứ.
- [ ] Đảm bảo không bị "Look-ahead bias" (không dùng dữ liệu tương lai để chấm điểm cho quá khứ).

## Implementation Steps
1. [ ] Tạo class `BacktestSimulator` trong `src/backtest/simulator.py`.
2. [ ] Map dữ liệu từ cache vào các Component chấm điểm hiện có.
3. [ ] Lưu kết quả chấm điểm hàng ngày vào một DataFrame tổng hợp.

## Files to Create/Modify
- `src/backtest/simulator.py` (New)
- `src/backtest/__init__.py` (New)

## Test Criteria
- [ ] Điểm số tính toán tại ngày T trong backtest phải giống hệt điểm số tính toán thực tế nếu chạy app tại ngày T đó.

---
Next Phase: [Performance Metrics](./phase-03-metrics.md)
