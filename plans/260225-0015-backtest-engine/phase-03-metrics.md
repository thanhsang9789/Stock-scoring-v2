# Phase 03: Performance Metrics

## Objective
Tính toán các chỉ số hiệu quả dựa trên kết quả mô phỏng từ Phase 2.

## Requirements
### Functional
- [ ] Tính % thay đổi giá sau T+3, T+5, T+10, T+20 kể từ ngày có tín hiệu.
- [ ] Phân loại tỷ lệ thắng (Win Rate) theo từng mức điểm (ví dụ: >50, 30-50, <15).
- [ ] Tính chỉ số Max Drawdown (mức sụt giảm tài sản lớn nhất) nếu theo tín hiệu.

## Implementation Steps
1. [ ] Tạo module `src/backtest/analyzer.py`.
2. [ ] Viết hàm tính toán `calculate_forward_returns()`.
3. [ ] Tổng hợp thống kê Win/Loss ratio.

## Files to Create/Modify
- `src/backtest/analyzer.py` (New)

## Test Criteria
- [ ] Các con số thống kê chính xác, khớp với biến động giá thực tế trên biểu đồ.
