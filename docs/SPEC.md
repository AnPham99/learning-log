# Learning Log — phạm vi đã được phép triển khai

Nguồn: Python Crash Course, Project 3, chương 18–20 (trang 379–463),
và yêu cầu trong chat ngày 10/10/2026: FE + BE hoàn chỉnh, chỉ chạy local,
cấu trúc hiện đại, rõ trách nhiệm, chạy bằng một lệnh.

| ID | Hành vi | Xác minh |
| --- | --- | --- |
| LL-01 | Trang giới thiệu, đăng ký, đăng nhập, đăng xuất POST | tests/test_accounts.py |
| LL-02 | Chủ đề riêng tư của từng tài khoản; tạo, liệt kê, xem | tests/test_journal_web.py |
| LL-03 | Thêm/sửa ghi chép; nội dung và ngày tạo được lưu | tests/test_journal_web.py |
| LL-04 | Chặn đọc/ghi qua ID của tài khoản khác, gồm bài tập 19-4 | tests/test_journal_web.py |
| LL-05 | Hiển thị lỗi form, trạng thái rỗng, 404, responsive | HTTP tests + browser desktop/mobile |
| LL-06 | Một lệnh chạy FE + BE, SQLite bền vững trên máy | launcher tests + restart browser check |
| LL-07 | Tách query, command, HTTP, validation, template, static | docs/ARCHITECTURE.md + source review |

Không nằm trong phạm vi: deploy cloud, chia sẻ công khai, đổi tên chủ đề, upload, React/API riêng, khôi phục mật khẩu.

Một tài khoản mới không có dữ liệu mẫu. Người dùng tự đăng ký và ghi chép.
Thư viện, CSS và JavaScript chạy trên máy; sau khi cài thư viện không cần CDN.

## Mở rộng được yêu cầu ngày 26/10/2026

- LL-08: Tìm chủ đề theo tên hoặc nội dung ghi chép; tìm nội dung trong một chủ đề.
  Query GET `q`, giữ từ khóa, có bỏ lọc và trạng thái không có kết quả. Chỉ tìm dữ liệu của mình.
- LL-09: Xóa ghi chép và xóa chủ đề (kèm ghi chép), GET chỉ xác nhận, POST có CSRF
  mới xóa; kiểm tra owner ở service và web; thông báo kết quả, có nút hủy.
- LL-10: Bổ sung gitignore, tạo repo public AnPham99/learning-log, commit và push source.
  Không công bố database, khóa local, môi trường Python hay file runtime cá nhân.

Xác minh: tests/test_search_delete.py, scripts/verify.sh, browser và GitHub API.
