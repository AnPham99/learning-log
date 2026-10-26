# Learning Log

Nhật ký học tập cá nhân bằng Python/Django, đầy đủ giao diện tiếng Việt và backend.
Chạy trên máy, lưu bằng SQLite. Không cần Node.js, Docker, tài khoản cloud hoặc CDN.

## Chạy ngay

Cần Python 3.12+ và Internet ở lần cài thư viện đầu tiên. Trong thư mục project, chạy:

```sh
python3 run.py
```

Hoặc mở `start.command` trên macOS. Script tự kiểm tra thư viện, áp dụng migrations,
khởi chạy tại **http://127.0.0.1:8000/** và mở trình duyệt. Nhấn **Ctrl+C** để dừng.
Tự đăng ký tài khoản trên giao diện; không có tài khoản mặc định hay dữ liệu mẫu.

Nếu chuyển project sang máy khác: cần Python **3.12+**, chạy `python3 run.py`
trong thư mục project. Lần cài thư viện đầu tiên cần Internet; các lần chạy sau
hoạt động offline. Trên Windows có thể dùng `py run.py`.

```sh
python3 run.py --port 8001       # Khi cổng 8000 đang được sử dụng
python3 run.py --no-browser     # Chạy mà không tự mở trình duyệt
```

## Các chức năng

- Đăng ký, đăng nhập và đăng xuất.
- Tạo chủ đề riêng tư, xem danh sách và tổng số ghi chép.
- Tìm theo tên chủ đề hoặc nội dung ghi chép; lọc ghi chép trong từng chủ đề.
- Xóa ghi chép hoặc chủ đề sau xác nhận. Xóa chủ đề sẽ xóa toàn bộ ghi chép bên trong.
- Thêm và sửa ghi chép; hiển thị ngày tạo, ghi chép mới nhất trước.
- Chặn truy cập dữ liệu của tài khoản khác, kể cả tự sửa ID trên URL.
- Form có validation, trạng thái rỗng, thông báo lưu thành công, trang 404/500.
- Giao diện responsive, dùng được với bàn phím, CSS/JS/icon lưu trong project.

## Cấu trúc

```text
learning-log/
├── run.py                      # Điều phối khởi chạy local
├── start.command               # Shortcut macOS
├── manage.py                   # Lệnh quản trị Django
├── pyproject.toml              # Metadata, pytest, coverage, Ruff
├── requirements*.txt           # Phiên bản thư viện được cố định
├── scripts/
│   ├── bootstrap.py            # Môi trường Python, dữ liệu, khóa local
│   ├── server.py               # Cổng, server, mở trình duyệt, tắt server
│   └── verify.sh               # Cổng kiểm chứng tự động
├── src/
│   ├── config/                 # Cấu hình, URL root, WSGI
│   ├── common/                 # Trang chủ, trang lỗi, cách hiển thị form
│   ├── accounts/               # Form, service và HTTP cho tài khoản
│   ├── journal/
│   │   ├── models.py           # Cấu trúc dữ liệu và ràng buộc
│   │   ├── selectors.py        # Truy vấn đọc, luôn giới hạn chủ sở hữu
│   │   ├── services.py         # Nghiệp vụ ghi, validation, transaction
│   │   ├── forms.py            # Validation đầu vào từ người dùng
│   │   ├── exceptions.py       # Lỗi nghiệp vụ không gắn với HTTP
│   │   ├── web/                # Adapter HTTP riêng cho chủ đề/ghi chép
│   │   └── migrations/         # Lịch sử schema
│   ├── templates/              # Trang và component giao diện tái sử dụng
│   └── static/                 # CSS theo trách nhiệm, JS, SVG
├── tests/                      # Kiểm thử tài khoản, journal, launcher
├── docs/                       # Đặc tả, kiến trúc, kế hoạch, bằng chứng
└── var/                        # Database và khóa local, không đưa vào Git
```

Đọc [kiến trúc và luồng dữ liệu](docs/ARCHITECTURE.md),
[phạm vi theo đề bài](docs/SPEC.md) và [kết quả kiểm chứng](docs/VERIFICATION.md).

## Dữ liệu local

Database ở `var/learning_log.sqlite3`. Khóa phiên đăng nhập ở `var/.secret-key`,
được tạo riêng cho máy và giữ lại qua các lần chạy. Script không xóa/reset dữ liệu.
Khi sao lưu, dừng ứng dụng rồi sao chép cả `var/`; không ghi đè database khi cập nhật code.
Thư mục này và `.venv/` được bỏ qua bởi `.gitignore`.

## Phát triển và kiểm thử

```sh
.venv/bin/python -m pip install -r requirements-dev.txt
./scripts/verify.sh
```

Gate bao gồm pytest + coverage tối thiểu 80%, Ruff, Django system check và kiểm tra
migrations đã đồng bộ. Kiểm thử dùng database riêng, không sửa database cá nhân.

Local dùng `DEBUG=False` để hiển thị trang lỗi thân thiện; launcher dùng
`runserver --insecure` để phục vụ static files trên loopback. Đây là cấu hình chạy
local theo yêu cầu, không phải cấu hình hosting. Không dùng `manage.py runserver`
thay cho launcher nếu chưa cấu hình static và khóa phiên tương ứng.

Có thể tạo tài khoản quản trị tùy chọn bằng `.venv/bin/python manage.py createsuperuser`
và mở `/admin/`. Giao diện chính không yêu cầu tài khoản quản trị.
