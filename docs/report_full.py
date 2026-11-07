"""Build the extended report from the verified compact report and source excerpts."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'var/report_full_qa'
ASSETS.mkdir(parents=True, exist_ok=True)
FONT='C:/Windows/Fonts/arial.ttf'

def diagram(kind):
    im=Image.new('RGB',(1800,1100),'white'); d=ImageDraw.Draw(im)
    f=ImageFont.truetype(FONT,27); small=ImageFont.truetype(FONT,23)
    def box(x,y,w,h,title,body=''):
        d.rounded_rectangle((x,y,x+w,y+h),radius=9,outline='#333333',width=3,fill='#f7f7f7')
        d.text((x+w/2,y+26),title,font=f,anchor='mm',fill='black')
        if body: d.multiline_text((x+17,y+58),body,font=small,fill='black',spacing=10)
    def arrow(a,b,label='',offset=(0,-24)):
        import math
        d.line((a,b),fill='#555555',width=3)
        th=math.atan2(b[1]-a[1],b[0]-a[0])
        pts=[b,(b[0]-15*math.cos(th-.45),b[1]-15*math.sin(th-.45)),(b[0]-15*math.cos(th+.45),b[1]-15*math.sin(th+.45))]
        d.polygon(pts,fill='#555555')
        if label: d.text(((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1]),label,font=small,anchor='mm',fill='black')
    if kind=='usecase':
        d.rectangle((460,45,1750,1050),outline='#555',width=3)
        d.text((1100,85),'HỆ THỐNG STOREDESK',font=f,anchor='mm',fill='black')
        for y,name in [(190,'Quản lý'),(510,'Nhân viên kho'),(830,'Nhân viên bán hàng')]:
            d.ellipse((170,y-28,210,y+12),outline='black',width=3)
            d.line((190,y+12,190,y+100),fill='black',width=3)
            d.line((140,y+50,240,y+50),fill='black',width=3)
            d.line((190,y+100,145,y+145),fill='black',width=3)
            d.line((190,y+100,235,y+145),fill='black',width=3)
            d.text((190,y+180),name,font=f,anchor='mm',fill='black')
        cases=[(155,'Đăng nhập và xem sản phẩm'),(280,'Quản trị tài khoản và sản phẩm'),(405,'Theo dõi Dashboard'),(530,'Lập và xác nhận phiếu nhập'),(655,'Xem tồn kho và sổ kho'),(780,'Lập và xác nhận đơn bán'),(905,'Điều chỉnh tồn và hoàn chứng từ')]
        for y,txt in cases:
            d.ellipse((740,y-42,1590,y+42),outline='#333',width=3,fill='#f7f7f7')
            d.text((1165,y),txt,font=f,anchor='mm',fill='black')
        for y in [155,280,405,530,655,780,905]: d.line((260,240,740,y),fill='#888',width=2)
        for y in [155,530,655]: d.line((260,560,740,y),fill='#555',width=2)
        for y in [155,780]: d.line((260,880,740,y),fill='#333',width=2)
    elif kind=='erd':
        box(45,80,440,210,'Contact','PK id\nkind, name, active')
        box(680,80,440,260,'Document','PK id; UNIQUE request_key\nFK contact, created_by\nFK confirmed_by, reversed_by\nkind, status, total, cost')
        box(1310,80,440,210,'User và Group','User PK id\nQuyền theo nhóm nghiệp vụ')
        box(680,530,440,220,'Line','PK id; FK document, product\nquantity, unit_price, cost\nUNIQUE document + product')
        box(45,530,440,220,'Product','PK id; UNIQUE sku\nselling_price, reorder_level\nname, active')
        box(45,880,440,170,'Stock','PK id; UNIQUE FK product\nquantity, value')
        box(1310,530,440,260,'Movement','PK id; FK product, actor\nFK document có thể rỗng\nquantity, value, balance\nreason, created_at')
        arrow((485,180),(680,180),'1 : N')
        arrow((1310,180),(1120,180),'1 : N')
        arrow((900,340),(900,530),'1 : N',(-65,0))
        arrow((485,635),(680,635),'1 : N')
        arrow((260,750),(260,880),'1 : 1',(-65,0))
        arrow((1530,290),(1530,530),'1 : N',(65,0))
        arrow((1120,290),(1310,555),'1 : N',(10,-25))
        d.line(((485,720),(580,720),(580,840),(1430,840),(1430,790)),fill='#555',width=3)
        d.text((920,865),'Product 1 : N Movement',font=small,anchor='mm',fill='black')
        d.text((1000,1000),'FK bảo vệ danh mục và lịch sử; Line phụ thuộc Document',font=f,anchor='mm',fill='black')
    else:
        xs=[130,490,850,1210,1650]
        for x,name in zip(xs,['Trình duyệt','View và Form','Service','PostgreSQL','Dashboard JS']):
            box(x-115,30,230,70,name)
            d.line((x,110,x,1050),fill='#aaa',width=2)
        events=[(0,1,'POST action=confirm'),(1,2,'confirm_document'),(2,3,'BEGIN và khóa Document'),(3,2,'Trạng thái hiện tại'),(2,3,'Khóa Stock theo product_id'),(3,2,'Số lượng và giá trị tồn'),(2,3,'Cập nhật Stock, Line, Movement'),(2,3,'Cập nhật Document và COMMIT'),(2,1,'Trả chứng từ'),(1,0,'Redirect về chi tiết'),(4,1,'GET /dashboard/data/ mỗi 10 giây'),(1,4,'JSON snapshot → cập nhật SVG')]
        for i,(a,b,label) in enumerate(events):
            y=160+i*73
            arrow((xs[a],y),(xs[b],y),label,(0,-22))
    path=ASSETS/(kind+'.png'); im.save(path); return path

for kind in ['usecase','erd','sequence']: diagram(kind)

intro=r'''
page('LỜI MỞ ĐẦU')
p('Trong quản lý cửa hàng, một đơn bán đồng thời ảnh hưởng đến doanh thu, giá vốn và tồn kho. Nếu các dữ liệu này được cập nhật rời rạc, việc kiểm tra tình hình kinh doanh và truy tìm chênh lệch sẽ khó khăn. Từ yêu cầu đó, nhóm xây dựng StoreDesk để kết nối nghiệp vụ nhập hàng, bán hàng và phân tích dữ liệu trong cùng một ứng dụng web.')
p('Mục tiêu của đồ án là triển khai quy trình có thể sử dụng và kiểm chứng: lập chứng từ, xác nhận để cập nhật kho, ghi nhận lịch sử, hủy hoặc hoàn theo quyền và tổng hợp Dashboard. Nhóm ưu tiên tính nhất quán của dữ liệu khi có thao tác đồng thời, thay vì chỉ hoàn thiện giao diện hiển thị.')
p('Báo cáo trình bày bài toán, yêu cầu, thiết kế dữ liệu, những phương thức xử lý quan trọng và kết quả kiểm thử. Phần Dashboard giải thích quy tắc tính doanh thu, giá vốn, thời điểm hoàn và cơ chế tự cập nhật, từ đó làm rõ ý nghĩa của số liệu khi trình diễn sản phẩm.')
h('Bố cục báo cáo')
for text in ['Chương 1 xác định phạm vi, tác nhân, yêu cầu và các tình huống sử dụng.', 'Chương 2 trình bày lựa chọn kiến trúc, quan hệ dữ liệu và ràng buộc nghiệp vụ.', 'Chương 3 phân tích cài đặt kho, chứng từ, truy vấn Dashboard và giao tiếp HTTP.', 'Chương 4 trình bày kiểm thử, giao diện, cách chạy và đánh giá mức độ hoàn thành.']: bullet(text)
h('Các thuật ngữ sử dụng')
table(['Thuật ngữ','Ý nghĩa trong đồ án'],[('MVT','Phân chia Model, View và Template của ứng dụng'),('ORM','Truy vấn và cập nhật các Model bằng giao diện của Django'),('SKU','Mã định danh sản phẩm, không trùng giữa các sản phẩm'),('Snapshot','Tập chỉ số đọc tại một lần lấy dữ liệu Dashboard'),('Polling','Trình duyệt định kỳ gửi yêu cầu lấy dữ liệu mới'),('Giá vốn ròng','Giá vốn bán trong kỳ trừ giá vốn hoàn trong kỳ')],[3.4,12.6])
'''

requirements=r'''
page('1.4  YÊU CẦU NGHIỆP VỤ VÀ PHÂN QUYỀN')
p('Các yêu cầu dưới đây được cụ thể hóa từ chức năng hiện có. Một thao tác hợp lệ cần thỏa mãn cả quyền của tác nhân, trạng thái chứng từ và các điều kiện dữ liệu; việc ẩn nút trên giao diện chỉ hỗ trợ sử dụng, không thay thế kiểm tra tại máy chủ. [3][4]')
p('Bảng 1.2  Ma trận quyền theo ba vai trò')
table(['Chức năng','Quản lý','Kho','Bán hàng'],[('Xem danh mục sản phẩm','Có','Có','Có'),('Tạo và sửa sản phẩm','Có','Không','Không'),('Nhà cung cấp và phiếu nhập','Có','Có','Không'),('Khách hàng và đơn bán','Có','Không','Có'),('Xem tồn và sổ kho','Có','Có','Không'),('Điều chỉnh tồn sau kiểm kê','Có','Không','Không'),('Hoàn chứng từ đã xác nhận','Có','Không','Không'),('Dashboard và tài khoản nhân viên','Có','Không','Không')],[8.2,2.6,2.6,2.6])
p('Nhân viên có thể hủy chứng từ nháp theo loại nghiệp vụ được cấp quyền. Quản lý có đầy đủ quyền; tài khoản superuser cũng được nhận diện là có quyền. Tài khoản không hoạt động không được chấp nhận bởi has_role.')
h('Các quy tắc nghiệp vụ chính')
table(['Mã','Quy tắc cần bảo đảm'],[('BR01','Mỗi chứng từ có 1–100 dòng; mỗi sản phẩm chỉ xuất hiện một lần; số lượng mỗi dòng từ 1 đến 1.000.000.'),('BR02','Phiếu nhập bắt buộc có nhà cung cấp; đơn bán có thể dùng khách lẻ. Giá bán lấy từ sản phẩm tại lúc lưu nháp.'),('BR03','Giảm giá không âm và không vượt tổng tiền hàng; phiếu nhập không áp dụng giảm giá.'),('BR04','Chỉ nháp được sửa; xác nhận mới ghi tồn và giá vốn. Không xác nhận lại chứng từ đã hủy hoặc hoàn.'),('BR05','Hoàn chỉ thực hiện toàn bộ, có lý do; phiếu nhập chỉ được hoàn nếu chưa có biến động tiếp theo trên sản phẩm.')],[2,14])
p('Tiêu chí nghiệm thu của nghiệp vụ kho là đối chiếu được Stock với Movement, trạng thái chứng từ phù hợp với biến động và các thao tác không làm tồn âm. Các giới hạn này giúp phạm vi đồ án rõ ràng, đồng thời tạo điều kiện kiểm thử tự động.')

page('1.5  TÁC NHÂN VÀ TÌNH HUỐNG SỬ DỤNG')
pic(ASSETS/'usecase.png','Hình 1.1  Sơ đồ ca sử dụng chính theo tác nhân',width=16)
p('Sơ đồ tập trung vào chức năng chính; quyền quản lý nhà cung cấp thuộc nghiệp vụ nhập và quyền quản lý khách hàng thuộc nghiệp vụ bán. Người dùng cần đăng nhập trước khi sử dụng các nhóm chức năng này.')
p('Bảng 1.3  Đặc tả ca sử dụng xác nhận đơn bán')
table(['Thành phần','Nội dung'],[('Tác nhân và điều kiện','Nhân viên bán hàng hoặc quản lý đã đăng nhập; đơn đang nháp và có ít nhất một dòng.'),('Luồng chính','Mở chi tiết → chọn xác nhận → kiểm tra quyền/trạng thái → khóa dữ liệu → xuất kho và ghi giá vốn → chuyển trạng thái → trả trang chi tiết.'),('Ngoại lệ','Thiếu tồn hoặc sản phẩm ngừng kinh doanh: báo lỗi, rollback toàn bộ; xác nhận lặp: trả chứng từ đã xác nhận.'),('Kết quả','Đơn có confirmed_at/confirmed_by; số lượng tồn giảm đúng; có Movement và giá vốn để báo cáo.')],[3.8,12.2])
p('Ca sử dụng theo dõi Dashboard: quản lý chọn ngày bắt đầu và kết thúc, nhận các chỉ số theo kỳ, sau đó trình duyệt tiếp tục lấy số liệu mới. Ngày sai hoặc khoảng quá dài bị từ chối; lỗi mạng chỉ thay đổi thông báo cập nhật, không xóa dữ liệu đang xem.')
'''

data=r'''
page('2.3  SƠ ĐỒ QUAN HỆ THỰC THỂ')
pic(ASSETS/'erd.png','Hình 2.3  Quan hệ giữa các bảng trong StoreDesk',width=16)
h('Các quyết định thiết kế')
p('Product và Stock tách riêng để phân biệt thông tin danh mục với trạng thái tồn thường xuyên thay đổi. Khi lưu sản phẩm, save_product đồng thời bảo đảm có một bản ghi Stock bằng get_or_create trong giao dịch. Quan hệ OneToOne ngăn tạo nhiều số dư cho cùng sản phẩm. [3][4]')
p('Document dùng chung cấu trúc cho nhập và bán vì hai nghiệp vụ đều gồm đối tác, dòng hàng, số tiền và vòng đời chứng từ. Trường kind phân biệt quy tắc xử lý, trong khi Line cho phép một chứng từ chứa nhiều sản phẩm mà không lặp các thông tin chung.')
p('Movement giữ lịch sử thay đổi có dấu; Stock cung cấp số dư hiện tại. Thiết kế này cho phép tra cứu tồn nhanh và truy lại nguyên nhân chênh lệch. Một biến động điều chỉnh không nhất thiết gắn Document nên khóa ngoại này được phép rỗng.')
p('User có nhiều quan hệ với Document theo vai trò người tạo, người xác nhận và người hoàn. Việc lưu riêng giúp xác định đúng người thực hiện từng bước; created_by không bị dùng thay cho toàn bộ lịch sử xử lý.')
h('Quản lý dữ liệu lịch sử')
p('Danh mục đang được tham chiếu được bảo vệ khỏi xóa bằng PROTECT. Sản phẩm và đối tác có cờ active để ngừng sử dụng trong nghiệp vụ mới. Thông tin tên và giá được chụp tại dòng chứng từ, do đó báo cáo cũ không tự đổi khi giá bán hiện tại thay đổi.')

page('2.4  RÀNG BUỘC VÀ VÒNG ĐỜI DỮ LIỆU')
p('Bảng 2.3  Các lớp kiểm tra dữ liệu tiêu biểu')
table(['Vị trí','Kiểm tra thực tế','Mục đích'],[('Form và FormSet','Kiểu trường, trường bắt buộc, dữ liệu từng dòng; form ngày kiểm tra thứ tự và độ dài kỳ','Phản hồi lỗi tại biểu mẫu trước khi gọi nghiệp vụ'),('Service','Quyền, loại đối tác, sản phẩm active, đủ tồn, giảm giá và trạng thái','Duy trì quy tắc khi service được gọi từ các View hoặc kiểm thử'),('Model và CSDL','SKU/request_key duy nhất; cặp document–product duy nhất; các CheckConstraint','Chặn dữ liệu vi phạm ở lớp lưu trữ'),('Giao dịch','atomic, select_for_update, khóa tư vấn theo yêu cầu','Không ghi dở dang hoặc xử lý trùng khi có yêu cầu đồng thời')],[3.1,7.8,5.1])
h('Vòng đời chứng từ')
code('draft ── xác nhận ──> confirmed ── hoàn toàn bộ ──> reversed\n  └──── hủy nháp ──> cancelled\nconfirmed, cancelled, reversed: không cho sửa nháp')
p('Hình 2.4  Các chuyển trạng thái được phép',False,C)
p('Không có trạng thái giao hàng hoặc công nợ riêng. Nút xác nhận bán đồng thời thể hiện đã thu tiền theo phương thức người dùng chọn; ứng dụng chưa kiểm chứng giao dịch ngân hàng. Vì vậy số đã thu trên Dashboard được hiểu theo dữ liệu ghi nhận nội bộ.')
h('Bảo toàn số liệu và truy vết')
p('Stock.value là giá trị theo giá vốn, không phải số lượng nhân giá bán. Line.cost giữ giá vốn của lần xuất; khi hoàn bán, hệ thống dùng chính giá vốn đã lưu để đảo lại thay vì tính theo giá bình quân hiện tại. Cách này giữ liên hệ giữa giao dịch bán và giao dịch hoàn.')
p('Các mốc confirmed_at, reversed_at có chỉ mục để hỗ trợ truy vấn theo kỳ. Document.status có chỉ mục phục vụ lọc trạng thái. Chưa có số liệu đo tải để khẳng định mức tăng tốc; khi mở rộng cần đo truy vấn thực tế trước khi thêm chỉ mục ghép hoặc bảng tổng hợp.')
p('Không chỉnh trực tiếp số dư Stock từ giao diện danh mục. Thay đổi tồn phải đi qua service nhập, bán, hoàn hoặc điều chỉnh để vừa cập nhật số dư vừa ghi Movement. Lệnh check_business_data dùng để đối chiếu tính nhất quán của dữ liệu nghiệp vụ.')
'''

sequence=r'''
page('3.2.1  TRÌNH TỰ XÁC NHẬN VÀ XỬ LÝ LỖI')
pic(ASSETS/'sequence.png','Hình 3.1  Trình tự xác nhận và làm mới Dashboard',width=16)
p('Sơ đồ thể hiện trường hợp xác nhận thành công. Dashboard dùng một yêu cầu HTTP riêng; giao dịch cập nhật chứng từ không trực tiếp gửi dữ liệu đến trình duyệt Dashboard. Người dùng xem kết quả mới ở lần polling sau khi giao dịch đã commit.')
h('Nhánh lỗi và xử lý đồng thời')
p('Nếu một sản phẩm không đủ tồn, BusinessError thoát khỏi hàm có transaction.atomic. Những thay đổi Stock, Movement và Line trước đó trong cùng lần xác nhận bị rollback. View nhận lỗi nghiệp vụ, hiển thị thông báo và chuyển về trang chi tiết; chứng từ vẫn là nháp.')
p('Khóa Document giải quyết hai yêu cầu cùng xác nhận một chứng từ. Khóa Stock giải quyết các chứng từ khác nhau cùng bán một sản phẩm. Hai loại khóa phục vụ hai nguy cơ khác nhau, vì vậy chỉ kiểm tra trạng thái đơn mà không khóa tồn là chưa đủ.')
p('Ví dụ kiểm thử đồng thời: kho còn 5, hai đơn đều mua 4. Giao dịch giữ khóa trước xác nhận và để tồn 1; giao dịch sau đọc lại tồn khi được cấp khóa, phát hiện thiếu và bị từ chối. Trường hợp bấm xác nhận hai lần cùng phiếu nhập chỉ tạo một Movement. [7]')
p('Khóa các sản phẩm theo cùng thứ tự product_id làm giảm nguy cơ chờ khóa vòng giữa các chứng từ nhiều dòng; báo cáo không khẳng định loại bỏ mọi tình huống deadlock. Cơ chế này được lựa chọn phù hợp với PostgreSQL đang dùng.')
'''

js=r'''
page('3.5  CƠ CHẾ TỰ CẬP NHẬT VÀ HIỂN THỊ')
p('Trích nguyên văn đoạn đầu của refresh trong src/static/js/dashboard.js. Phần còn lại của hàm xử lý lỗi, cập nhật thông báo và đặt lại inFlight trong finally. [5]')
js_source=(ROOT/'src/static/js/dashboard.js').read_text(encoding='utf-8')
start=js_source.index('  async function refresh()')
end=js_source.index('    } catch (_)',start)
code(js_source[start:end].rstrip())
p('Dòng 1 khai báo hàm bất đồng bộ. Dòng 2 dừng nếu có yêu cầu đang chạy hoặc tab đang ẩn. Dòng 3 đánh dấu đang tải. Dòng 4 mở khối bắt lỗi; dòng 5 gửi GET kèm bộ lọc hiện tại, yêu cầu JSON, timeout 8 giây và không dùng cache trình duyệt. Dòng 6 kiểm tra lỗi HTTP hoặc chuyển hướng đăng nhập; dòng 7 đọc JSON rồi render.')
p('setInterval(refresh, 10000) đặt chu kỳ 10 giây; visibilitychange gọi lại ngay khi tab hiện. Nếu mạng lỗi, thông báo cho biết đang giữ dữ liệu cũ. Đây là cơ chế gần thời gian thực, không bảo đảm thay đổi xuất hiện tức thì hoặc trong một độ trễ cố định khi mạng chậm.')
h('Biểu đồ và cấu trúc dữ liệu trả về')
p('Bảng 3.3  Các nhóm dữ liệu Dashboard trả về trình duyệt')
table(['Nhóm dữ liệu JSON','Cách giao diện sử dụng'],[('revenue, profit, collected, refunds','Cập nhật thẻ chỉ số; định dạng tiền theo vi-VN'),('daily: date, label, revenue','Dựng SVG đường và vùng; đồng thời dựng bảng số liệu từng ngày'),('top: name, units','Dựng thanh xếp hạng theo số lượng bán ròng'),('stock_units, stock_value, low_count, low_stock','Hiển thị tồn hiện tại và danh sách cần nhập thêm'),('recent và updated_at','Dựng liên kết đơn gần đây và thời điểm cập nhật')],[7,9])
p('SVG tính trục tung theo cả giá trị âm và dương, nên có thể biểu diễn ngày hoàn tiền vượt doanh thu. Ngày không bán vẫn được trả về với giá trị 0. Dữ liệu khởi tạo được đọc từ trang, sau đó dùng cùng render để cập nhật; không cần tải lại toàn bộ trang.')
p('Giới hạn: mỗi lượt cập nhật vẫn chạy lại truy vấn và dựng lại phần hiển thị. Chưa có cache, push hoặc tổng hợp tiền tính sẵn. Khi số người xem hoặc dữ liệu tăng, cần đo chi phí truy vấn và lưu lượng trước khi điều chỉnh kiến trúc.')
'''

tests=r'''
page('4.2  BẢNG KIỂM THỬ CHI TIẾT')
p('Bảng dưới đây rút gọn các kiểm thử đã có trong mã nguồn, không tạo số liệu đánh giá giả định. Cột kết quả ghi Đạt vì các hàm kiểm thử tương ứng nằm trong lần chạy 60 passed tại mục 4.1. [7]')
p('Bảng 4.2  Đầu vào và kết quả các ca kiểm thử tiêu biểu')
table(['Mã','Đầu vào hoặc thao tác','Kỳ vọng và kết quả đối chiếu'],[('TC01','Nhập 10 giá 20.000; bán 3 giá 50.000, giảm 10.000; xác nhận lặp','Đạt: đơn 140.000; tồn 7, giá trị 140.000; giá vốn 60.000; tổng 2 Movement.'),('TC02','Đơn gồm 2 dòng; dòng thứ hai không đủ hàng','Đạt: đơn vẫn nháp, cost=0; tồn dòng đầu không đổi; không có xuất kho dở dang.'),('TC03','Hai đơn cùng mua 4 khi tồn 5','Đạt: một confirmed, một rejected; tồn cuối 1; chỉ một đơn bán xác nhận.'),('TC04','Nhập 10×10.000 và 10×30.000; bán 5 rồi hoàn','Đạt: giá vốn bán 100.000; sau hoàn tồn 20, giá trị 400.000.'),('TC05','Bán 90.000 hôm trước; hoàn toàn bộ hôm nay','Đạt: hôm trước 90.000, hôm nay −90.000; tổng kỳ và lợi nhuận bằng 0.'),('TC06','Chỉ có đơn nháp trong kỳ','Đạt: doanh thu=0, orders=0; sản phẩm chưa có tồn thuộc cảnh báo thấp.'),('TC07','Bán hàng truy cập Dashboard; kho truy cập đơn bán','Đạt: HTTP 403 ở các đường dẫn sai quyền.'),('TC08','POST tạo sản phẩm thiếu CSRF bằng client bật kiểm tra CSRF','Đạt: HTTP 403; chưa có yêu cầu hợp lệ để ghi sản phẩm.'),('TC09','Lọc ngày sai định dạng, đảo thứ tự hoặc khoảng quá dài','Đạt: /dashboard/data/ trả 400; trang Dashboard vẫn trả trang biểu mẫu.'),('TC10','Cố ý đổi Stock.quantity và Document.total sai trong CSDL test','Đạt: check_business_data trả ok=False, phát hiện lỗi Stock và tổng tiền.')],[1.5,6.2,8.3])
h('Phạm vi kiểm chứng')
p('Bộ kiểm thử còn bao gồm form tạo chứng từ, chống trùng request_key, giá chụp tại lúc lưu, render các trang quản lý và escape nội dung HTML. Test dùng Django client kiểm tra HTTP không đồng nghĩa đã chạy trình duyệt đầy đủ; hành vi SVG, responsive và độ trễ thực tế cần kiểm tra trực tiếp.')
p('TODO: ghi trình duyệt và kích thước màn hình đã kiểm tra, kết quả sử dụng trên điện thoại và log đo tải nếu thực hiện. Chưa có số liệu coverage được đo trong báo cáo, nên không suy ra tỉ lệ bao phủ từ số ca kiểm thử.')
'''

screens=r'''
page('4.4  GIAO DIỆN DANH MỤC SẢN PHẨM')
pic(ROOT/'docs/screenshots/products.png','Hình 4.2  Danh mục sản phẩm',maxheight=11)
p('Danh mục hỗ trợ tìm theo SKU, tên hoặc danh mục; hiển thị thông tin bán hàng và tồn liên quan. Quản lý có quyền thêm/sửa; nhân viên kho và bán hàng có thể xem. Mỗi SKU là duy nhất và sản phẩm có trạng thái đang kinh doanh để kiểm soát các giao dịch mới.')
h('Quy trình sử dụng')
p('Quản lý thêm SKU, tên, danh mục, đơn vị, giá bán và ngưỡng cảnh báo. Sau khi lưu, hệ thống tạo bản ghi Stock nếu chưa có. Người dùng tìm theo từ khóa để đối chiếu danh mục; việc đổi giá bán chỉ ảnh hưởng những dòng chứng từ được lưu sau đó, không tự cập nhật các dòng cũ.')
p('Giá bán không được âm; SKU không trùng. Khi ngừng kinh doanh một sản phẩm, quản lý tắt trạng thái active. Service xác nhận còn kiểm tra trạng thái sản phẩm để ngăn xác nhận một nháp chứa sản phẩm đã ngừng kinh doanh.')
page('4.5  GIAO DIỆN TỒN KHO VÀ CẢNH BÁO')
pic(ROOT/'docs/screenshots/stock.png','Hình 4.3  Tồn kho hiện tại và cảnh báo',maxheight=11)
p('Trang tồn kho cho phép tìm sản phẩm và lọc tồn thấp. Số lượng và giá trị tồn được cập nhật sau xác nhận chứng từ; điều chỉnh kiểm kê yêu cầu quản lý nhập chênh lệch và lý do. Sổ kho là nơi tra cứu biến động theo sản phẩm, chứng từ và người thực hiện.')
p('Ví dụ kiểm tra: khi tồn bằng đúng ngưỡng cảnh báo, sản phẩm đã thuộc nhóm tồn thấp vì điều kiện là nhỏ hơn hoặc bằng. Sản phẩm ngừng kinh doanh không được tính trong danh sách cảnh báo; tổng tồn vẫn đọc số dư hiện tại của Stock.')
p('Các ảnh trong mục 4.3–4.8 được lấy từ thư mục docs/screenshots của dự án, ghi nhận ngày 07/11/2026. Chúng minh họa giao diện có sẵn và không thay thế bằng chứng kiểm thử tương tác trên trình duyệt. [8]')

page('4.6  GIAO DIỆN NHẬP HÀNG')
pic(ROOT/'docs/screenshots/purchases.png','Hình 4.4  Danh sách phiếu nhập',maxheight=11)
p('Phiếu nhập được quản lý theo mã và trạng thái. Nhân viên kho chọn nhà cung cấp, nhập các dòng hàng và đơn giá rồi lưu nháp. Chỉ khi xác nhận hệ thống mới cộng tồn và ghi sổ; phiếu đã xác nhận không được sửa trực tiếp.')
h('Điểm kiểm soát trên phiếu nhập')
p('Nhà cung cấp là bắt buộc và phải thuộc đúng loại supplier đang hoạt động. Đơn giá nhập được nhập theo từng dòng; giá trị nhập làm tăng Stock.value và ảnh hưởng giá vốn bình quân của lần xuất sau. Phiếu nhập không có giảm giá trong phạm vi hiện tại.')
p('Khi phát hiện nhập nhầm trước xác nhận, người dùng sửa hoặc hủy nháp. Sau xác nhận, quản lý chỉ được hoàn toàn bộ nếu các sản phẩm chưa có biến động tiếp theo. Quy tắc này tránh đảo một khoản nhập đã được dùng làm cơ sở cho giá vốn của giao dịch sau.')
page('4.7  GIAO DIỆN BÁN HÀNG')
pic(ROOT/'docs/screenshots/sales.png','Hình 4.5  Danh sách đơn bán',maxheight=17)
p('Đơn bán dùng giá sản phẩm khi lưu nháp, cho phép giảm giá trong giới hạn tổng hàng và ghi phương thức thanh toán. Trang chi tiết hiển thị dòng hàng, tổng tiền và thao tác theo trạng thái. Hủy nháp không ảnh hưởng kho; hoàn đơn đã xác nhận đảo toàn bộ tồn và số tiền được ghi nhận.')
p('Mã chứng từ có dạng PN hoặc BH kèm số định danh. Danh sách có tìm kiếm, lọc trạng thái và phân trang. Chức năng này phục vụ bán hàng nội bộ, chưa phải quy trình khách tự mua hàng và phát hành hóa đơn điện tử.')

page('4.8  TÀI KHOẢN VÀ ĐÁNH GIÁ MỨC ĐỘ HOÀN THÀNH')
pic(ROOT/'docs/screenshots/staff.png','Hình 4.6  Quản lý tài khoản nhân viên',maxheight=8)
p('Quản lý tạo tài khoản kèm vai trò nghiệp vụ. Khi truy cập trang chủ, hệ thống đưa quản lý đến Dashboard, nhân viên kho đến tồn kho và nhân viên bán hàng đến đơn bán. Quyền còn được kiểm tra khi gọi trực tiếp URL hoặc service, tránh phụ thuộc vào menu hiển thị.')
p('Bảng 4.3  Đối chiếu phạm vi đề tài và sản phẩm')
table(['Yêu cầu','Mức độ hoàn thành thực tế'],[('Nhập, xuất và cảnh báo tồn thấp','Đã có; xuất bán gắn với xác nhận đơn, cảnh báo theo ngưỡng từng sản phẩm.'),('Kiểm kê','Có điều chỉnh chênh lệch có lý do và sổ kho; chưa có phiếu kiểm kê và bước duyệt riêng.'),('Đơn hàng và tự trừ kho','Đã có đơn nhiều dòng, chiết khấu, xác nhận, hủy/hoàn; chưa có giỏ hàng công khai.'),('Dashboard tự cập nhật','Đã có JSON polling 10 giây; chưa có WebSocket/Channels.'),('Ngày, tuần, tháng và bán chạy','Có chọn khoảng ngày, chuỗi theo ngày và tối đa 6 sản phẩm; chưa nhóm theo tuần/tháng, chưa đúng top 5 nếu yêu cầu bắt buộc.'),('Tỉ lệ đơn thành công/hủy','Chưa có; có số đơn xác nhận và số hoàn, không thay thế cho tỉ lệ trạng thái.')],[5,11])
p('Đánh giá chung: sản phẩm đã thể hiện quy trình nghiệp vụ liên thông và cơ chế phân tích dữ liệu. Một số tiêu chí trong định hướng ban đầu chưa triển khai đầy đủ; nhóm cần trình bày rõ giới hạn và hướng bổ sung thay vì đồng nhất các chức năng gần giống nhau.')

page('4.9  CÀI ĐẶT VÀ BÀN GIAO SẢN PHẨM')
h('Chuẩn bị và chạy ứng dụng')
p('Bảng 4.4  Các bước chạy và kiểm tra khi bàn giao')
table(['Bước','Thao tác và kết quả cần kiểm tra'],[('1. Chuẩn bị','Python 3.12+ và PostgreSQL 15+ có initdb, pg_ctl; máy chạy cần cài thư viện theo requirements.'),('2. Khởi động','Tại thư mục gốc chạy python run.py; launcher tạo môi trường, chuẩn bị CSDL và áp dụng migrations.'),('3. Truy cập','Mở http://127.0.0.1:8010/; lần đầu tạo quản lý; sau đó thêm sản phẩm, đối tác và nhân viên.'),('4. Dữ liệu trình diễn','Dùng dữ liệu đã sao lưu hoặc seed_demo trên CSDL trống; không giả định số liệu seed trùng ảnh minh họa hiện tại.'),('5. Đối soát','Chạy manage.py check_business_data trong môi trường dự án; xem kết quả trước khi bàn giao.'),('6. Kết thúc','Ctrl+C dừng web; python run.py --stop-db dừng PostgreSQL cục bộ khi cần.')],[3.3,12.7])
h('Sao lưu và chuyển máy')
p('README hướng dẫn sao lưu bằng pg_dump và khôi phục bằng pg_restore vào CSDL trống. Không sao chép trực tiếp thư mục dữ liệu PostgreSQL khi máy chủ đang chạy. Mã nguồn nộp không bao gồm .venv, .git, mật khẩu hoặc toàn bộ var/postgres; bản sao lưu dữ liệu minh họa được gửi riêng nếu cần. [1]')
p('TODO: xác nhận vị trí bản backup nộp cuối, phiên bản PostgreSQL, cấu hình máy và hướng dẫn khôi phục đã thử trên máy nhận. Các thông tin đăng nhập được trao đổi riêng, không đưa vào báo cáo in.')
h('Kịch bản trình diễn khi bảo vệ')
p('Trình bày theo một luồng xuyên suốt: quản lý tạo danh mục → kho xác nhận nhập 10 → bán hàng xác nhận bán 3 → đối chiếu tồn 7 và sổ kho → quản lý xem Dashboard cập nhật → thử bán quá tồn → hoàn đơn và kiểm tra số liệu. Dùng một sản phẩm mới không có tồn để số lượng dễ theo dõi.')
p('Cần giải thích được ba điểm: lý do khóa cả chứng từ và tồn; sự khác nhau giữa hủy nháp và hoàn; doanh thu tính theo ngày bán/ngày hoàn trong khi tồn luôn là hiện tại. Khi mạng chậm hoặc tab bị ẩn, dựa vào thông báo cập nhật thay vì cam kết một độ trễ cố định.')
'''

src=(ROOT/'docs/report_build.py').read_text(encoding='utf-8')
src=src.replace("OUT = ROOT / 'docs' / 'Bao_cao_Python_StoreDesk_PTIT.docx'", "OUT = ROOT / 'docs' / 'Bao_cao_Python_StoreDesk_PTIT_Hoan_chinh.docx'")
# Use a fixed source location even when this builder is run outside the repository.
src=src.replace("ROOT = Path(__file__).resolve().parents[1]",f"ROOT = Path({str(ROOT)!r})\nASSETS=ROOT/'var/report_full_qa'")
helper='''
def pic(path, caption, width=15.5, maxheight=None):
    from PIL import Image
    with Image.open(path) as image:
        ratio=image.height/image.width
    if maxheight: width=min(width,maxheight/ratio)
    doc.add_picture(str(path),width=Cm(width))
    doc.paragraphs[-1].alignment=C
    cap=p(caption,False,C)
    cap.paragraph_format.space_after=Pt(7)
'''
src=src.replace("p('HỌC VIỆN CÔNG NGHỆ",helper+"\np('HỌC VIỆN CÔNG NGHỆ",1)
src=src.replace("page('THÔNG TIN NHÓM VÀ MỤC LỤC')",intro+"\npage('THÔNG TIN NHÓM VÀ MỤC LỤC')")
src=src.replace("page('CHƯƠNG 2  KIẾN TRÚC VÀ THIẾT KẾ DỮ LIỆU')",requirements+"\npage('CHƯƠNG 2  KIẾN TRÚC VÀ THIẾT KẾ DỮ LIỆU')")
src=src.replace("page('CHƯƠNG 3  CÀI ĐẶT NGHIỆP VỤ VÀ DASHBOARD')",data+"\npage('CHƯƠNG 3  CÀI ĐẶT NGHIỆP VỤ VÀ DASHBOARD')")
src=src.replace("page('3.3  THIẾT KẾ DASHBOARD VÀ LUỒNG DỮ LIỆU')",sequence+"\npage('3.3  THIẾT KẾ DASHBOARD VÀ LUỒNG DỮ LIỆU')")
src=src.replace("page('CHƯƠNG 4  KIỂM THỬ VÀ KẾT QUẢ THỰC HIỆN')",js+"\npage('CHƯƠNG 4  KIỂM THỬ VÀ KẾT QUẢ THỰC HIỆN')")
src=src.replace("page('4.3  GIAO DIỆN VÀ KẾT QUẢ MINH HỌA')",tests+"\npage('4.3  GIAO DIỆN VÀ KẾT QUẢ MINH HỌA')")
src=src.replace("page('KẾT LUẬN VÀ TÀI LIỆU THAM KHẢO')",screens+"\npage('KẾT LUẬN VÀ TÀI LIỆU THAM KHẢO')")
src=src.replace('........................................ 3','........................................ 4').replace('........................................... 4','........................................... 7').replace('............................. 6','............................. 11').replace('....................................... 9','....................................... 16').replace('...................................................... 11','...................................................... 25')
src=src.replace('Phân công đề xuất với khối lượng tương đương, mỗi thành viên khoảng 1/6 tổng công việc. Nhóm xác nhận lại theo đóng góp thực tế trước khi nộp.','Phương án phân công theo sáu nhóm công việc, khối lượng dự kiến tương đương nhau. TODO: xác nhận phân công và mức đóng góp thực tế của từng thành viên.')
src=src.replace("h('4.2  Cách chạy và kịch bản trình diễn')", "h('4.1.1  Cách chạy và kịch bản trình diễn')")
src=src.replace('Các bảng và hình được đánh số trong từng chương. TODO: đối chiếu mẫu bìa, quy định trình bày của giảng viên và cập nhật mục lục nếu chỉnh sửa nội dung.','TODO: hoàn thiện thông tin nhóm và đối chiếu mẫu trình bày riêng của giảng viên; cập nhật số trang mục lục sau khi chỉnh sửa bản nộp.')
src=src.replace('[8] docs/README.md; docs/screenshots/dashboard.png. Ảnh giao diện và dữ liệu minh họa.','[8] docs/README.md; docs/screenshots gồm dashboard, products, stock, purchases, sales, staff. Ảnh giao diện và dữ liệu minh họa.')
exec(compile(src,str(ROOT/'docs/report_build.py'),'exec'))
