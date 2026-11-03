# Hướng dẫn trình bày StoreDesk với giảng viên

## 1. Giới thiệu trong 30 giây

“StoreDesk là website quản lý một cửa hàng và một kho bằng Django. Nhân viên nhập
hàng, bán hàng và xem lịch sử kho theo vai trò. Quản lý theo dõi doanh số, lợi nhuận
gộp và tồn thấp trên dashboard tự cập nhật mỗi 10 giây. Dữ liệu nằm trong PostgreSQL;
giao diện được Django render trên server.”

Đề tài là ứng dụng kho/bán hàng riêng theo yêu cầu đã thống nhất, có vận dụng kiến
thức Django và visualization. Không trình bày nó như bài Learning Log nguyên bản
của Python Crash Course.

## 2. Chuẩn bị trước buổi demo

Từ thư mục project:

```sh
python3 run.py --prepare-only
./scripts/verify.sh
.venv/bin/python manage.py check_business_data
python3 run.py
```

Nếu web đã chạy ở 8010, chỉ cần dùng trang đang có và bỏ lệnh khởi chạy lần hai.
Mở http://127.0.0.1:8010/login/. Nếu browser còn giữ `/setup/`, tải lại hoặc vào
`/login/` vì quản lý demo đã được tạo sẵn.

| Tài khoản demo | Mục đích |
| --- | --- |
| `quanly` | Dashboard, quản lý và toàn bộ giao dịch |
| `nhanvien_kho` | Tồn kho, phiếu nhập, nhà cung cấp |
| `nhanvien_banhang` | Đơn bán và khách hàng |

Mật khẩu riêng nằm trong `var/demo-accounts.txt` trên máy. Không đưa nội dung file
này vào slide, repo hoặc tài liệu gửi công khai.

Bộ demo lúc kiểm tra: 8 sản phẩm, 1 nhà cung cấp, 3 khách hàng, 32 chứng từ,
69 biến động kho. Gồm 2 nháp, 28 xác nhận, 1 hủy và 1 hoàn; dữ liệu bán 14 ngày,
cả tiền mặt/chuyển khoản và 3 sản phẩm tồn thấp. Có dữ liệu ở mọi module chính;
đây là dữ liệu minh họa, không phải toàn bộ biến thể nghiệp vụ của một hệ thống ERP.
Bộ bán hàng được tạo cho khoảng **21/10/2026–03/11/2026**. Nếu demo vào ngày khác,
chọn lại khoảng này trên dashboard để xem đầy đủ, vì bộ lọc mặc định là 14 ngày gần nhất.
Số đếm sẽ thay đổi sau khi bạn thao tác, dùng lệnh đối chiếu để kiểm tra lại.

Không chạy seed_demo lần nữa trên dữ liệu hiện có: lệnh sẽ từ chối để tránh nạp trùng.

## 3. Kịch bản demo 8–10 phút

| Thời gian | Thao tác | Điểm cần giải thích |
| --- | --- | --- |
| 0–1 phút | Đăng nhập `quanly`, mở Tổng quan | Thẻ/biểu đồ lấy từ giao dịch thật trong PostgreSQL, không hard-code số liệu |
| 1–2 phút | Sản phẩm, đối tác và tồn kho | SKU, đơn vị, giá bán, ngưỡng tồn; Product khác Stock |
| 2–3 phút | Nhập hàng → lọc Nháp → mở phiếu chờ → xác nhận | Nháp không đổi tồn; xác nhận mới tăng tồn và ghi sổ |
| 3–5 phút | Bán hàng → mở đơn nháp hoặc tạo mới → giảm giá → xác nhận | Kiểm tra đủ tồn, ghi thanh toán đầy đủ và trừ kho |
| 5–6 phút | Mở dashboard ở tab khác | Chờ tối đa khoảng một chu kỳ 10 giây để thấy cập nhật, giữ nguyên bộ lọc ngày |
| 6–7 phút | Sổ kho; hoàn toàn bộ một đơn vừa bán | Mọi biến động có actor/lý do; hoàn phục hồi hàng và ghi nhận hoàn tiền |
| 7–8 phút | Đăng nhập vai trò kho/bán hàng, thử đường dẫn bị cấm | Phân quyền được kiểm tra server, không chỉ ẩn menu |
| 8–10 phút | Mở ARCHITECTURE.md và source tương ứng | Trình bày module, ERD, transaction và bằng chứng test |

Nên dùng một bản sao database cho buổi tập thao tác. Khi xác nhận/hoàn trên database
chính thì số liệu demo thay đổi thật. Không hủy phiếu chỉ để làm số đếm “trở lại ban đầu”.

### Ví dụ số dễ trình bày

Dùng Bút gel `PN-02`, giá bán 25.000 ₫ và giá nhập demo 11.000 ₫:

1. Bán 2 sản phẩm, giảm toàn đơn 5.000 ₫.
2. Tổng thu = 2 × 25.000 − 5.000 = **45.000 ₫**.
3. Nếu tồn của sản phẩm vẫn có giá vốn bình quân demo 11.000 ₫, giá vốn xuất = **22.000 ₫**.
4. Lợi nhuận gộp đơn = **23.000 ₫**; tồn giảm 2.
5. Hoàn toàn bộ: tồn tăng lại 2 và hoàn tiền 45.000 ₫, giá vốn được phục hồi theo đơn gốc.

Nếu bạn đã nhập hàng với giá khác, kiểm tra giá vốn hiện tại trước khi dùng ví dụ;
không khẳng định luôn là 11.000 ₫. Điều chỉnh kho cũng có thể làm thay đổi giá vốn.

## 4. Những file nên mở khi giải thích

| Câu hỏi | File / hàm |
| --- | --- |
| Đường dẫn trang bán hàng ở đâu? | `src/config/urls.py` |
| View có làm nghiệp vụ trừ tồn không? | `src/trading/views.py: document_detail` chỉ gọi service |
| Dữ liệu nhập được kiểm tra thế nào? | `src/trading/forms.py: DocumentForm, LineFormSet` |
| Khi nào cập nhật kho? | `src/trading/services.py: confirm_document` |
| Số dư và lịch sử cùng được ghi ở đâu? | `src/inventory/services.py: move` |
| Cấu trúc database ở đâu? | `src/catalog/models.py`, `src/trading/models.py`, `src/inventory/models.py` |
| Dashboard tính doanh số thế nào? | `src/analytics/selectors.py: dashboard, _snapshot` |
| Trình duyệt tự làm mới thế nào? | `src/static/js/dashboard.js: refresh, setInterval` |
| Phân quyền kiểm tra ở đâu? | `src/accounts/permissions.py: require_role, roles_required` |
| Có bằng chứng không bán quá tồn không? | `tests/test_concurrency.py` |
| Seed có gây trùng không? | `tests/test_seed_and_audit.py`, `seed_demo.py` |

## 5. Câu hỏi thường gặp

**Vì sao chọn Django?** Django có ORM, form, template, session và CSRF. Phù hợp
một web app nội bộ; service bổ sung để giữ nghiệp vụ rõ ràng và dễ kiểm thử.

**Đây là SSR hay SPA?** SSR cho các trang chính. Dashboard có fetch JSON để cập
nhật một phần trang. Không có React hoặc một frontend server riêng.

**Vì sao PostgreSQL?** Project có giao dịch tồn kho đồng thời. Hiện dùng khóa dòng
PostgreSQL và tests chạy trên chính PostgreSQL để kiểm chứng điều đó.

**Làm sao tránh tồn âm?** Khóa số dư trong transaction rồi mới kiểm tra. Nếu một
mặt hàng thiếu, toàn bộ chứng từ rollback; không chỉ dựa vào con số đang hiện trên UI.

**Bấm xác nhận hai lần thì sao?** Service kiểm tra trạng thái trong khóa Document;
confirmed sẽ không ghi biến động lần hai. Lưu nháp còn dùng UUID token và advisory lock.

**Lợi nhuận là lợi nhuận ròng?** Không. Đây là lợi nhuận gộp: doanh số thuần trừ giá vốn,
chưa trừ thuê mặt bằng, lương, thuế hoặc các chi phí vận hành khác.

**Hoàn đơn có xóa dữ liệu không?** Không. Giữ chứng từ và dòng hàng gốc, tạo biến động
đảo, lưu lý do/người thực hiện và ngày hoàn. Dashboard tính hoàn theo ngày hoàn.

**Thời gian thực đến mức nào?** Polling 10 giây khi tab đang hiện; có độ trễ một chu kỳ
và thời gian mạng/xử lý. Chưa dùng WebSocket/SSE.

**Có bán online/thanh toán ngân hàng không?** Hiện bán nội bộ và nhân viên ghi nhận
thanh toán thủ công. Chọn “Chuyển khoản” không tự xác minh giao dịch ngân hàng.

**Phạm vi còn giới hạn gì?** Một cửa hàng/kho, hàng số lượng nguyên, hoàn toàn bộ,
không công nợ, VAT/hóa đơn điện tử, serial/lô/hạn dùng hoặc nhiều chi nhánh.

## 6. Tài liệu gửi kèm

- README.md: cài đặt, chạy và cách dùng.
- docs/SCOPE.md: yêu cầu và giới hạn.
- docs/ARCHITECTURE.md: sơ đồ kiến trúc, ERD, sequence và module map.
- docs/VERIFICATION.md + verification.txt: phương pháp/kết quả kiểm thử.
- docs/data-check.json: đối chiếu dữ liệu demo hiện tại.
- docs/screenshots/: ảnh UI minh họa; không thay thế chạy demo thật.

### Thử thao tác dòng hàng

Ở form nhập hoặc bán, thêm 3 dòng rồi bấm Xóa dòng ở dòng giữa: dòng biến mất ngay.
Bấm Hoàn tác xóa dòng để thấy dữ liệu cũ trở lại. Xóa lần nữa và lưu nháp: chỉ những
dòng còn lại được lưu và tính tiền. Chỉ khi xác nhận chứng từ mới thay đổi tồn kho.
