# Kiểm chứng StoreDesk — cập nhật 03/11/2026

Nguồn yêu cầu: docs/SCOPE.md và yêu cầu kiểm tra lại dữ liệu demo, bổ sung mô tả
kiến trúc để trình bày với giảng viên. Bản hiện tại chạy local tại 8010.

## 1. Bộ kiểm chứng tự động mới nhất

`./scripts/verify.sh` chạy trên macOS ARM64, Python 3.14.7, Django 6.1.2,
psycopg 3.3.6 và PostgreSQL 15.17 thật, dùng database test riêng.

| Kiểm tra | Kết quả | Bằng chứng |
| --- | --- | --- |
| Pytest | **60 passed**, 0 failed | `verification.txt` |
| Coverage phần ứng dụng | **90.77%**, 791 statements, 73 chưa đi qua | Cùng log |
| Ruff check / format | Pass; 75 files đã định dạng | Cùng log |
| Django system check | Không có lỗi | Cùng log |
| Migrations | Không có thay đổi chưa tạo | Cùng log |

Nhóm rủi ro đã kiểm thử:

- Hai đơn cùng mua lượng hàng cuối: chỉ một đơn xác nhận, tồn không âm.
- Hai request xác nhận cùng phiếu: chỉ một lần ghi tồn/ledger.
- Hai request cùng token lưu draft: chỉ một chứng từ.
- Phiếu nhiều dòng: một dòng thiếu tồn làm rollback toàn bộ phiếu.
- Nháp không đổi tồn; snapshot giá bán, bình quân giá vốn và hoàn toàn bộ.
- Chặn hoàn nhập sau biến động tiếp theo; giữ người xác nhận/hủy/hoàn.
- Quyền ở service/HTTP, anonymous, CSRF, XSS escaping và form validation.
- Dashboard phân biệt ngày bán/ngày hoàn, bỏ qua nháp, kiểm tra kỳ báo cáo.
- Regression: giá trị ẩn mặc định của form phiếu nhập.
- 3 tests mới ở `test_seed_and_audit.py`: seed đủ module; chạy lại bị từ chối;
  đối chiếu dữ liệu đúng và phát hiện số dư/tổng tiền bị làm sai trong database test.

Coverage không phải bằng chứng mọi tình huống đã được kiểm tra. Log chỉ tính các
module ứng dụng, loại migrations và management commands theo pyproject.toml.

## 2. Dữ liệu demo hiện tại

Báo cáo chỉ đọc: `data-check.json`, tạo bằng:

```sh
.venv/bin/python manage.py check_business_data
```

| Dữ liệu | Số lượng |
| --- | --- |
| Tài khoản | 3: quản lý, kho, bán hàng |
| Sản phẩm | 8 |
| Nhà cung cấp / khách hàng | 1 / 3 |
| Chứng từ | 32 |
| Trạng thái | 2 nháp, 28 xác nhận, 1 hủy, 1 hoàn |
| Biến động kho | 69 |
| Lỗi đối chiếu | **0**, `ok: true` |

Dữ liệu bán được seed cho 21/10/2026–03/11/2026, có tiền mặt/chuyển khoản, giảm
giá, hoàn tiền và 3 sản phẩm tồn thấp. Dữ liệu phủ mọi module chính trong phạm vi
đã chốt; không bao gồm các nghiệp vụ ngoài phạm vi như VAT, công nợ hoặc nhiều kho.

Lệnh audit đối chiếu số dư/giá trị tồn với tổng Movement, balance sau từng biến động,
tổng tiền/giá vốn chứng từ và tác động kho theo trạng thái. Lệnh không tự sửa dữ liệu
và không khẳng định phát hiện mọi dạng can thiệp thủ công.

## 3. Kiểm tra trình duyệt sau seeding

Chromium qua Playwright, desktop **1440×1000** và mobile **390×844**.
12 nhóm kiểm tra mới nhất trong `browser-retest.json`, **không có JS page error**:

1. Đăng nhập quản lý.
2. Dashboard có dữ liệu seed, thẻ số và SVG.
3. Xác nhận phiếu nhập nháp có sẵn.
4. Xác nhận đơn bán nháp có sẵn.
5. Hoàn bán và phục hồi kho/lịch sử.
6. Đăng nhập kho, kiểm tra trang đúng vai trò và 403 với bán hàng.
7. Đăng nhập bán hàng, kiểm tra trang đúng vai trò và 403 với kho.
8. Polling 10 giây giữ start/end đã chọn.
9. Mobile không tràn ngang; menu dùng bàn phím, sidebar ẩn không nhận focus.
10. Mô phỏng lỗi mạng: giữ số liệu cũ và hiển thị trạng thái thử lại.
11. Bán vượt tồn: báo lỗi, chứng từ vẫn nháp.
12. Tìm kiếm đúng SKU trong bộ seed.

Các thao tác ghi được thực hiện trên **bản sao pg_dump của bộ demo**, không trên
bộ dữ liệu chính. Audit bản sao sau thao tác vẫn `ok: true`. Database/server bản
sao đã được xóa/dừng. Browser context riêng và thông tin đăng nhập trong bộ nhớ đã dọn.

Đã đăng nhập đọc site chính 8010, dashboard trả HTTP 200, đúng 28 đơn xác nhận
trong kỳ (gồm 1 đơn đã hoàn), 1 hoàn trả và 3 sản phẩm tồn thấp. Dữ liệu chính vẫn
32 chứng từ/69 biến động như trước. Ảnh dashboard desktop/mobile trong screenshots/
được cập nhật từ bộ demo chính và đã xem trực tiếp.

21 nhóm kiểm tra ở `browser-results.json` là bằng chứng lần triển khai đầu, gồm
thêm sản phẩm, tạo/sửa nháp, nhập nhiều dòng, điều chỉnh có lý do và tạo nhân viên.
Không cộng hai đợt này thành một con số “test cases” mới vì có trường hợp trùng.

## 4. Persistence và tài liệu

- Đợt triển khai đầu đã kiểm tra restart giữ dữ liệu/session.
- pg_dump → pg_restore sang database mới: số chứng từ, số biến động, tổng tồn và
  giá trị tồn khớp; database khôi phục thử đã được xóa.
- `ARCHITECTURE.md`: module/layer map, ERD, sequence, state machine, dashboard flow.
- `PRESENTATION.md`: kịch bản 8–10 phút, ví dụ số và câu hỏi thường gặp.
- Module chính và use case quan trọng có docstring; tham chiếu Python source trong
  hai tài liệu đã được kiểm tra tồn tại.

## 5. Giới hạn xác minh

Đã kiểm tra macOS/Chromium, chưa kiểm tra trực tiếp Windows/Linux, Safari/Firefox
hoặc tải lớn. Đây là bản local một cửa hàng/kho. Dashboard polling 10 giây khi tab
hiện, chưa phải push tức thì. Lợi nhuận là lợi nhuận gộp; thanh toán ghi nhận thủ
công; chưa có VAT/hóa đơn điện tử, trả một phần, công nợ, biến thể/lô/serial,
nhiều kho hoặc thanh toán online. Chi tiết phạm vi trong SCOPE.md và README.md.

## 6. UI/UX và xóa dòng trực tiếp — 03/11/2026

- Sửa điểm UX của form: checkbox Bỏ dòng được thay bằng nút Xóa dòng khi JS chạy.
  Dòng ẩn ngay, có Hoàn tác giữ giá trị cũ; checkbox chuẩn vẫn là fallback không JS.
- 6 regression tests mới trong tests/test_document_rows.py cho tạo/sửa nháp nhập/bán,
  dòng xóa có input invalid, tổng tiền dòng còn lại và từ chối xóa hết rồi lưu.
- Tổng 58 tests pass; coverage 90.77%; lint/format/system check/migrations pass.
- Browser đã kiểm tra xóa giữa, undo, sửa nháp đã có dòng, xóa hết, thêm lại 105 lần
  không hết slot, bàn phím, mobile 390px và desktop 1440px. Không có JS page errors.
- 9 trang điều hướng chính trả 200 và có heading rõ ràng. Đây là rà soát sơ lược,
  không phải chứng nhận accessibility hoặc kiểm tra toàn bộ OS/browser.
- Căn nút xóa cạnh số lượng trên mobile đơn bán; thông báo lỗi trải hết form-grid.
- Bằng chứng: browser-row-delete.json; screenshots/purchase-rows-desktop.png và
  screenshots/sale-rows-mobile.png đã được xem trực tiếp.
- Thao tác ghi dùng bản sao PostgreSQL. Bản sao/server/context đã dọn; dữ liệu chính
  ở thời điểm rà có 33 chứng từ/71 biến động, audit ok=true, không reset dữ liệu người dùng.
- App chính đã restart tại 8010 để tải template mới.

Tham khảo UI checklist: https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md

## 7. Dấu × thay checkbox — 03/11/2026

User screenshot vẫn có checkbox Bỏ dòng. Đã chuyển DELETE thành HiddenInput và
render sẵn nút × 44×44 trong components/document_line.html, có aria-label/title.
JS cập nhật giá trị DELETE ẩn thay vì checked; thêm phiên bản asset JS/CSS để tránh
trình duyệt giữ bản cũ. Không còn checkbox ngay cả ở HTML trước khi JS khởi tạo.

60 tests pass, lint/format/check/migrations pass; có 2 regression kiểm tra HTML
không chứa checkbox/Bỏ dòng và có nút ×. Browser trên app chính đã xác minh nhập/bán:
nút ×, xóa trực tiếp, undo giữ giá trị, không lỗi JS; mobile không tràn ngang.
Không lưu chứng từ thử trên data chính. App đã restart, phiên bản asset row-x-2.
