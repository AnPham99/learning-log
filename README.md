# StoreDesk

Nội dung hiện tại của repo `AnPham99/learning-log` là **StoreDesk** — ứng dụng kho/bán hàng.
Mã Learning Log trước đây vẫn có trong lịch sử Git.

Ứng dụng Django quản lý một cửa hàng, một kho và bán hàng nội bộ.
Giao diện tiếng Việt đơn giản: menu, bảng, form và dashboard. Database PostgreSQL,
SSR bằng Django templates; không cần Node.js hoặc CDN để sử dụng.

## Tài liệu để đọc và trình bày

- [Kiến trúc và sơ đồ dữ liệu](docs/ARCHITECTURE.md): module, trách nhiệm từng lớp,
  ERD, sequence nhập/bán và luồng dashboard.
- [Kịch bản trình bày với giảng viên](docs/PRESENTATION.md): demo 8–10 phút,
  file cần mở và câu hỏi thường gặp.
- [Kiểm chứng](docs/VERIFICATION.md) và [đối chiếu dữ liệu demo](docs/data-check.json).

Đọc docstring ngay đầu các module chính để biết file đó chịu trách nhiệm gì.

## Chạy local

```sh
git clone https://github.com/AnPham99/learning-log.git
cd learning-log
python3 run.py
```

Nếu đã có source, mở Terminal trong thư mục project và chạy `python3 run.py`.

Mở **http://127.0.0.1:8010/**. Lần đầu tạo tài khoản quản lý trên trang thiết lập;
không có tài khoản/mật khẩu mặc định. Sau khi tạo quản lý, trang thiết lập đóng.

Launcher tự chuẩn bị `.venv`, cài thư viện nếu thiếu, khởi động PostgreSQL riêng,
áp dụng migrations và mở trình duyệt. Có thể mở `start.command` trên macOS.

```sh
python3 run.py --no-browser       # Không tự mở browser
python3 run.py --port 8020        # Đổi cổng web nếu bị chiếm
python3 run.py --prepare-only     # Chỉ chuẩn bị môi trường, DB và migrations
python3 run.py --stop-db          # Dừng PostgreSQL riêng sau khi đã dừng web
```

Ctrl+C dừng web. Database tiếp tục chạy và giữ dữ liệu; dùng `--stop-db` khi muốn
đóng hẳn. PostgreSQL tại cổng **55432**, cluster trong `var/postgres`; không dùng
hoặc chỉnh sửa PostgreSQL đang có ở cổng 5432. Web chỉ lắng nghe loopback.

## Khi chuyển sang máy khác

Cần **Python 3.12+**, **PostgreSQL 15+** với `pg_config`, `initdb`, `pg_ctl` có trong PATH,
và Internet ở lần cài thư viện đầu tiên. Đã kiểm chứng trên macOS ARM64,
Python 3.14.7, PostgreSQL 15.17, Django 6.1.2; chưa kiểm chứng Windows/Linux.

Ví dụ macOS nếu chưa có PostgreSQL: `brew install postgresql@15`, thêm thư mục
bin của bản PostgreSQL này vào PATH rồi chạy `python3 run.py`. Không cần bật
Homebrew PostgreSQL service vì launcher quản lý cluster riêng.

Có thể dùng PostgreSQL đã chuẩn bị bên ngoài bằng các biến `PGHOST`, `PGPORT`,
`PGDATABASE`, `PGUSER`, `PGPASSWORD`. Khi có `PGHOST`, launcher không quản lý
cluster, tạo hoặc dừng database ngoài; database và quyền truy cập phải có sẵn.
Không ghi mật khẩu vào source. Để chạy tests, role cần quyền tạo database test.

## Sử dụng

1. Tạo tài khoản quản lý đầu tiên.
2. **Sản phẩm → Thêm sản phẩm**: SKU duy nhất, tên, danh mục, đơn vị, giá bán,
   ngưỡng tồn thấp. Bỏ chọn “Đang kinh doanh” để ngừng bán, vẫn giữ lịch sử.
3. **Nhà cung cấp**: thêm nhà cung cấp cho phiếu nhập.
4. **Nhập hàng → Tạo phiếu nhập**: chọn nhà cung cấp, các sản phẩm, số lượng,
   giá nhập. “Thêm dòng” để thêm mặt hàng; dấu “×” ở cuối dòng để xóa trực tiếp, có “Hoàn tác xóa dòng” nếu nhầm. Lưu nháp,
   kiểm tra rồi **Xác nhận nhập kho**. Nháp chưa tăng tồn.
5. **Khách hàng**: thêm khách hàng nếu cần; đơn bán có thể chọn khách lẻ.
6. **Bán hàng → Tạo đơn bán**: chọn sản phẩm, số lượng, giảm giá toàn đơn,
   tiền mặt/chuyển khoản. Giá bán lấy từ danh mục lúc lưu nháp. Kiểm tra rồi
   **Xác nhận bán & đã thu tiền**. Hệ thống trừ tồn và ghi nhận thanh toán đầy đủ.
7. **Tồn kho / Sổ kho**: xem số lượng, giá vốn bình quân và biến động. Quản lý
   có thể điều chỉnh tăng/giảm tồn kèm lý do; tăng tồn cần nhập giá vốn.
8. **Hoàn đơn**: quản lý mở chứng từ đã xác nhận, chọn hoàn toàn bộ và nhập lý do.
   Hoàn đơn bán phục hồi hàng và ghi nhận hoàn tiền. Không xóa lịch sử chứng từ.
9. **Nhân viên**: quản lý tạo tài khoản kho hoặc bán hàng với mật khẩu riêng.
10. **Tổng quan**: lọc ngày, xem doanh số/lợi nhuận, hàng bán chạy và cảnh báo tồn.
    Dashboard tự lấy dữ liệu mới mỗi 10 giây khi tab đang mở; lỗi mạng giữ số liệu
    cũ và báo chưa cập nhật. Có bảng dữ liệu thay thế cho biểu đồ.

Các danh sách chính có tìm kiếm và phân trang 20 dòng. Kho có bộ lọc tồn thấp;
chứng từ có bộ lọc trạng thái.

## Quyền

| Vai trò | Quyền |
| --- | --- |
| Quản lý | Toàn bộ nghiệp vụ, dashboard, điều chỉnh kho, hoàn chứng từ, tạo nhân viên |
| Nhân viên kho | Xem sản phẩm, quản lý nhà cung cấp, nhập hàng, xem tồn và sổ kho |
| Nhân viên bán hàng | Xem sản phẩm, quản lý khách hàng, tạo/xác nhận đơn bán |

Nhân viên có thể hủy phiếu nháp thuộc loại chứng từ được phép thao tác.
Chỉ quản lý được hoàn chứng từ đã xác nhận. Kiểm tra quyền được thực hiện ở
cả HTTP và service, không chỉ ẩn nút trên giao diện.

## Quy tắc nghiệp vụ

- Số lượng nguyên, tiền VND. Đơn bán chỉ hỗ trợ thanh toán đầy đủ được nhân viên
  ghi nhận thủ công; không tích hợp cổng thanh toán hoặc công nợ.
- Xác nhận khóa dòng tồn kho trong transaction: không bán âm tồn khi có nhiều
  người thao tác. Xác nhận/lưu nháp lặp cùng token không tạo tác động lần hai.
- Giá bán và tên sản phẩm được lưu trên dòng nháp; giá vốn lưu khi xác nhận.
  Đổi giá sản phẩm không làm thay đổi chứng từ cũ.
- Giá vốn bình quân gia quyền được tính từ tổng giá trị tồn/số lượng tồn.
  Giá trị vốn nội bộ giữ 4 chữ số thập phân; giao diện làm tròn đến đồng.
- Hoàn bán là toàn bộ đơn và toàn bộ tiền đã thu, không hoàn một phần.
- Hoàn phiếu nhập chỉ được phép khi mỗi sản phẩm chưa có biến động tiếp theo;
  nếu đã bán/điều chỉnh/nhập tiếp thì bị chặn để giữ đúng tồn và giá vốn.
- Doanh số thuần = giá trị đơn xác nhận trong kỳ − giá trị hoàn trả trong kỳ.
  Hoàn trả tính theo ngày hoàn; ngày bán cũ vẫn giữ doanh số lịch sử.
- Lợi nhuận gộp = doanh số thuần − giá vốn ròng tương ứng; chưa trừ chi phí vận hành.
- Bộ lọc ngày áp dụng cho giao dịch, biểu đồ và bán chạy. Tồn kho luôn là **hiện tại**,
  không phải tồn tại cuối khoảng ngày đã chọn. Ngày theo giờ Việt Nam, tối đa 366 ngày.

Phạm vi hiện tại không gồm VAT/hóa đơn điện tử, vận chuyển, biến thể size/màu,
lô/hạn dùng/serial, nhiều kho, bán online hoặc báo cáo kế toán pháp lý.

## Dữ liệu minh họa (tùy chọn)

Sau khi tạo quản lý, nếu cửa hàng chưa có sản phẩm/giao dịch:

```sh
.venv/bin/python manage.py seed_demo --username TEN_DANG_NHAP_QUAN_LY
```

Lệnh tạo 8 sản phẩm, 1 phiếu nhập, 28 đơn bán trong 14 ngày gần nhất và một số
điều chỉnh kho minh họa. Lệnh không tạo tài khoản hoặc mật khẩu và từ chối chạy
trên cửa hàng đã có sản phẩm/giao dịch. Ảnh trong `docs/screenshots` lấy từ DB thử.

## Sao lưu

File runtime nằm trong `var/`, gồm cluster PostgreSQL và khóa local. Không đưa
thư mục này lên Git. Không sao chép thô thư mục PostgreSQL trong lúc DB đang chạy.

Đối với cluster mặc định, chạy từ thư mục project để sao lưu bằng PostgreSQL:

```sh
mkdir -p var/backups
pg_dump -h "$PWD/var/socket" -p 55432 -U storedesk -d storedesk -Fc -f var/backups/storedesk.dump
```

Giữ file backup ở nơi riêng tư. Khi khôi phục, tạo database **trống mới** bằng
`createdb` rồi dùng `pg_restore -h "$PWD/var/socket" -p 55432 -U storedesk -d TEN_DB_MOI var/backups/storedesk.dump`.
Dùng `PGDATABASE=TEN_DB_MOI python3 run.py` để kiểm tra bản khôi phục.
Khóa `.secret-key` nên giữ lại khi sao lưu/cập nhật để bảo toàn session.

## Cấu trúc

```text
storedesk/
├── run.py, start.command        Khởi chạy local
├── manage.py                   Django CLI
├── scripts/                    Bootstrap, PostgreSQL, verify
├── src/
│   ├── config/                 Settings, routes, WSGI
│   ├── common/                 Form style, pagination, domain errors
│   ├── accounts/               Setup, đăng nhập, vai trò, nhân viên
│   ├── catalog/                Sản phẩm, khách hàng, nhà cung cấp
│   ├── inventory/              Tồn kho, điều chỉnh, sổ kho
│   ├── trading/                Phiếu nhập/đơn bán, xác nhận, hoàn
│   ├── analytics/              Chỉ số, bộ lọc ngày, JSON dashboard
│   ├── templates/              Trang SSR và component HTML chung
│   └── static/                 CSS/JS lưu local
├── tests/                      Nghiệp vụ, HTTP, concurrency PostgreSQL
├── docs/                       Phạm vi, kiến trúc, kiểm chứng
└── var/                        Runtime, không đưa vào Git
```

Trong từng nghiệp vụ: `models` giữ schema, `forms` kiểm tra input, `services`
điều phối ghi có quyền/transaction, `selectors` truy vấn báo cáo, `views` xử lý HTTP.

## Kiểm thử

```sh
python3 run.py --prepare-only
.venv/bin/python -m pip install -r requirements-dev.txt
./scripts/verify.sh
```

Có thể đối chiếu dữ liệu đang có mà không sửa database:

```sh
.venv/bin/python manage.py check_business_data
```

Lệnh kiểm tra số dư, lịch sử kho, tổng tiền/giá vốn và tác động kho theo trạng thái
chứng từ. `ok: true` nghĩa là các đối chiếu được kiểm tra đều khớp tại thời điểm chạy.

Tests tạo database PostgreSQL riêng (`test_storedesk` theo cấu hình mặc định),
không ghi vào database cửa hàng. Có kiểm thử multithread bán đồng thời, xác nhận
lặp, rollback, giá vốn, hoàn hàng, phân quyền, CSRF và bộ lọc dashboard.

Xem `docs/SCOPE.md`, `docs/ARCHITECTURE.md`, `docs/VERIFICATION.md`.
