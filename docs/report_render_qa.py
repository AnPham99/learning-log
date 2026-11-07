from pathlib import Path
import sys
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageOps
p=Path(sys.argv[1])
ims=convert_from_path(str(p),dpi=100,poppler_path=r'C:\Users\Huyen\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin')
for i,im in enumerate(ims): im.save(p.parent/f'page-{i+1}.png')
for start in range(0,len(ims),12):
    sheet=Image.new('RGB',(1120,1260),'#ccc'); draw=ImageDraw.Draw(sheet)
    for i,im in enumerate(ims[start:start+12]):
        sheet.paste(ImageOps.contain(im,(270,390)),((i%4)*280,(i//4)*420))
        draw.text(((i%4)*280+8,(i//4)*420+395),str(start+i+1),fill='black')
    sheet.save(p.parent/f'contact-{start//12}.png')
print(len(ims))
