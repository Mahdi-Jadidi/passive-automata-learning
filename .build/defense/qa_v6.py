from PIL import Image,ImageDraw,ImageChops
from pathlib import Path
root=Path(__file__).parent
for page in range(4):
    canvas=Image.new('RGB',(1000,620),'#dddddd')
    draw=ImageDraw.Draw(canvas)
    for j in range(8):
        i=page*8+j+1
        if i>28:break
        im=Image.open(root/'render-v6'/f'slide-{i:02}.png').convert('RGB');im.thumbnail((490,270))
        x=(j%2)*500;y=(j//2)*155
        # Thumbnails are for QA only, never used as slide content.
        im.thumbnail((265,149));canvas.paste(im,(x,y));draw.text((x+275,y+20),str(i),fill='black')
    canvas.save(root/f'qa-slides-v6-{page+1}.png')
changes=[]
for i in range(1,29):
    old=Image.open(root/'render-delivery'/f'slide-{i:02}.png').convert('RGB')
    new=Image.open(root/'render-v6'/f'slide-{i:02}.png').convert('RGB')
    diff=ImageChops.difference(old,new)
    nonzero=sum(1 for p in diff.getdata() if max(p)>40)
    if nonzero>200:changes.append((i,nonzero))
print('Changed slides:',changes)
paths=sorted(root.glob('notes-v6-*.png'))
for page in range(0,len(paths),4):
    canvas=Image.new('RGB',(1100,780),'#dddddd')
    for j,p in enumerate(paths[page:page+4]):
        im=Image.open(p).convert('RGB');im.thumbnail((545,380));canvas.paste(im,((j%2)*550,(j//2)*390))
    canvas.save(root/f'qa-notes-v6-{page//4+1}.png')
