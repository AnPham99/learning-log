from pathlib import Path
from copy import deepcopy
import re
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/Bao_cao_Python_StoreDesk_PTIT_HCM_Dinh_dang.docx'
doc=Document(ROOT/'docs/Bao_cao_Python_StoreDesk_PTIT_Hoan_chinh.docx')
body=doc._element.body
nodes=list(body)[:-1]
def txt(el): return ''.join(el.itertext()) if False else ''.join(el.xpath('.//w:t/text()'))
def find(title): return next(i for i,e in enumerate(nodes) if txt(e)==title)
intro_i=find('LỜI MỞ ĐẦU'); group_i=find('THÔNG TIN NHÓM VÀ MỤC LỤC'); chapter_i=find('CHƯƠNG 1  BÀI TOÁN VÀ PHẠM VI THỰC HIỆN')
cover=nodes[:intro_i]; intro=nodes[intro_i:group_i]; group=nodes[group_i:chapter_i]; main=nodes[chapter_i:]
# Remove page breaks introduced by the original page-by-page builder.
def clean(items):
    result=[]
    for e in items:
        e=deepcopy(e)
        for b in e.xpath('.//w:br[@w:type="page"]'): b.getparent().remove(b)
        if e.tag==qn('w:p') and not txt(e).strip() and not e.xpath('.//w:drawing'): continue
        result.append(e)
    return result
cover,intro,group,main=map(clean,[cover,intro,group,main])
toc_i=next(i for i,e in enumerate(group) if txt(e)=='Mục lục')
group=group[:toc_i]
for e in list(body):
    if e.tag!=qn('w:sectPr'): body.remove(e)
def append(items):
    for e in items: body.insert(len(body)-1,e)
def p(text='',style=None): return doc.add_paragraph(text,style)
def heading(text):
    x=p(text,'Heading 1'); x.paragraph_format.page_break_before=True; return x
def field(para,instruction):
    r=para.add_run(); b=OxmlElement('w:fldChar'); b.set(qn('w:fldCharType'),'begin'); r._r.append(b)
    r=para.add_run(); e=OxmlElement('w:instrText'); e.set(qn('xml:space'),'preserve'); e.text=' '+instruction+' '; r._r.append(e)
    r=para.add_run(); e=OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'),'separate'); r._r.append(e)
    para.add_run('Cập nhật trường trong Word')
    r=para.add_run(); e=OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'),'end'); r._r.append(e)

# Rebuild the cover to identify the user's campus and faculty.
for text in ['HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG','CƠ SỞ TẠI THÀNH PHỐ HỒ CHÍ MINH','KHOA CÔNG NGHỆ THÔNG TIN 2']:
    x=p(text); x.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for r in x.runs: r.bold=True; r.font.size=Pt(13)
x=p('BÁO CÁO BÀI TẬP LỚN'); x.alignment=WD_ALIGN_PARAGRAPH.CENTER; x.paragraph_format.space_before=Pt(58)
for r in x.runs: r.bold=True; r.font.size=Pt(20)
x=p('MÔN HỌC LẬP TRÌNH PYTHON'); x.alignment=WD_ALIGN_PARAGRAPH.CENTER
for r in x.runs: r.bold=True; r.font.size=Pt(16)
x=p('XÂY DỰNG WEBSITE QUẢN LÝ KHO HÀNG\nVÀ BÁN HÀNG BẰNG DJANGO\nTÍCH HỢP DASHBOARD PHÂN TÍCH DỮ LIỆU','Title'); x.alignment=WD_ALIGN_PARAGRAPH.CENTER; x.paragraph_format.space_before=Pt(35)
x=p('Ứng dụng StoreDesk'); x.alignment=WD_ALIGN_PARAGRAPH.CENTER
for i,text in enumerate(['Giảng viên hướng dẫn: TODO','Nhóm thực hiện: TODO — 06 thành viên','Lớp học phần: TODO','Học kỳ và năm học: TODO']):
    x=p(text); x.paragraph_format.left_indent=Cm(1.8)
    if i==0: x.paragraph_format.space_before=Pt(35)
x=p('TP. Hồ Chí Minh, tháng TODO năm TODO'); x.alignment=WD_ALIGN_PARAGRAPH.CENTER; x.paragraph_format.space_before=Pt(65)
prelim=doc.add_section(WD_SECTION_START.NEW_PAGE)
append(group)
Paragraph(group[0],doc._body).text='DANH SÁCH THÀNH VIÊN VÀ PHÂN CÔNG'
heading('MỤC LỤC')
field(p(),r'TOC \o "1-2" \h \z')
heading('DANH MỤC BẢNG')
field(p(),r'TOC \h \z \t "Table Caption,1"')
heading('DANH MỤC HÌNH')
field(p(),r'TOC \h \z \t "Figure Caption,1"')
content=doc.add_section(WD_SECTION_START.NEW_PAGE)
append(intro+main)

# Styles encode semantic heading levels for navigation and automatic contents.
for name in ['Table Caption','Figure Caption']:
    if name not in doc.styles: doc.styles.add_style(name,1)
    doc.styles[name].base_style=doc.styles['Caption']
if 'Front Heading' not in doc.styles: doc.styles.add_style('Front Heading',1)
doc.styles['Front Heading'].base_style=doc.styles['Normal']
front_style=doc.styles['Front Heading']
front_style.font.size=Pt(15); front_style.font.bold=True
front_outline=OxmlElement('w:outlineLvl'); front_outline.set(qn('w:val'),'9')
front_style.element.get_or_add_pPr().append(front_outline)
for style in doc.styles:
    if style.type==1:
        style.font.name='Times New Roman'; style.font.color.rgb=RGBColor(0,0,0)
        rf=style.element.get_or_add_rPr().find(qn('w:rFonts'))
        if rf is not None:
            for key in list(rf.attrib):
                if 'theme' in key.lower(): del rf.attrib[key]
            for k in ['ascii','hAnsi','eastAsia','cs']: rf.set(qn('w:'+k),'Times New Roman')
    for b in list(style.element.iter(qn('w:pBdr'))): b.getparent().remove(b)
norm=doc.styles['Normal']; norm.font.size=Pt(13)
norm.paragraph_format.line_spacing=1.5
norm.paragraph_format.space_after=Pt(3)
norm.paragraph_format.first_line_indent=Cm(1)
norm.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
for name,size in [('Title',17),('Heading 1',15),('Heading 2',14),('Heading 3',13)]:
    st=doc.styles[name]; st.font.size=Pt(size); st.font.bold=True
    st.paragraph_format.first_line_indent=Cm(0); st.paragraph_format.line_spacing=1.2
    st.paragraph_format.space_before=Pt(12); st.paragraph_format.space_after=Pt(9)
    st.paragraph_format.keep_with_next=True
for name in ['Caption','Table Caption','Figure Caption']:
    st=doc.styles[name]; st.font.size=Pt(12); st.font.italic=False
    st.paragraph_format.first_line_indent=Cm(0); st.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
    st.paragraph_format.line_spacing=1.15

in_cover=True
for para in doc.paragraphs:
    text=para.text.strip(); pf=para.paragraph_format
    # Keep the full ERD and Dashboard explanation; remove their duplicate summaries.
    if text.startswith('Contact 1 ') or text.startswith('Hình 2.2  Quan hệ giữa các thực thể') or text.startswith('Ca sử dụng theo dõi Dashboard:') or text.startswith('Không chỉnh trực tiếp số dư Stock'):
        para._element.getparent().remove(para._element); continue
    if text.startswith('Hình 2.3  '): para.text=text.replace('Hình 2.3  ','Hình 2.2  ',1); text=para.text
    if text.startswith('Hình 2.4  '): para.text=text.replace('Hình 2.4  ','Hình 2.3  ',1); text=para.text
    if text=='DANH SÁCH THÀNH VIÊN VÀ PHÂN CÔNG': in_cover=False
    if in_cover:
        pf.first_line_indent=Cm(0); pf.line_spacing=1.15
        continue
    pf.first_line_indent=Cm(1); pf.left_indent=Cm(0)
    pf.line_spacing=1.5; pf.space_after=Pt(3); pf.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.widow_control=True
    if text.startswith('TODO: hoàn thiện thông tin nhóm'):
        para._element.getparent().remove(para._element); continue
    code=any(r.font.name=='Consolas' for r in para.runs)
    pic=bool(para._p.xpath('.//w:drawing'))
    if pic:
        pf.first_line_indent=Cm(0); pf.alignment=WD_ALIGN_PARAGRAPH.CENTER
        pf.line_spacing=1; pf.keep_with_next=True; pf.space_before=Pt(6)
    elif code:
        pf.first_line_indent=Cm(0); pf.alignment=WD_ALIGN_PARAGRAPH.LEFT; pf.line_spacing=1
        for r in para.runs: r.font.name='Consolas'; r.font.size=Pt(9)
    elif re.match(r'^Bảng \d+\.\d+',text):
        para.style='Table Caption'; pf.first_line_indent=Cm(0); pf.alignment=WD_ALIGN_PARAGRAPH.CENTER
        pf.line_spacing=1.15; pf.keep_with_next=True
    elif re.match(r'^Hình \d+\.\d+',text):
        para.style='Figure Caption'; pf.first_line_indent=Cm(0); pf.alignment=WD_ALIGN_PARAGRAPH.CENTER; pf.line_spacing=1.15
    elif para.style.name.startswith('Heading'):
        if text.startswith('CHƯƠNG') or text in ['LỜI MỞ ĐẦU','DANH SÁCH THÀNH VIÊN VÀ PHÂN CÔNG','MỤC LỤC','DANH MỤC BẢNG','DANH MỤC HÌNH','KẾT LUẬN VÀ TÀI LIỆU THAM KHẢO']:
            para.style='Heading 1'; pf.page_break_before=True; pf.alignment=WD_ALIGN_PARAGRAPH.CENTER
            if text=='KẾT LUẬN VÀ TÀI LIỆU THAM KHẢO': para.text='KẾT LUẬN'
        elif re.match(r'^\d+\.\d+\.\d+',text): para.style='Heading 3'
        elif re.match(r'^\d+\.\d+',text): para.style='Heading 2'
        elif text=='Tài liệu tham khảo':
            para.style='Heading 1'; para.text='TÀI LIỆU THAM KHẢO'; pf.page_break_before=True; pf.alignment=WD_ALIGN_PARAGRAPH.CENTER
        else: para.style='Heading 3'
        pf.first_line_indent=Cm(0); pf.line_spacing=1.2; pf.keep_with_next=True
        if para.style.name=='Heading 3': pf.space_before=Pt(6)
        # Only real chapter/opening/back matter starts force a new page.
        if para.style.name!='Heading 1': pf.page_break_before=False
    elif text.startswith('• '):
        pf.left_indent=Cm(.6); pf.first_line_indent=Cm(-.4)
    elif re.match(r'^\[\d+\]',text):
        pf.left_indent=Cm(.8); pf.first_line_indent=Cm(-.8); pf.line_spacing=1.2
        for r in para.runs: r.font.size=Pt(12)
    if text=='Kết luận':
        para._element.getparent().remove(para._element)

# Avoid including navigation pages themselves in the automatic table of contents.
for para in doc.paragraphs:
    if para.text in ['MỤC LỤC','DANH MỤC BẢNG','DANH MỤC HÌNH']:
        para.style='Front Heading'
        out=OxmlElement('w:outlineLvl'); out.set(qn('w:val'),'9'); para._p.get_or_add_pPr().append(out)
    if para.text.startswith('4.9 '): para.paragraph_format.page_break_before=True

for t in doc.tables:
    installation=bool(t.rows and t.cell(0,0).text=='Bước')
    for row_index,row in enumerate(t.rows):
        for cell in row.cells:
            for para in cell.paragraphs:
                pf=para.paragraph_format; pf.line_spacing=1.1; pf.space_after=Pt(3)
                pf.first_line_indent=Cm(0); pf.alignment=WD_ALIGN_PARAGRAPH.LEFT
                if row_index==0: pf.keep_with_next=True
                for r in para.runs: r.font.name='Times New Roman'; r.font.size=Pt(11)
                if installation: pf.line_spacing=1

for i,sec in enumerate(doc.sections):
    sec.page_width=Cm(21); sec.page_height=Cm(29.7)
    sec.top_margin=Cm(2); sec.bottom_margin=Cm(2); sec.left_margin=Cm(3.5); sec.right_margin=Cm(2)
    sec.header_distance=Cm(.8); sec.footer_distance=Cm(1)
    sec.different_first_page_header_footer=False
    sec.header.is_linked_to_previous=False; sec.footer.is_linked_to_previous=False
    for hf in [sec.header,sec.footer]:
        for e in list(hf._element): hf._element.remove(e)
    num=sec._sectPr.find(qn('w:pgNumType'))
    if num is None: num=OxmlElement('w:pgNumType'); sec._sectPr.append(num)
    num.set(qn('w:start'),'1'); num.set(qn('w:fmt'),'lowerRoman' if i==1 else 'decimal')
    if i:
        f=sec.footer.add_paragraph(); f.alignment=WD_ALIGN_PARAGRAPH.CENTER
        f.paragraph_format.first_line_indent=Cm(0); f.paragraph_format.line_spacing=1
        field(f,'PAGE')

# Fit all original fixed-width tables and drawings to the new binding margin.
available=Cm(15.5)
for t in doc.tables:
    total=sum(col.width for col in t.columns)
    if total>available:
        factor=available/total
        for col in t.columns: col.width=int(col.width*factor)
        for row in t.rows:
            for cell in row.cells:
                if cell.width: cell.width=int(cell.width*factor)
for shape_index,shape in enumerate(doc.inline_shapes):
    if shape.width>available:
        factor=available/shape.width; shape.height=int(shape.height*factor); shape.width=available
    # Screenshots and diagrams stay with their captions without consuming a full page.
    if shape.height>Cm(17):
        factor=Cm(17)/shape.height; shape.width=int(shape.width*factor); shape.height=Cm(17)
    if shape_index==8 and shape.height>Cm(6.3):
        factor=Cm(6.3)/shape.height; shape.width=int(shape.width*factor); shape.height=Cm(6.3)

doc.core_properties.title='Báo cáo Lập trình Python StoreDesk PTIT HCM'
doc.save(OUT)
print(OUT)
