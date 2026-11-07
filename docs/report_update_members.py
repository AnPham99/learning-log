from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'docs/Bao_cao_Python_StoreDesk_PTIT_HCM.docx'
doc=Document(PATH)
members=[
    ('Phạm Tuấn Ân','K25DTCN090',1,'Nghiệp vụ chứng từ và xử lý đồng thời: lưu nháp, xác nhận, hủy/hoàn; transaction, khóa dữ liệu, chống xử lý trùng và tích hợp luồng nhập–bán. Phụ trách mục 3.2 và sơ đồ trình tự.'),
    ('Hoàng Ngọc Đạt','K25DTCN092',4,'Tài khoản, phân quyền và danh mục: đăng nhập, nhóm quyền, sản phẩm, khách hàng, nhà cung cấp; kiểm tra đầu vào và quyền truy cập. Phụ trách yêu cầu nghiệp vụ, ma trận quyền và các View liên quan.'),
    ('Nguyễn Thị Ngọc Huyền','K25DTCN095',3,'Dashboard: truy vấn ORM, doanh thu và hoàn tiền theo kỳ, lợi nhuận gộp, sản phẩm bán chạy; JSON, biểu đồ SVG và cập nhật định kỳ. Phụ trách mục 3.3–3.5 và đối chiếu chỉ số.'),
    ('Đinh Công Nhiên','K25DTCN099',6,'Kiểm thử và tài liệu: chạy bộ kiểm thử hiện có, ghi nhận kết quả, kiểm tra giao diện theo kịch bản, chụp ảnh, tổng hợp báo cáo và hướng dẫn cài đặt/bàn giao. Phụ trách chương 4 và tài liệu trình bày.'),
    ('Đào Văn Quyết','K25DTCN103',2,'Kho và thiết kế dữ liệu: Model, quan hệ ER/UML, ràng buộc CSDL; số lượng và giá trị tồn, giá vốn bình quân, điều chỉnh và sổ kho; phối hợp kiểm tra đảo kho khi hoàn. Phụ trách mục 2.2–2.5 và 3.1.'),
    ('Nguyễn Quốc Tuấn','B25DTCN014',5,'Giao diện và tương tác: templates, CSS, bố cục responsive, menu, tìm kiếm/phân trang, thêm/xóa dòng chứng từ và thông báo lỗi. Phối hợp tích hợp giao diện các mô-đun, kiểm tra thao tác người dùng.'),
]
for p in doc.paragraphs:
    if p.text.startswith('Phương án phân công theo sáu nhóm công việc'):
        p.text='Nhiệm vụ được phân công theo mức độ khó giảm dần: hạng 1 khó nhất, hạng 6 nhẹ nhất. Mỗi thành viên chịu trách nhiệm phần việc được giao, phối hợp tích hợp và tham gia bảo vệ đồ án.'
    if p.text.startswith('Mỗi thành viên tự kiểm thử mô-đun'):
        p.text='Mỗi thành viên kiểm thử phần phụ trách và rà soát chéo. Phạm Tuấn Ân tích hợp luồng nghiệp vụ; Đinh Công Nhiên tổng hợp minh chứng và định dạng báo cáo. Cả nhóm tham gia trình bày và trả lời câu hỏi về phần việc của mình.'

old=next(t for t in doc.tables if 'Thành viên' in t.cell(0,0).text)
t=doc.add_table(rows=1,cols=4)
t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
widths=[3.5,2.8,8,1.2]
for col,w in zip(t.columns,widths): col.width=Cm(w)
for c,txt in zip(t.rows[0].cells,['Thành viên','Mã sinh viên','Nhiệm vụ và sản phẩm phụ trách','Độ khó']): c.text=txt
for name,student_id,rank,task in members:
    cells=t.add_row().cells
    for c,txt in zip(cells,[name,student_id,task,str(rank)]): c.text=txt
for ri,row in enumerate(t.rows):
    rp=row._tr.get_or_add_trPr()
    rp.append(OxmlElement('w:cantSplit'))
    if ri==0: rp.append(OxmlElement('w:tblHeader'))
    for ci,(cell,w) in enumerate(zip(row.cells,widths)):
        cell.width=Cm(w); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        cp=cell._tc.get_or_add_tcPr()
        borders=OxmlElement('w:tcBorders')
        for edge in ['top','left','bottom','right']:
            el=OxmlElement('w:'+edge)
            for k,v in [('val','single'),('sz','4'),('color','D9D9D9')]: el.set(qn('w:'+k),v)
            borders.append(el)
        cp.append(borders)
        margins=OxmlElement('w:tcMar')
        for edge in ['top','left','bottom','right']:
            el=OxmlElement('w:'+edge); el.set(qn('w:w'),'70'); el.set(qn('w:type'),'dxa'); margins.append(el)
        cp.append(margins)
        if ri==0:
            fill=OxmlElement('w:shd'); fill.set(qn('w:fill'),'E7E6E6'); cp.append(fill)
        for p in cell.paragraphs:
            pf=p.paragraph_format; pf.first_line_indent=Cm(0); pf.left_indent=Cm(0)
            pf.line_spacing=1.1; pf.space_before=Pt(0); pf.space_after=Pt(2)
            pf.keep_with_next=ri==0
            p.alignment=WD_ALIGN_PARAGRAPH.CENTER if ci==3 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs: run.font.name='Times New Roman'; run.font.size=Pt(11); run.bold=ri==0
old._tbl.getparent().replace(old._tbl,t._tbl)
doc.core_properties.author='; '.join(m[0] for m in members)
doc.save(PATH)
assert len(t.rows)==7
assert [t.cell(i,3).text for i in range(1,7)]==['1','4','3','6','2','5']
print(PATH)
