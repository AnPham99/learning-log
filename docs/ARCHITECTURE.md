# Luồng hoạt động

```text
Trình duyệt → urls.py → views.py
                        ├─ GET: đọc dữ liệu → template → HTML
                        └─ POST: form → service → ORM → PostgreSQL
```

- Model: các bảng và quan hệ.
- Form: kiểm tra dữ liệu nhập.
- View: nhận yêu cầu, gọi xử lý, trả trang.
- Service: nghiệp vụ, phân quyền và transaction.
- Selector: truy vấn báo cáo.

## Dữ liệu chính

| Bảng | Nội dung |
| --- | --- |
| Product | Sản phẩm, SKU, giá bán |
| Contact | Nhà cung cấp hoặc khách hàng |
| Document | Phiếu nhập/đơn bán, trạng thái, tổng tiền, người tạo |
| Line | Sản phẩm, số lượng, giá trên từng chứng từ |
| Stock | Số lượng và giá trị tồn hiện tại |
| Movement | Biến động kho và người thực hiện |

Một Document có nhiều Line. Mỗi Product có một Stock và nhiều Movement.

## Nhập và bán

1. Nhập form, lưu nháp: tạo Document/Line, chưa đổi tồn.
2. Xác nhận: khóa chứng từ và tồn kho trong transaction.
3. Nhập cộng tồn; bán kiểm tra đủ hàng rồi trừ tồn.
4. Ghi Movement và giá vốn, chuyển sang Đã xác nhận.
5. Nếu lỗi, rollback toàn bộ.

Nháp có thể hủy. Chứng từ xác nhận chỉ được hoàn toàn bộ bởi quản lý.
Hoàn bán trả lại tồn và giá vốn gốc. Hoàn nhập bị chặn nếu sản phẩm có giao dịch tiếp theo.
Xác nhận lặp không cộng/trừ kho lần hai.

## Dashboard

Doanh thu thuần = tổng bán xác nhận trong kỳ − hoàn tiền trong kỳ.
Lợi nhuận gộp = doanh thu thuần − giá vốn ròng, chưa trừ chi phí vận hành.
Ngày hoàn được tính riêng với ngày bán. Tồn kho luôn là tồn hiện tại.
JavaScript lấy JSON cập nhật mỗi 10 giây khi tab đang mở.

## File chính

- `src/config/urls.py`: đường dẫn.
- `src/trading/views.py`, `forms.py`, `services.py`: chứng từ.
- `src/inventory/services.py`: cập nhật tồn và sổ kho.
- `src/analytics/selectors.py`: số liệu báo cáo.
- `src/accounts/permissions.py`: phân quyền.
