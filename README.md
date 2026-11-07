# StoreDesk

Đồ án Python/Django quản lý cửa hàng: sản phẩm, nhập hàng, bán hàng, tồn kho và báo cáo.
Dữ liệu lưu trong PostgreSQL, giao diện dùng Django templates.

## Chạy

Cài Python 3.12+ và PostgreSQL 15+ có `pg_config`, `initdb`, `pg_ctl`.
Trên Windows dùng Python Windows, PostgreSQL có thể cài trong `C:\Program Files\PostgreSQL`.

```powershell
python run.py
```

Mở http://127.0.0.1:8010/. Lần đầu tạo tài khoản quản lý, sau đó tạo nhân viên trong web.
Launcher tự tạo venv, cài thư viện và chạy migrations.
Ctrl+C dừng web; dữ liệu vẫn còn. Dừng PostgreSQL riêng bằng `python run.py --stop-db`.
Đổi cổng web: `python run.py --port 8020`.

## Chức năng

- Quản lý sản phẩm, nhà cung cấp và khách hàng.
- Phiếu nhập/đơn bán: nháp, xác nhận, hủy, hoàn.
- Xác nhận mới cập nhật tồn; nháp/hủy không thay đổi kho.
- Hoàn toàn bộ có lưu lý do, quản lý thực hiện.
- Giá vốn bình quân, sổ kho, điều chỉnh tồn.
- Dashboard doanh thu, lợi nhuận gộp, hàng bán chạy và tồn thấp.

| Vai trò | Quyền |
| --- | --- |
| Quản lý | Toàn bộ |
| Nhân viên kho | Nhập hàng, nhà cung cấp, tồn kho và sổ kho |
| Nhân viên bán hàng | Đơn bán và khách hàng |

Thanh toán ghi nhận thủ công bằng tiền mặt/chuyển khoản. Phạm vi một cửa hàng, một kho.

## Cấu trúc

- `src/accounts`: tài khoản và quyền.
- `src/catalog`: sản phẩm và đối tác.
- `src/trading`: phiếu nhập, đơn bán.
- `src/inventory`: tồn kho và lịch sử.
- `src/analytics`: báo cáo.
- `src/templates`, `src/static`: HTML, CSS, JS.
- `tests`: kiểm thử.
- `docs`: luồng chạy và ảnh desktop.

## Kiểm tra

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe manage.py check_business_data
```

macOS/Linux dùng `.venv/bin/python`. Tests dùng database riêng.

## Dữ liệu và sao lưu

Database local nằm ở `var/postgres`, cổng 55432. Không xóa `var` khi muốn giữ dữ liệu.
Sao lưu bằng `pg_dump`, không sao chép thư mục PostgreSQL khi đang chạy.
Không đưa venv, mật khẩu hoặc thư mục var lên Git.

Database local hiện có 7 sản phẩm, 3 nhà cung cấp, 5 khách hàng và 31 chứng từ minh họa.
Kỳ 23/10–07/11/2026: doanh thu thuần 12.530.000đ, lợi nhuận gộp 4.394.000đ.
Số liệu sẽ đổi khi thao tác trên web. Bộ seed tùy chọn chỉ dành cho database trống:
`manage.py seed_demo --username TEN_QUAN_LY`.

Khi nộp/chuyển máy, source không bao gồm dữ liệu PostgreSQL. Bản sao lưu đã kiểm tra
khôi phục nằm tại `var/backups/submission.dump`; gửi riêng nếu cần giữ số liệu minh họa.
Khôi phục vào database trống bằng `pg_restore`, rồi đặt `PGDATABASE` trỏ tới database đó.
Không gửi `.venv`, `.git` hoặc toàn bộ `var/postgres`; mật khẩu đăng nhập trao đổi riêng.

Xem [luồng hoạt động](docs/ARCHITECTURE.md) và [ảnh giao diện](docs/README.md).
