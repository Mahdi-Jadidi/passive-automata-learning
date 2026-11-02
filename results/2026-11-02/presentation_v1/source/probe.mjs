import fs from 'node:fs/promises';
import {pathToFileURL,fileURLToPath} from 'node:url';
const {Presentation,PresentationFile}=await import(pathToFileURL('C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const root=new URL('../',import.meta.url);
const p=Presentation.create({slideSize:{width:1280,height:720}});
const s=p.slides.add();s.background.fill='#F7F7F2';
const sh=s.shapes.add({geometry:'textbox',position:{left:60,top:45,width:1160,height:120},fill:'none',line:{fill:'none',width:0}});
sh.text='کشف افراز الفبا از تریس‌های درهم‌تنیده';
sh.text.style={fontSize:50,typeface:'Arial',color:'#101E2E',alignment:'right',verticalAlignment:'middle',autoFit:'none',insets:0};
const t=s.tables.add({rows:3,columns:3,left:80,top:250,width:1120,height:240,values:[['نتیجه','تصویر منفی','افراز'],['سازگار','ba , cd','ab / cd'],['ناممکن','ac , bd','ac / bd']]});
t.borders.assign({fill:'#D7DFE1',width:1});
for(let r=0;r<3;r++)for(let c=0;c<3;c++){const v=t.getCell(r,c);v.fill=r===0?'#101E2E':'#FFFFFF';v.text.style={typeface:'Arial',fontSize:30,color:r===0?'#FFFFFF':'#101E2E',alignment:'center',verticalAlignment:'middle',insets:6};}
s.speakerNotes.text='آزمایش خوانایی فارسی. Source: docs/ALGORITHM_TUTORIAL_FA.md';
await fs.writeFile(new URL('private/probe.png',root),new Uint8Array(await (await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));
await (await PresentationFile.exportPptx(p)).save(fileURLToPath(new URL('private/probe.pptx',root)));
console.log('probe exported');
