# Kiểm chứng

## Tự động

Gate: `./scripts/verify.sh`.

- Account: đăng ký, username trùng, mật khẩu sai/yếu, session, logout POST, safe next.
- Journal: validation, owner, thêm/sửa entry, XSS escaping, mới nhất trước, thống kê.
- Truy cập trái phép: GET/POST qua ID của tài khoản khác và tài nguyên không tồn tại.
- CSRF: request ghi thiếu token bị từ chối.
- Launcher: cổng bị chiếm, đối số không hợp lệ, khóa/database được giữ nguyên.

Kết quả ngày **10/10/2026**, trên macOS, Python 3.14.7 / Django 6.1.2:

| Gate | Kết quả |
| --- | --- |
| pytest | **51 passed**, 0 failed |
| Coverage các module ứng dụng | **98.73%** (236 statements; 3 chưa đi qua) |
| Ruff check | All checks passed |
| Ruff format | 48 files already formatted |
| Django template format | 20 files checked; 0 files would be updated |
| Django system check | No issues (0 silenced) |
| Migration consistency | No changes detected |
| Chromium browser | **32 checks passed**, 0 JavaScript runtime errors |
| Restart | Dữ liệu và session giữ nguyên sau dừng/chạy lại |
| Fresh install | Bản sao chưa có `.venv`/database tự cài thư viện, migrate và trả HTTP 200 |

Browser kiểm tra desktop 1440×1000 và mobile 390×844. Chi tiết được lưu trong
`browser-results.json`; ảnh minh họa ở `screenshots/`. Coverage tính phần ứng dụng
`accounts`, `journal`, `common`, không tính migrations, config, admin và launcher.
Launcher có 8 bài kiểm thử riêng và được kiểm tra bằng chạy thật.

Hai regression đã được tái hiện bằng bài kiểm thử thất bại trước khi sửa:
thứ tự Topic khi annotate và kiểm tra cổng trong trạng thái TIME_WAIT sau restart.
Kiểm thử browser cũng xác minh sidebar ẩn trên mobile không nhận focus bàn phím.

Giới hạn xác minh: đã chạy thực tế trên máy macOS này và Chromium. Chưa chạy
trực tiếp trên Windows/Linux, Safari hoặc Firefox. Cần Internet khi cài thư viện
trên máy mới; máy bàn giao đã có môi trường cài sẵn.

## Browser acceptance có thể kiểm tra lại

1. Chạy `python3 run.py`; trang chủ, CSS, JS và SVG tải thành công.
2. Đăng ký tài khoản A; kiểm tra dashboard rỗng.
3. Tạo chủ đề Python, thêm ghi chép nhiều dòng; sửa và tải lại để kiểm tra đã lưu.
4. Tạo thêm chủ đề; kiểm tra tổng số chủ đề và ghi chép.
5. Mở viewport desktop và mobile; không có cuộn ngang; menu mobile mở/đóng được.
6. Đăng xuất, đăng ký B; không thấy chủ đề của A.
7. B truy cập đường dẫn chi tiết, thêm và sửa entry của A: nhận 404.
8. Dừng app rồi chạy lại; đăng nhập A và kiểm tra ghi chép vẫn còn.

Không có tài khoản mẫu trong database cá nhân. Browser tests dùng
`LEARNING_LOG_DATA_DIR` trỏ tới thư mục kiểm chứng bên ngoài project.

## Mở rộng ngày 26/10/2026

`./scripts/verify.sh`: 57 passed, coverage 98.91% (274 statements, 3 missing),
Ruff và format 50 Python files, 22 templates, Django check và migrations đều pass.
`tests/test_search_delete.py` xác minh tìm tên/nội dung, số đếm không nhân đôi,
owner isolation, xác nhận GET không xóa, POST xóa cascade, CSRF, anonymous và phương thức HTTP.
Chromium: tìm chủ đề qua nội dung ghi chép, empty search, bỏ lọc, hủy xóa, xóa entry/topic;
kiểm tra UI desktop và mobile 390x844 (không tràn ngang). Test data nằm ở thư mục tạm.
