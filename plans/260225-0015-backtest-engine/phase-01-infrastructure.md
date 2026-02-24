# Phase 01: Infrastructure & Data Sync

## Objective
Xây dựng cơ chế tải và lưu trữ dữ liệu lịch sử số lượng lớn (Price & Flow) cho danh sách VN100 để phục vụ backtest trong khoảng thời gian từ 3-6 tháng.

## Requirements
### Functional
- [ ] Mở rộng `VNStockCollector` để hỗ trợ tải dữ liệu theo khoảng ngày dài.
- [ ] Cơ chế caching dữ liệu vào thư mục `data/historical` để tránh tải lại nhiều lần (vượt hạn mức API).
- [ ] Xử lý gộp dữ liệu Giá (Quotes) và Dòng tiền (Flow) đồng bộ theo thời gian.

## Implementation Steps
1. [ ] Tạo thư mục `data/historical` để lưu cache.
2. [ ] Viết script `src/collectors/historical_sync.py` để tải dữ liệu VN100 trong 180 ngày.
3. [ ] Tích hợp cơ chế pacing (delay) để không bị khóa API khi tải số lượng lớn.

## Files to Create/Modify
- `src/collectors/historical_sync.py` (New)
- `data/historical/` (New Folder)

## Test Criteria
- [ ] Dữ liệu tải về đầy đủ các cột (Open, High, Low, Close, Volume, SM_Flow, Retail_Flow).
- [ ] Không bị lỗi Unicode khi lưu trữ tên file/thư mục.

---
Next Phase: [Simulation Engine](./phase-02-simulation.md)
