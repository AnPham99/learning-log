from pathlib import Path
from datetime import date
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'Bao_cao_Python_StoreDesk_PTIT.docx'
doc = Document()
s = doc.sections[0]
s.page_width, s.page_height = Cm(21), Cm(29.7)
s.top_margin, s.bottom_margin, s.left_margin, s.right_margin = Cm(2), Cm(2), Cm(3), Cm(2)
s.header_distance, s.footer_distance = Cm(.8), Cm(1)
s.different_first_page_header_footer = True
for name in ['Normal', 'Title', 'Subtitle', 'Heading 1', 'Heading 2', 'Heading 3', 'Caption']:
    st = doc.styles[name]
    st.font.name = 'Times New Roman'
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.font.size = Pt(13)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.15
for name, size in [('Title', 18), ('Heading 1', 15), ('Heading 2', 13)]:
    doc.styles[name].font.size = Pt(size)
    doc.styles[name].font.bold = True
doc.styles['Heading 1'].paragraph_format.space_before = Pt(0)
doc.styles['Heading 2'].paragraph_format.space_before = Pt(8)
doc.styles['Caption'].font.italic = True
doc.styles['Caption'].font.size = Pt(11)
normal = doc.styles['Normal'].paragraph_format
normal.widow_control = True
footer = s.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = footer.add_run()
field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), 'PAGE'); run._r.addnext(field)

def p(text='', bold=False, align=None):
    x = doc.add_paragraph()
    x.add_run(text).bold = bold
    if align is not None: x.alignment = align
    return x

def h(text, level=2): doc.add_heading(text, level)
def page(title):
    doc.add_page_break()
    h(title, 1)
def bullet(text):
    x=p('• ' + text)
    x.paragraph_format.left_indent=Cm(.3)
    x.paragraph_format.first_line_indent=Cm(-.3)

def table(headers, rows, widths):
    t=doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.autofit=False
    for c,w in zip(t.columns,widths): c.width=Cm(w)
    for c,txt,w in zip(t.rows[0].cells,headers,widths): c.width=Cm(w); c.text=txt
    for row in rows:
        cells=t.add_row().cells
        for c,txt,w in zip(cells,row,widths): c.width=Cm(w); c.text=str(txt)
    for i,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr()
        cant=OxmlElement('w:cantSplit'); trpr.append(cant)
        if i==0:
            repeat=OxmlElement('w:tblHeader'); trpr.append(repeat)
        for cell in row.cells:
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr=cell._tc.get_or_add_tcPr()
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'4'); e.set(qn('w:color'),'D9D9D9'); borders.append(e)
            pr.append(borders)
            mar=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge); e.set(qn('w:w'),'70'); e.set(qn('w:type'),'dxa'); mar.append(e)
            pr.append(mar)
            if i==0:
                sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),'E7E6E6'); pr.append(sh)
            for para in cell.paragraphs:
                para.paragraph_format.space_after=Pt(2)
                para.paragraph_format.line_spacing=1.05
                for r in para.runs: r.font.size=Pt(11); r.bold=i==0
    p('').paragraph_format.space_after=Pt(0)
    return t

def code(text):
    x=p()
    x.paragraph_format.line_spacing=1
    for n,line in enumerate(text.splitlines()):
        r=x.add_run(('\n' if n else '')+line)
        r.font.name='Consolas'; r.font.size=Pt(9)
    return x

C=WD_ALIGN_PARAGRAPH.CENTER
p('HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG',True,C)
p('KHOA TODO TÊN KHOA',True,C)
p('\n')
p('BÁO CÁO BÀI TẬP LỚN',True,C)
p('MÔN HỌC LẬP TRÌNH PYTHON',True,C)
p('\n')
t=doc.add_paragraph('XÂY DỰNG WEBSITE QUẢN LÝ KHO HÀNG\nVÀ BÁN HÀNG BẰNG DJANGO\nTÍCH HỢP DASHBOARD PHÂN TÍCH DỮ LIỆU', 'Title'); t.alignment=C
p('Ứng dụng StoreDesk',False,C)
p('\n')
for line in ['Giảng viên hướng dẫn: TODO', 'Lớp học phần: TODO', 'Nhóm thực hiện: TODO — 06 thành viên', 'Học kỳ và năm học: TODO']:
    p(line)
p('\n\n')
p('TODO ĐỊA ĐIỂM, tháng TODO năm TODO',False,C)

page('THÔNG TIN NHÓM VÀ MỤC LỤC')
h('Phân công nhiệm vụ cho 6 thành viên')
p('Phân công đề xuất với khối lượng tương đương, mỗi thành viên khoảng 1/6 tổng công việc. Nhóm xác nhận lại theo đóng góp thực tế trước khi nộp.')
table(['Thành viên', 'Phần việc chính', 'Sản phẩm bàn giao'],[
('TV1 — TODO họ tên, MSSV','Phân tích yêu cầu; accounts; điều phối tích hợp','Ma trận quyền, đăng nhập, kiểm thử quyền; mục 1 và 2.1'),
('TV2 — TODO họ tên, MSSV','catalog; thiết kế dữ liệu danh mục','Sản phẩm, đối tác, ràng buộc; mục 2.2'),
('TV3 — TODO họ tên, MSSV','inventory; giá vốn và đối soát','Tồn kho, điều chỉnh, sổ kho; mục 3.1'),
('TV4 — TODO họ tên, MSSV','trading; giao dịch và xử lý đồng thời','Phiếu nhập, đơn bán, hủy/hoàn; mục 3.2'),
('TV5 — TODO họ tên, MSSV','analytics; truy vấn và Dashboard','Chỉ số, JSON, biểu đồ, polling; mục 3.3 và 3.4'),
('TV6 — TODO họ tên, MSSV','Giao diện dùng chung; kiểm thử tích hợp; triển khai','Templates/CSS, bằng chứng chạy, đóng gói báo cáo; chương 4 và kết luận'),
],[3.5,6.2,6.3])
p('Mỗi thành viên tự kiểm thử mô-đun, rà soát chéo ít nhất một phần của thành viên khác và tham gia trình bày. TV1 tổng hợp nội dung; TV6 chuẩn hóa bản nộp.')
h('Mục lục')
for text in [
'Chương 1  Bài toán và phạm vi thực hiện ........................................ 3',
'Chương 2  Kiến trúc và thiết kế dữ liệu ........................................... 4',
'Chương 3  Cài đặt các nghiệp vụ và Dashboard ............................. 6',
'Chương 4  Kiểm thử và kết quả thực hiện ....................................... 9',
'Kết luận và tài liệu tham khảo ...................................................... 11']:
    p(text)
p('Các bảng và hình được đánh số trong từng chương. TODO: đối chiếu mẫu bìa, quy định trình bày của giảng viên và cập nhật mục lục nếu chỉnh sửa nội dung.',False)

page('CHƯƠNG 1  BÀI TOÁN VÀ PHẠM VI THỰC HIỆN')
h('1.1  Mục tiêu và phạm vi')
p('StoreDesk hỗ trợ một cửa hàng quản lý xuyên suốt từ nhập hàng, lập đơn bán đến kiểm soát tồn kho và theo dõi kết quả kinh doanh. Nhóm tập trung bảo đảm số liệu nhất quán khi nhiều nhân viên thao tác, đồng thời cung cấp Dashboard tự cập nhật để quản lý theo dõi doanh thu và hàng cần nhập thêm.')
p('Phạm vi triển khai là một cửa hàng, một kho; thanh toán được ghi nhận thủ công bằng tiền mặt hoặc chuyển khoản. Đây là ứng dụng nghiệp vụ nội bộ, chưa có quy trình khách hàng tự đặt mua và thanh toán trực tuyến.')
h('1.2  Chức năng và quyền sử dụng')
p('Bảng 1.1  Các nhóm chức năng đã có trong mã nguồn')
table(['Nhóm chức năng','Nội dung','Vai trò chính'],[
('Danh mục','Thêm/sửa sản phẩm, SKU, giá bán, ngưỡng tồn; nhà cung cấp và khách hàng','Quản lý; đối tác theo nghiệp vụ'),
('Kho','Nhập hàng, xem tồn/sổ kho, cảnh báo tồn thấp; quản lý điều chỉnh chênh lệch kiểm kê','Kho và quản lý'),
('Bán hàng','Đơn nhiều dòng, giảm giá, ghi nhận cách thanh toán; xác nhận mới trừ kho','Bán hàng và quản lý'),
('Chứng từ','Nháp → xác nhận; hủy nháp; quản lý hoàn toàn bộ chứng từ đã xác nhận','Theo loại chứng từ'),
('Dashboard','Doanh thu thuần, lợi nhuận gộp, doanh thu theo ngày, bán chạy và tồn thấp','Chỉ quản lý'),
('Tài khoản','Tạo quản lý lần đầu; quản lý tạo và quản trị nhân viên','Quản lý'),
],[3.1,9.5,3.4])
h('1.3  Yêu cầu chất lượng và giới hạn')
bullet('Tồn kho và giá trị tồn không âm; nếu một dòng bán thiếu hàng thì toàn bộ xác nhận phải bị hủy giao dịch.')
bullet('Thao tác lặp hoặc hai người cùng xác nhận không được làm cập nhật tồn hai lần. Kiểm tra quyền ở máy chủ, bao gồm lớp service.')
bullet('Dashboard dùng cùng quy tắc tính ngày bán/ngày hoàn; lỗi mạng phải giữ số liệu đang hiển thị và báo trạng thái cập nhật.')
p('Hiện trạng so với định hướng ban đầu: danh sách bán chạy lấy tối đa 6 sản phẩm; biểu đồ vẫn nhóm theo ngày dù chọn khoảng tuần/tháng; chưa có tỉ lệ đơn thành công/hủy, giỏ hàng công khai, WebSocket hoặc hóa đơn điện tử. Các hạng mục này thuộc hướng phát triển.')

page('CHƯƠNG 2  KIẾN TRÚC VÀ THIẾT KẾ DỮ LIỆU')
h('2.1  Công nghệ và lựa chọn kiến trúc')
p('Bảng 2.1  Công nghệ đối chiếu từ cấu hình và mã nguồn')
table(['Thành phần','Triển khai thực tế','Lý do phù hợp'],[
('Python và Django','Python 3.13.9; Django 6.1.2 trong môi trường kiểm tra và requirements.txt','Dùng chung ORM, forms, xác thực và templates'),
('Cơ sở dữ liệu','PostgreSQL; psycopg[binary] 3.3.6','Khóa dòng, giao dịch và mức cô lập phục vụ nghiệp vụ kho'),
('Frontend','Django Templates, HTML, CSS tự viết, JavaScript thuần','Một ứng dụng đồng nhất; không cần frontend tách riêng'),
('Dashboard','ORM Sum/TruncDate; JSON; SVG và thanh xếp hạng bằng DOM/CSS','Không cần Pandas hoặc thư viện vẽ biểu đồ ngoài'),
('Tự cập nhật','fetch và setInterval mỗi 10 giây','Đủ cho quy mô đồ án; không vận hành hàng đợi hay kết nối đẩy'),
],[3.4,6.3,6.3])
p('Chưa dùng Django REST Framework, Celery, Channels, Bootstrap, Chart.js hoặc Plotly. Phiên bản PostgreSQL thực tế trên máy nộp: TODO. Yêu cầu cài đặt trong README là Python 3.12+ và PostgreSQL 15+. [1]')
p('Nhóm chọn MVT vì phần lớn tương tác là biểu mẫu nghiệp vụ và trang dữ liệu. View xử lý HTTP, Form kiểm tra đầu vào, Template hiển thị; service tách các quy tắc kho khỏi giao diện và selector tập trung truy vấn báo cáo. Cách tổ chức này cho phép kiểm thử nghiệp vụ mà không phụ thuộc trình duyệt. [2]')
code('Trình duyệt → urls.py → View → Form → Service → ORM → PostgreSQL\n                          ↓                  ↑\n                       Template ← Selector ──┘\nDashboard JS → GET /dashboard/data/ → Selector → JSON → SVG/DOM')
p('Hình 2.1  Luồng xử lý chính và luồng cập nhật Dashboard',False,C)
p('Các ứng dụng được chia theo nghiệp vụ: accounts quản lý quyền; catalog quản lý danh mục; trading quản lý chứng từ; inventory quản lý tồn và lịch sử; analytics tổng hợp báo cáo. GET đọc dữ liệu; POST thay đổi trạng thái sau xác thực, kiểm tra CSRF và phân quyền.')

page('2.2  THIẾT KẾ CƠ SỞ DỮ LIỆU')
p('Bảng 2.2  Các bảng nghiệp vụ và trường quan trọng [3]')
table(['Model','Trường chính và kiểu dữ liệu','Ràng buộc và quan hệ'],[
('Product','sku Char(40); name Char(160); category Char(80); unit Char(30); selling_price Decimal(14,0); reorder_level PositiveInteger; active Boolean','SKU duy nhất; giá bán ≥ 0; một Stock; nhiều Line và Movement'),
('Contact','kind Char(12); name Char(160); phone Char(30); email Email; address Char(250); active Boolean','kind là supplier hoặc customer; được Document tham chiếu'),
('Document','kind/status Char(12); request_key UUID; discount Decimal(16,0); total Decimal(18,0); cost Decimal(22,4); payment_method Char(8); các mốc ngày giờ','request_key duy nhất; total/discount ≥ 0; FK contact và người tạo/xác nhận/hoàn'),
('Line','FK document/product; product_name Char(160); sku Char(40); quantity PositiveInteger; unit_price Decimal(14,0); cost Decimal(22,4)','quantity > 0; giá ≥ 0; duy nhất cặp document–product'),
('Stock','OneToOne product; quantity PositiveInteger; value Decimal(22,4)','Một bản ghi tồn cho mỗi sản phẩm; value ≥ 0'),
('Movement','FK product/document/actor; quantity Integer; value Decimal(22,4); balance PositiveInteger; reason Char(250); created_at DateTime','quantity/value có dấu; document có thể rỗng khi điều chỉnh; lưu số dư sau giao dịch'),
],[2.2,8.5,5.3])
p('Tất cả bảng có khóa chính id kiểu BigAutoField theo cấu hình mặc định. User và Group dùng cơ chế xác thực của Django; ba nhóm nghiệp vụ là manager, warehouse và sales.')
code('Contact 1 ── N Document 1 ── N Line N ── 1 Product\nUser    1 ── N Document                 Product 1 ── 1 Stock\nUser    1 ── N Movement N ── 1 Product\nDocument 1 ── N Movement  (có thể không gắn chứng từ)')
p('Hình 2.2  Quan hệ giữa các thực thể nghiệp vụ',False,C)
p('Line lưu bản chụp tên, SKU, đơn giá tại lúc lưu nháp; Document lưu tên đối tác. Vì vậy sửa danh mục sau đó không tự đổi dữ liệu các dòng đã lưu. PROTECT ngăn xóa đối tượng đang được tham chiếu; Line dùng CASCADE theo Document. Tiền dùng Decimal, giá vốn giữ 4 chữ số thập phân để giảm sai số làm tròn. Các cột trạng thái và mốc thời gian chứng từ có chỉ mục phục vụ lọc báo cáo.')

page('CHƯƠNG 3  CÀI ĐẶT NGHIỆP VỤ VÀ DASHBOARD')
h('3.1  Cập nhật tồn và tính giá vốn')
p('Stock lưu số lượng Q và giá trị V hiện tại; Movement ghi biến động và người thực hiện. Khi nhập q sản phẩm giá p, hệ thống cộng Q thêm q, V thêm q × p. Khi bán q, giá vốn xuất = V/Q × q, làm tròn 4 chữ số thập phân; nếu bán hết thì lấy toàn bộ V để không còn giá trị dư. [4]')
p('Ví dụ minh họa quy tắc: nhập 10 đơn vị giá 10.000đ rồi 10 đơn vị giá 30.000đ tạo Q = 20, V = 400.000đ. Bán 5 đơn vị ghi giá vốn 100.000đ; tồn còn 15 đơn vị trị giá 300.000đ. Đây cũng là tình huống đã có trong kiểm thử.')
p('Cảnh báo khi quantity ≤ reorder_level đối với sản phẩm đang kinh doanh. Kiểm kê hiện được hỗ trợ bằng điều chỉnh chênh lệch có lý do do quản lý thực hiện; chưa có quy trình lập và duyệt phiếu kiểm kê riêng.')
h('3.2  Xác nhận đơn và bảo đảm nhất quán')
for text in [
'1. View nhận POST, xác thực người dùng và kiểm tra Form/FormSet; save_draft kiểm tra loại đối tác, số lượng, giá và giảm giá rồi lưu Document/Line. Lưu nháp chưa thay đổi kho.',
'2. confirm_document chạy trong transaction.atomic, khóa Document bằng select_for_update. Nếu đã xác nhận thì trả lại chứng từ, không cập nhật tồn lần nữa.',
'3. Lấy các dòng và khóa Stock theo thứ tự product_id để các giao dịch dùng cùng thứ tự khóa. Phiếu nhập cộng tồn; đơn bán kiểm tra đủ hàng trước khi xuất từng dòng.',
'4. Ghi Movement, giá vốn từng Line, tổng cost, người xác nhận và confirmed_at. Nếu bất kỳ dòng nào lỗi, transaction rollback toàn bộ các thay đổi của lần xác nhận.',
'5. JavaScript Dashboard lấy snapshot mới ở chu kỳ kế tiếp. Với kết nối bình thường, thay đổi được phản ánh sau khoảng thời gian chờ chu kỳ cộng thời gian xử lý và mạng.',
]: p(text)
p('Khi tạo nháp, UUID request_key kết hợp khóa tư vấn PostgreSQL pg_advisory_xact_lock và ràng buộc duy nhất giúp chống tạo trùng do gửi lại cùng yêu cầu. Khi hai đơn cùng mua lượng tồn cuối, khóa dòng buộc chúng xử lý lần lượt; đơn sau kiểm tra lại tồn và có thể bị từ chối. [4]')
p('Hủy nháp chuyển sang cancelled, không ghi biến động kho. Hoàn chứng từ đã xác nhận chỉ dành cho quản lý và hoàn toàn bộ: hoàn bán trả lại số lượng và giá vốn gốc; hoàn nhập bị chặn nếu sản phẩm có biến động tiếp theo. Hệ thống lưu lý do, người thực hiện và thời điểm hoàn.')

page('3.3  THIẾT KẾ DASHBOARD VÀ LUỒNG DỮ LIỆU')
p('Pipeline xử lý là PostgreSQL → selector tổng hợp bằng ORM → JsonResponse → fetch → cập nhật chỉ số, SVG và DOM. Doanh thu theo thời gian và tồn kho dùng hai cách diễn giải: doanh thu theo khoảng ngày đã chọn; tồn kho luôn phản ánh hiện tại. [5]')
p('Bảng 3.1  Quy tắc tính các chỉ số')
table(['Chỉ số','Cách tính và ý nghĩa'],[
('Doanh thu thuần','Tổng total của đơn bán xác nhận trong kỳ trừ total của đơn hoàn trong kỳ; nháp và hủy nháp không tính.'),
('Lợi nhuận gộp','Doanh thu thuần trừ giá vốn ròng; giá vốn ròng = cost bán trong kỳ − cost hoàn trong kỳ. Chưa trừ chi phí vận hành.'),
('Chuỗi doanh thu ngày','TruncDate theo confirmed_at và reversed_at; Sum(total) mỗi ngày; trừ hoàn và bổ sung ngày không phát sinh bằng 0.'),
('Sản phẩm bán chạy','Cộng số lượng bán theo sản phẩm rồi trừ số lượng hoàn trong kỳ; sắp giảm dần, lấy tối đa 6 ứng viên và chỉ giữ lượng ròng dương.'),
('Số đơn và số hoàn','orders đếm đơn có ngày xác nhận trong kỳ, kể cả đơn đã hoàn; returns đếm đơn có ngày hoàn trong kỳ. Không phải tỉ lệ thành công/hủy.'),
('Tồn và cảnh báo','Tổng quantity/value hiện tại; đếm sản phẩm active có tồn ≤ ngưỡng; danh sách cảnh báo hiển thị tối đa 8 sản phẩm.'),
],[3.8,12.2])
p('Khoảng lọc được chuyển thành [00:00 ngày bắt đầu, 00:00 ngày sau ngày kết thúc) theo Asia/Ho_Chi_Minh. Form giới hạn tối đa 366 ngày và mặc định 14 ngày gần nhất. Ví dụ bán hôm trước, hoàn hôm nay: ngày trước ghi doanh thu bán, hôm nay ghi doanh thu âm do hoàn; tổng cả hai ngày bằng 0 nếu hoàn toàn bộ.')
p('dashboard mở transaction; nếu không nằm trong transaction có sẵn, đặt mức cô lập REPEATABLE READ trước khi lấy dữ liệu. Các truy vấn của một snapshot vì vậy đọc cùng ảnh chụp dữ liệu trong giao dịch đó. Tổng hợp ở CSDL và dùng select_related giúp hạn chế việc kéo dữ liệu hoặc truy vấn lặp không cần thiết.')
p('Phía trình duyệt gọi lại mỗi 10 giây khi tab hiển thị, bỏ qua nếu yêu cầu trước chưa xong, timeout 8 giây. Khi trở lại tab, tải lại ngay; nếu lỗi thì giữ dữ liệu cũ và hiển thị thông báo. Đây là cập nhật gần thời gian thực bằng polling, chưa có cơ chế đẩy ngay khi phát sinh đơn.')

page('3.4  TRÍCH ĐOẠN CỐT LÕI VÀ CÁC VIEW')
p('Trích nguyên văn phần đầu hàm _snapshot trong src/analytics/selectors.py; đây là đoạn tổng hợp doanh thu và giá vốn, không phải toàn bộ hàm. [5]')
source=(ROOT/'src/analytics/selectors.py').read_text(encoding='utf-8')
snippet=source[source.index('    lower, upper = date_bounds'):source.index('    days = defaultdict')]
code(snippet.rstrip())
p('Giải thích theo dòng trong đoạn trích:')
bullet('Dòng 1 tạo hai cận thời gian có múi giờ. Dòng 2 chọn đơn bán đã xác nhận hoặc đã hoàn để không làm mất lịch sử doanh thu.')
bullet('Dòng 3 lọc bán theo ngày xác nhận; dòng 4 lọc hoàn theo ngày hoàn. Hai tập này có thể chứa cùng chứng từ nếu cả bán và hoàn nằm trong kỳ.')
bullet('Dòng 5–6 dùng aggregate và Sum tại CSDL để cộng tiền và giá vốn. Dòng 7–8 thay kết quả rỗng bằng Decimal(0), sau đó trừ hoàn để ra doanh thu thuần và giá vốn ròng.')
p('Bảng 3.2  Các đường dẫn và View tiêu biểu [6]')
table(['Đường dẫn và phương thức','View và kết quả','Quyền'],[
('GET /','home → dashboard_page; trả HTML hoặc điều hướng theo vai trò','Đăng nhập; Dashboard chỉ quản lý'),
('GET /dashboard/data/?start=…&end=…','dashboard_data; JSON snapshot; ngày sai trả HTTP 400','Quản lý'),
('GET/POST /products/new/','product_edit; biểu mẫu tạo sản phẩm','Quản lý'),
('GET/POST /documents/<kind>/new/','document_edit; lưu nháp; kind = purchase hoặc sale','Kho/nhập; bán hàng/bán; quản lý'),
('GET/POST /document/<pk>/','document_detail; POST action=confirm hoặc reverse; xử lý rồi redirect','Theo loại; hoàn chỉ quản lý'),
('GET /stock/ và /stock/ledger/','stock_list và ledger; tồn và biến động','Kho hoặc quản lý'),
('GET/POST /stock/adjust/','adjustment; ghi chênh lệch có lý do','Quản lý'),
],[6,6.7,3.3])
p('Các đường dẫn nghiệp vụ phục vụ HTML/Form; chỉ endpoint Dashboard trả JSON. Hệ thống dùng session của Django, CSRF cho POST, kiểm tra vai trò ở View và service. Dữ liệu nhạy cảm của Dashboard có never_cache; JSON hợp lệ được JS đưa vào textContent và thuộc tính SVG.')

page('CHƯƠNG 4  KIỂM THỬ VÀ KẾT QUẢ THỰC HIỆN')
h('4.1  Môi trường và kết quả kiểm thử')
p('Kiểm tra ngày 07/11/2026 trên môi trường dự án: Python 3.13.9, Django 6.1.2, backend PostgreSQL. Lệnh .venv\\Scripts\\python.exe -m pytest -q hoàn thành với 60 passed trong 29,29 giây. Đây là kiểm thử tự động trên CSDL kiểm thử riêng, chưa phải đo tải triển khai thực tế. [7]')
p('Bảng 4.1  Các tình huống quan trọng trong bộ kiểm thử đã chạy')
table(['Tình huống','Kết quả mong đợi đã được kiểm tra'],[
('Nhập, bán và xác nhận lặp','Lưu nháp chưa đổi tồn; xác nhận cập nhật đúng; gọi lặp không tạo thêm Movement.'),
('Thiếu hàng ở một dòng','Rollback cả đơn; các sản phẩm khác không bị trừ dở dang.'),
('Hai đơn đồng thời cùng bán 4 khi chỉ còn 5','Một đơn xác nhận, một đơn bị từ chối; tồn cuối bằng 1.'),
('Hai lần xác nhận hoặc tạo nháp đồng thời','Chỉ một lần nhập tồn; cùng request_key chỉ tạo một chứng từ.'),
('Giá vốn bình quân và hoàn toàn bộ','Bán đúng giá vốn bình quân; hoàn khôi phục số lượng và giá trị gốc.'),
('Hoàn nhập sau giao dịch tiếp theo','Bị chặn để tránh đảo sai giá trị tồn.'),
('Ngày bán khác ngày hoàn','Doanh thu phân bổ theo từng ngày; tổng chuỗi ngày bằng doanh thu thuần toàn kỳ.'),
('Dữ liệu hoặc vai trò không hợp lệ','Chặn số lượng/giá/giảm giá sai, sai quyền; endpoint ngày sai trả 400.'),
],[6,10])
h('4.2  Cách chạy và kịch bản trình diễn')
p('Cài Python và PostgreSQL theo README, chạy python run.py, mở http://127.0.0.1:8010/. Launcher chuẩn bị môi trường, khởi động PostgreSQL cục bộ và chạy migrations. Lần đầu tạo tài khoản quản lý; sau đó tạo nhân viên kho và bán hàng. Dữ liệu nằm trong var; không xóa thư mục này khi cần giữ dữ liệu. [1]')
p('Kịch bản bảo vệ: nhập 10 sản phẩm → xác nhận nhập → lập và xác nhận bán 3 → kiểm tra tồn còn 7 và sổ kho → mở Dashboard và chờ chu kỳ cập nhật → thử bán quá tồn để thấy bị chặn → quản lý hoàn đơn và đối chiếu lại tồn, doanh thu. Dùng dữ liệu minh họa riêng và ghi ảnh kết quả thực tế.')
p('TODO: bổ sung cấu hình máy, phiên bản PostgreSQL và bằng chứng kiểm thử trình duyệt/mobile. Chưa đo thời gian phản hồi, số người dùng đồng thời hoặc tốc độ với tập dữ liệu lớn; không kết luận về hiệu năng sản xuất khi chưa đo.')

page('4.3  GIAO DIỆN VÀ KẾT QUẢ MINH HỌA')
doc.add_picture(str(ROOT/'docs/screenshots/dashboard.png'),width=Cm(15.3))
doc.paragraphs[-1].alignment=C
p('Hình 4.1  Dashboard StoreDesk với dữ liệu minh họa trong CSDL',False,C)
p('Ảnh giao diện lưu trong dự án ngày 07/11/2026, kỳ 23/10–07/11/2026: đã thu 13.030.000đ, hoàn tiền 500.000đ, doanh thu thuần 12.530.000đ và lợi nhuận gộp 4.394.000đ. Đây là dữ liệu minh họa, không phải doanh thu kinh doanh thực tế. [8]')
p('Đối chiếu: 13.030.000 − 500.000 = 12.530.000đ. Dashboard thể hiện doanh thu theo ngày, sản phẩm bán chạy, đơn gần đây, tồn hiện tại và cảnh báo cần nhập thêm. Số liệu sẽ thay đổi khi nhóm thao tác; cần cập nhật ảnh nếu đổi bộ dữ liệu nộp.')

page('KẾT LUẬN VÀ TÀI LIỆU THAM KHẢO')
h('Kết luận')
p('Nhóm đã xây dựng StoreDesk với quy trình nhập và bán gắn trực tiếp với tồn kho, lịch sử biến động và báo cáo. Điểm trọng tâm là xác nhận chứng từ trong một giao dịch có khóa dữ liệu, lưu giá vốn tại thời điểm xuất và tính doanh thu có xét thời điểm hoàn. Dashboard tự lấy số liệu mỗi 10 giây, giúp quản lý theo dõi cùng một nguồn dữ liệu với nghiệp vụ hàng ngày.')
p('Bộ 60 kiểm thử tự động đã chạy thành công, bao gồm giao dịch, đồng thời, phân quyền và tổng hợp báo cáo. Kết quả này chứng minh các tình huống được kiểm tra trong môi trường hiện tại; việc vận hành thực tế cần thêm kiểm thử tải và quy trình triển khai phù hợp.')
h('Hạn chế và hướng phát triển')
bullet('Chuẩn hóa theo yêu cầu cuối của môn học: đổi top 6 thành top 5 nếu bắt buộc; bổ sung nhóm theo tuần/tháng và biểu đồ tỉ lệ đơn với mẫu số, trạng thái và mốc thời gian rõ ràng.')
bullet('Bổ sung giỏ hàng cho khách, thanh toán trực tuyến, in/xuất chứng từ và quy trình kiểm kê riêng nếu mở rộng phạm vi; hiện chỉ ghi nhận thanh toán thủ công, hoàn toàn bộ và một kho.')
bullet('Khi cần độ trễ thấp hơn polling, đánh giá Channels/WebSocket; chỉ bổ sung Celery cho tác vụ nền có nhu cầu cụ thể. Đo tải trước khi quyết định cache hoặc bảng tổng hợp.')
bullet('Hoàn thiện triển khai: HTTPS, cấu hình production, sao lưu/khôi phục và theo dõi lỗi. Không đưa mật khẩu, .venv hoặc thư mục dữ liệu PostgreSQL vào bản mã nguồn nộp.')
h('Tài liệu tham khảo')
p('Nguồn chính là mã nguồn và tài liệu dự án StoreDesk, đối chiếu ngày 07/11/2026. Đường dẫn dưới đây tính từ thư mục gốc dự án.')
for text in [
'[1] requirements.txt; pyproject.toml; README.md; run.py; src/config/settings.py. Công nghệ và hướng dẫn vận hành.',
'[2] docs/ARCHITECTURE.md. Kiến trúc và luồng xử lý nghiệp vụ.',
'[3] src/catalog/models.py; src/trading/models.py; src/inventory/models.py. Thiết kế dữ liệu và ràng buộc.',
'[4] src/trading/services.py; src/inventory/services.py; src/accounts/permissions.py. Giao dịch, giá vốn và phân quyền.',
'[5] src/analytics/selectors.py; forms.py; views.py; src/static/js/dashboard.js. Truy vấn và cập nhật Dashboard.',
'[6] src/config/urls.py và các views.py tương ứng. Đường dẫn và xử lý yêu cầu.',
'[7] tests/test_transactions.py; test_concurrency.py; test_dashboard.py và toàn bộ thư mục tests. Kết quả chạy pytest nêu tại mục 4.1.',
'[8] docs/README.md; docs/screenshots/dashboard.png. Ảnh giao diện và dữ liệu minh họa.',
]:
    x=p(text); x.paragraph_format.space_after=Pt(4)
    for r in x.runs: r.font.size=Pt(11)

doc.core_properties.title='Báo cáo Lập trình Python StoreDesk PTIT'
doc.core_properties.author='Nhóm TODO gồm 6 thành viên'
doc.core_properties.subject='Website quản lý kho và bán hàng bằng Django tích hợp Dashboard'
# Strip built-in theme fonts and decorative title borders from the base template.
for st in doc.styles:
    for border in list(st.element.iter(qn('w:pBdr'))):
        border.getparent().remove(border)
    if st.name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
        rf=st.element.get_or_add_rPr().find(qn('w:rFonts'))
        if rf is not None:
            for key in list(rf.attrib):
                if 'Theme' in key or 'theme' in key: del rf.attrib[key]
            for key in ['ascii','hAnsi','eastAsia','cs']: rf.set(qn('w:'+key),'Times New Roman')
last_page=False
for para in doc.paragraphs:
    if para.text=='KẾT LUẬN VÀ TÀI LIỆU THAM KHẢO': last_page=True
    if last_page:
        para.paragraph_format.line_spacing=1.05
        para.paragraph_format.space_after=Pt(4)
    for border in list(para._p.iter(qn('w:pBdr'))): border.getparent().remove(border)
doc.save(OUT)
print(OUT)
