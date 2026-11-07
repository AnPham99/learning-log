from pathlib import Path
from copy import deepcopy
from docx import Document
from docx.shared import Cm, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/Bao_cao_Python_StoreDesk_PTIT_HCM_Dinh_dang.docx'
OUT=ROOT/'docs/Bao_cao_Python_StoreDesk_PTIT_HCM.docx'
doc=Document(SOURCE)

def locate(prefix):
    return next(p for p in doc.paragraphs if p.text.startswith(prefix) and not p.style.name.lower().startswith('toc'))

def put(anchor,text,style='Normal'):
    p=anchor.insert_paragraph_before(text,style)
    pf=p.paragraph_format
    pf.space_after=Pt(3); pf.first_line_indent=Cm(1)
    pf.line_spacing=1.5; pf.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    if style.startswith('Heading'):
        pf.first_line_indent=Cm(0); pf.line_spacing=1.2
        pf.keep_with_next=True; pf.space_before=Pt(12); pf.space_after=Pt(6)
    return p

# Replace the existing use-case drawing with the user's original PNG.
cap=locate('Hình 1.1')
pic_para=cap._p.getprevious()
pic_para.getparent().remove(pic_para)
pp=cap.insert_paragraph_before()
pp.alignment=WD_ALIGN_PARAGRAPH.CENTER
pp.paragraph_format.first_line_indent=Cm(0); pp.paragraph_format.line_spacing=1
pp.paragraph_format.keep_with_next=True
pp.add_run().add_picture(str(ROOT/'docs/diagrams/UseCase.png'),width=Cm(15))
cap.text='Hình 1.1  Sơ đồ Use Case các nghiệp vụ chính'
locate('Sơ đồ tập trung vào chức năng chính').text=(
    'Hình 1.1 gồm bốn ca sử dụng: nhập, bán, hoàn đơn và xem Dashboard. Quản lý tham gia cả bốn; '
    'nhân viên kho tham gia nhập, nhân viên bán hàng tham gia bán. Hoàn chứng từ đã xác nhận chỉ dành cho quản lý. Các quyền khác xem Bảng 1.2. [9]')

# Replace the old ER subsection, then insert the class diagram as its own subsection.
start=locate('2.3  SƠ ĐỒ QUAN HỆ THỰC THỂ')
anchor=locate('2.4  RÀNG BUỘC VÀ VÒNG ĐỜI DỮ LIỆU')
node=start._p
while node is not anchor._p:
    nxt=node.getnext(); node.getparent().remove(node); node=nxt
anchor.text='2.5  RÀNG BUỘC VÀ VÒNG ĐỜI DỮ LIỆU'

# Section properties describe the section ending at the corresponding paragraph.
main_end=doc._element.body.sectPr
portrait=deepcopy(main_end)
first_main_section=True
def section_break(anchor,landscape=False):
    global first_main_section
    p=anchor.insert_paragraph_before()
    pf=p.paragraph_format
    pf.space_before=Pt(0); pf.space_after=Pt(0); pf.line_spacing=1
    for r in p.runs: r.font.size=Pt(1)
    sec=deepcopy(portrait)
    num=sec.find(qn('w:pgNumType'))
    if num is not None and not first_main_section: num.attrib.pop(qn('w:start'),None)
    first_main_section=False
    typ=sec.find(qn('w:type'))
    if typ is None: typ=OxmlElement('w:type'); sec.insert(0,typ)
    typ.set(qn('w:val'),'nextPage')
    if landscape:
        size=sec.find(qn('w:pgSz'))
        size.set(qn('w:w'),str(int(Cm(29.7).twips))); size.set(qn('w:h'),str(int(Cm(21).twips)))
        size.set(qn('w:orient'),'landscape')
        mar=sec.find(qn('w:pgMar'))
        for side in ['top','bottom']: mar.set(qn('w:'+side),str(int(Cm(1.1).twips)))
        mar.set(qn('w:header'),str(int(Cm(.4).twips)))
        mar.set(qn('w:footer'),str(int(Cm(.6).twips)))
    p._p.get_or_add_pPr().append(sec)
    return p

def full_diagram(anchor,title,filename,caption):
    p=put(anchor,title,'Heading 2')
    p.paragraph_format.space_before=Pt(0); p.paragraph_format.space_after=Pt(4)
    p.paragraph_format.page_break_before=False
    p=anchor.insert_paragraph_before()
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent=Cm(0); p.paragraph_format.line_spacing=1
    p.paragraph_format.space_after=Pt(0); p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(str(ROOT/'docs/diagrams'/filename),width=Cm(24))
    p=put(anchor,caption,'Figure Caption')
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.first_line_indent=Cm(0)
    p.paragraph_format.line_spacing=1; p.paragraph_format.space_before=Pt(0)
    p.paragraph_format.space_after=Pt(0)

put(anchor,'Hình 2.2 và Hình 2.3 mô tả cùng sáu thực thể nghiệp vụ ở hai góc nhìn: quan hệ dữ liệu và cấu trúc lớp. Các sơ đồ lược bỏ User/Group và một số trường kỹ thuật; danh sách trường, kiểu dữ liệu và ràng buộc được đối chiếu với Bảng 2.2. [3][9]')
section_break(anchor)
full_diagram(anchor,'2.3  SƠ ĐỒ QUAN HỆ THỰC THỂ','ER.png','Hình 2.2  Sơ đồ ER các thực thể nghiệp vụ theo ký pháp Chen')
section_break(anchor,landscape=True)
full_diagram(anchor,'2.4  SƠ ĐỒ LỚP UML','UML.png','Hình 2.3  Sơ đồ lớp UML các Model nghiệp vụ')
section_break(anchor,landscape=True)
num=main_end.find(qn('w:pgNumType'))
if num is not None: num.attrib.pop(qn('w:start'),None)

put(anchor,'ER thể hiện quan hệ giữa sáu thực thể. Stock tách khỏi Product để phân biệt danh mục với số dư; Document dùng chung cho nhập và bán, phân biệt bằng kind. Movement có thể không gắn Document khi điều chỉnh kho. [3][9]')
put(anchor,'UML bổ sung thuộc tính và phương thức Model: Product/Contact có __str__, Document có code, Line có subtotal. Các lớp kế thừa models.Model; xử lý xác nhận, hoàn và điều chỉnh nằm trong service. User/Group và một số trường kỹ thuật được lược bỏ. [3][4][9]')
put(anchor,'Bội số CSDL cho phép Document có 0..* Line và Product tối đa một Stock. Nghiệp vụ yêu cầu chứng từ có 1–100 dòng, tự tạo Stock khi lưu sản phẩm và không lặp sản phẩm trong chứng từ. Hai lớp ràng buộc này cần được phân biệt khi đọc sơ đồ.')

for p in doc.paragraphs:
    if p.text.startswith('Các mốc confirmed_at, reversed_at có chỉ mục') or p.text=='Bảo toàn số liệu và truy vết' or p.text.startswith('Stock.value là giá trị theo giá vốn'):
        p._element.getparent().remove(p._element); continue
    if p.text.startswith('Hình 2.3  Các chuyển trạng thái'):
        p.text='Hình 2.4  Các chuyển trạng thái được phép'
    if p.style.name=='Figure Caption':
        for r in p.runs: r.bold=False; r.font.size=Pt(12)
    if p.text.startswith('Chương 2 trình bày lựa chọn kiến trúc'):
        p.text='• Chương 2 trình bày kiến trúc, thiết kế dữ liệu, sơ đồ ER và sơ đồ lớp UML.'

# Include the diagram files in the traceable report sources.
p=doc.add_paragraph('[9] docs/diagrams/UseCase.png; ER.png; UML.png. Sơ đồ Use Case, ER và lớp UML của StoreDesk.','Normal')
p.paragraph_format.left_indent=Cm(.8); p.paragraph_format.first_line_indent=Cm(-.8)
p.paragraph_format.line_spacing=1.2; p.paragraph_format.space_after=Pt(3)
for r in p.runs: r.font.size=Pt(12)
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            if 'Sản phẩm, đối tác, ràng buộc; mục 2.2' in cell.text:
                for p in cell.paragraphs:
                    p.text=p.text.replace('mục 2.2','mục 2.2–2.5')
                    for r in p.runs: r.font.size=Pt(11)

# Keep the current automatic TOCs; Word updates their cached text and page numbers.
doc.save(OUT)
print(OUT)
