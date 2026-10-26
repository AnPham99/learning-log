# Progress

Completed: learning-log-local, theo docs/SPEC.md.

- FE/BE hoàn chỉnh: tài khoản, chủ đề riêng tư, thêm/sửa ghi chép, responsive UI.
- TDD: HTTP tests RED (34 failed), sau triển khai GREEN; bổ sung launcher tests.
- Regression: annotation ordering và restart port TIME_WAIT, đều RED → GREEN.
- `./scripts/verify.sh`: 51 tests passed; application coverage 98.73%; Ruff,
  template format, Django checks và migrations đều pass.
- Chromium: 32 browser checks pass, không lỗi JavaScript, desktop/mobile không tràn ngang.
- Restart test giữ nguyên database và session. Fresh copy tự bootstrap thành công.
- Browser/fresh-install tests dùng database riêng trong work/, không seed dữ liệu cá nhân.
- Tài liệu: README.md, ARCHITECTURE.md, VERIFICATION.md, browser-results.json.
- Không auto-commit hoặc deploy. Chỉ tạo project trong outputs/learning-log.

Handoff: chạy `python3 run.py` hoặc `start.command`; đăng ký tài khoản mới trên UI.
Nếu mở rộng sau này, chốt phạm vi trong SPEC.md trước, viết test và cập nhật harness.

## Kiểm tra lại 12/10/2026

- Người dùng báo ảnh đăng nhập tại 8001 có phần xám bên phải.
- Khi kiểm tra, 8001 không có listener; 8000 do Node/Express sử dụng và trả 404.
- Khởi chạy lại bằng `python3 run.py --port 8001 --no-browser`; migrations đồng bộ,
  Django check không có lỗi. Server Learning Log đang chạy tại 127.0.0.1:8001.
- Chạy lại `./scripts/verify.sh`: 51 passed, coverage 98.73%, toàn bộ gate pass.
- Chromium login: viewport/body/document đều rộng 2556 px, nền rgb(248,247,243).
  Phần xám trong ảnh chưa tái hiện được; chưa xác nhận nguyên nhân ảnh cũ.
- Không thay đổi mã ứng dụng hoặc dữ liệu cá nhân trong lần kiểm tra này.

## Mở rộng 26/10/2026

- Scope theo yêu cầu: tìm kiếm, xóa và xuất bản source vào repo public AnPham99/learning-log.
- Đã thêm tìm chủ đề theo tên/nội dung entry và lọc entry trong chủ đề, query GET có bỏ lọc.
- Đã thêm xác nhận xóa entry/topic; POST + CSRF + kiểm tra owner ở service. Topic xóa cascade.
- Sáu bài kiểm thử mới RED trước triển khai, GREEN sau triển khai. Toàn bộ 57 tests pass,
  coverage 98.91%; format/lint/Django/migrations pass.
- Chromium desktop/mobile: search, không có kết quả, bỏ lọc, hủy, xóa entry/topic pass.
  Mobile 390px không tràn ngang; kiểm tra hình sau khi sidebar hoàn tất chuyển trạng thái.
- Test browser dùng database tạm riêng. Không xóa dữ liệu của người dùng.
- Đã mở rộng gitignore, kiểm tra database/secret/env/venv bị loại khỏi Git.
- Đã commit 0335f12 và push main; GitHub API xác nhận repo PUBLIC:
  https://github.com/AnPham99/learning-log.
- Đã dừng server kiểm chứng và khởi động lại app cá nhân ở cổng 8001 để tải code mới.
- Không còn công việc trong phạm vi tính năng này; người dùng có thể refresh để dùng.
