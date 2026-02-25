# Phase 01: Web Core Setup

## Objective
Tạo cấu trúc ứng dụng Streamlit cơ bản và tích hợp logic chấm điểm hiện có.

## Requirements
- [ ] Tạo file `app.py` làm entry point cho Web.
- [ ] Chuyển đổi các cấu hình từ `config.yaml` sang giao diện Sidebar của Streamlit (nếu cần).
- [ ] Tạo dashboard hiển thị thông tin tổng quan thị trường.

---
# Phase 02: Interactive Scanning

## Objective
Biến quy trình chạy lệnh CLI thành trải nghiệm "Bấm nút" trên Web.

## Requirements
- [ ] Nút bấm "🚀 Run Daily Scan".
- [ ] Hiển thị thanh tiến trình (Progress Bar) khi quét 100 mã VN100.
- [ ] Hiển thị kết quả dưới dạng bảng tương tác (DataTable) có màu sắc (Entry = Green, Trap = Red).
- [ ] Tích hợp tính năng xem lại kết quả Backtest trên Web.

---
# Phase 03: Authentication & Security

## Objective
Bảo vệ ứng dụng bằng mật khẩu đơn giản để chỉ anh mới có quyền bấm nút quét.

## Requirements
- [ ] Xây dựng màn hình Login đơn giản (nhập pass).
- [ ] Cấu hình `secrets.toml` để lưu mật khẩu an toàn.
- [ ] Ẩn thông tin nhạy cảm như API Key trên giao diện.

---
# Phase 04: Deployment Guide

## Objective
Đưa ứng dụng lên mạng (Global access).

## Requirements
- [ ] Tạo file `requirements.txt` đầy đủ các thư viện.
- [ ] Hướng dẫn đẩy code lên GitHub.
- [ ] Kết nối GitHub với Streamlit Cloud.
