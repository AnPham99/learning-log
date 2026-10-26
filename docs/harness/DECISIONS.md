# Decisions

- 2026-10-10: Chạy local theo yêu cầu, thay thế hướng deploy trước đó.
- Django 6.1.2 + Python 3.12+; templates và tài nguyên static local cho FE hoàn chỉnh.
- Module theo chức năng; selectors đọc, services ghi, forms validation, views HTTP.
- SQLite persistent; launcher không reset dữ liệu, khóa session được giữ qua restart.
- Đưa kiểm tra quyền ở bài tập 19-4 vào scope để không thêm entry vào topic của người khác.
- Kiểm thử browser dùng database riêng; không seed dữ liệu vào database cá nhân.
- Không auto-commit. Các thay đổi truy vết đến docs/SPEC.md và yêu cầu chat.

- 26/10/2026: Tìm kiếm dùng subquery entry để không nhân bản topic hoặc làm sai Count.
  Xóa có trang xác nhận chung, GET chỉ đọc, POST qua service kiểm tra owner và atomic.
  Giữ giao diện SSR, không thêm dependency. User cho phép repo public và push mã nguồn.
