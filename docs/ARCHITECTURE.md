# Kiến trúc Learning Log

## Quyết định

Dùng **Django modular monolith** với `src/` layout và module theo chức năng.
FE và BE cùng một tiến trình, một origin; session authentication và CSRF do Django
quản lý. Giao diện render ở server bằng template, không cần build JavaScript.
Python 3.12+; máy kiểm chứng dùng Python 3.14.7 và Django 6.1.2.

Đây là kiến trúc phù hợp cho phạm vi Learning Log, không phải khẳng định có một
kiến trúc “mới nhất” áp dụng cho mọi ứng dụng Python.

## Trách nhiệm và hướng phụ thuộc

```text
Browser → URL → web view → form validation
                     ├→ selectors → Django ORM → SQLite (đọc)
                     └→ services → selectors + model validation → SQLite (ghi)
                 ↓
          template + local CSS/JS → HTML response
```

| Phần | Chịu trách nhiệm | Không chịu trách nhiệm |
| --- | --- | --- |
| `config/` | Ghép module, cấu hình framework và môi trường | Nghiệp vụ journal |
| `models.py` | Schema, quan hệ, field constraints và metadata | HTTP, template |
| `selectors.py` | Query đọc và giới hạn dữ liệu theo owner | Render hoặc sửa dữ liệu |
| `services.py` | Command ghi, kiểm tra quyền, validation, transaction | HTTP hoặc HTML |
| `forms.py` | Dữ liệu đầu vào, lỗi form, widget | Lưu database |
| `web/` / account views | Nhận request, gọi use case, trả response | Viết query trực tiếp |
| `templates/` | Nội dung, bố cục và component giao diện | Query hoặc nghiệp vụ |
| `static/css/` | Token chung, layout, các trang journal | Dữ liệu |
| `static/js/` | Menu mobile và đếm ký tự | Lưu ghi chép hoặc xác thực |
| `scripts/` | Chuẩn bị môi trường và vòng đời server local | Nghiệp vụ app |

Accounts tái sử dụng model User và bộ xác thực Django. View chỉ gọi service để tạo
user và gọi Django login để tạo session; không tự hash mật khẩu hay xây hệ thống auth.
Các module sử dụng trực tiếp ORM thay vì thêm repository wrapper trùng với Django.

## Dữ liệu

- `User 1 → N Topic`: topic có `owner`, tên tối đa 200 ký tự, ngày tạo.
- `Topic 1 → N Entry`: entry có nội dung, ngày tạo, thời điểm cập nhật.
- Entry kế thừa quyền sở hữu qua Topic; không lưu owner hai lần.
- Index `(owner, date_added)` và `(topic, date_added)` phục vụ truy vấn danh sách.
- Dashboard annotate số entry theo Topic, tránh một query đếm riêng cho mỗi card.
- SQLite lưu trong `var/`, không đặt trong mã nguồn. Migrations được lưu trong project.

## Quyền và validation

Mọi trang dữ liệu cá nhân yêu cầu đăng nhập. Selectors tìm bằng **ID + owner**;
không tìm ID trước rồi bỏ qua quyền. Không tồn tại và không thuộc tài khoản đều
trở thành `JournalNotFound`, được web adapter đổi thành HTTP 404.

Service thêm entry kiểm tra owner của topic; service sửa entry kiểm tra owner qua
topic. Quy tắc vẫn áp dụng khi gọi service trực tiếp, không chỉ qua UI. Form xử lý
dữ liệu không hợp lệ; service gọi `full_clean()` trước khi ghi. Nội dung người dùng
được template tự escape. Các POST có CSRF; đăng xuất chỉ nhận POST. Trang chi tiết
chỉ nhận GET, vì vậy POST tới endpoint đó nhận 405.

## Chạy local

Launcher: kiểm tra cổng → chuẩn bị `.venv` → tạo dữ liệu/khóa nếu chưa có → migrate
→ system check → server `127.0.0.1` → mở browser sau khi server sẵn sàng.
Tắt server không reset dữ liệu. Cổng có thể đổi qua `--port`.

`config/settings/base.py` chứa cấu hình chung; `local.py` dùng SQLite và loopback;
`test.py` dùng khóa/hasher dành riêng cho kiểm thử. Biến `LEARNING_LOG_DATA_DIR`
cho phép chạy browser acceptance trên database riêng mà không làm bẩn dữ liệu thật.

## Phạm vi mở rộng

Thêm chức năng journal trong cùng module, viết test trước rồi nối form/view/template.
Chỉ tách backend API hoặc frontend riêng khi có yêu cầu cụ thể. Tìm kiếm dùng selectors với điều kiện owner; xóa dùng services có transaction và
kiểm tra owner. GET hiển thị xác nhận; POST có CSRF thực hiện xóa. Hiện chưa có
public topics hoặc upload.
