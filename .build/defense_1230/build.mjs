import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const build=path.dirname(fileURLToPath(import.meta.url));
const workspace=path.resolve(build,'../..');
const out=path.join(workspace,'output/final_1230');
const skill='C:/Users/Mahdi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const py='C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES='C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const slides=JSON.parse(await fs.readFile(path.join(build,'slides.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const navy='#17324D',ink='#172A3A',accent='#1C6C64',muted='#5C6A74';
const tables=[];
function text(s,str,x,y,w,h,size,{font='Tahoma',color=ink,bold=false,align='left',name='text'}={}){
 const sh=s.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=str;sh.text.style={typeface:font,fontSize:size,color,bold,alignment:align,verticalAlignment:'middle',wrap:'square',autoFit:'none',insets:0};return sh;
}
for(const [i,d] of slides.entries()){
 const s=p.slides.add();s.background.fill='#FFFFFF';
 const appendix=i>=14;
 if(i===0){
  text(s,d.title,76,145,1128,105,60,{color:navy,bold:true,name:'slide-title'});
  text(s,d.blocks[0].text,80,285,1120,75,37,{color:accent});
  text(s,d.blocks[1].text,80,390,1120,72,30);
  text(s,d.blocks[2].text,80,515,1120,70,26,{color:muted});
 }else{
  text(s,d.title,70,39,1140,92,appendix?39:43,{color:navy,bold:true,name:'slide-title'});
  let y=157;
  for(const [j,b] of d.blocks.entries()){
   if(b.kind==='table'){
    const rows=b.rows.length+1;const rowHeight=b.rowHeight??(appendix?59:50);const h=rows*rowHeight;
    const t=s.tables.add({rows,columns:b.headers.length,left:80,top:y,width:1120,height:h,columnWidths:b.widths.map(v=>1120*v/b.widths.reduce((a,c)=>a+c,0)),values:[b.headers,...b.rows]});
    t.styleOptions={headerRow:true,bandedRows:false};t.borders.assign({style:'solid',fill:'#D9D9D9',width:1});
    for(let r=0;r<rows;r++)for(let c=0;c<b.headers.length;c++){
     const cell=t.getCell(r,c);cell.fill=r===0?navy:(r%2?'#F3F6F8':'#FFFFFF');
     cell.text.style={typeface:'Tahoma',fontSize:appendix?25:26,color:r===0?'#FFFFFF':ink,bold:r===0,alignment:'center',verticalAlignment:'middle',wrap:'square',autoFit:'none',insets:{left:10,right:10,top:5,bottom:5}};
    }
    tables.push(i+1);y+=h+18;
   }else{
    const formula=b.kind==='eq';let size=formula?(appendix?29:31):(appendix?25:28);
    if(formula&&b.text.length>84)size=26;
    const h=b.height??(formula?60:(b.text.length>100?77:64));
    text(s,b.text,80,y,1120,h,size,{font:formula?'Cambria Math':'Tahoma',color:formula?accent:ink,align:formula?'center':'left',name:`body-${j}`});
    y+=h+11;
   }
  }
  if(y>660)console.log('DENSITY',i+1,y);
 }
 text(s,`${i+1} / 28`,70,674,130,25,18,{color:muted,name:'page-number'});
 if(appendix)text(s,'PROOF APPENDIX',890,674,310,25,18,{color:muted,align:'right',name:'appendix-label'});
 s.speakerNotes.text=(d.seconds?`زمان پیشنهادی: ${d.seconds} ثانیه\n\n`:'پیوست خارج از زمان اصلی\n\n')+d.notes+'\n\nProof: '+d.proof+'\nSource: '+d.source;
}
await fs.writeFile(path.join(build,'presentation.proto.json'),JSON.stringify(p.toProto()),'utf8');
const raw=path.join(build,'raw.pptx');await (await PresentationFile.exportPptx(p)).save(raw);
const candidate=path.join(build,'candidate.pptx');
const patch=spawnSync(py,['-X','utf8',path.join(build,'patch_rtl.py'),raw,candidate],{encoding:'utf8'});
if(patch.status!==0)throw new Error(patch.stderr||patch.stdout);
const receipt=await finalizePresentation({workspaceDir:workspace,candidatePath:candidate,finalPath:path.join(out,'RPNI_Final_1230_EN.pptx'),pythonExecutable:py,
 explicitTotalSlideCount:28,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tables.flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:tables,fontPolicy:{basis:'design',families:['Tahoma','Cambria Math']},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation-v3.json')});
console.log(JSON.stringify(receipt));
