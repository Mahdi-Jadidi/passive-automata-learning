import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const {Presentation,PresentationFile}=await import(pathToFileURL('C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const data=JSON.parse(await fs.readFile(path.join(root,'source/slides_bilingual_v5.json'),'utf8'));
function box(s,t,x,y,w,h,size,bold,align){
 const a=s.shapes.add({name:'text-'+s.shapes.items.length,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 a.text=t;a.text.style={fontSize:size,typeface:'Arial',color:'#000000',alignment:align,verticalAlignment:'middle',bold,autoFit:'none',wrap:'square',insets:0};
}
for(const lang of ['en','fa']){
 const p=Presentation.create({slideSize:{width:1280,height:720}});
 const speaker=[];
 for(let i=0;i<data.length;i++){
  const src=data[i],d=src[lang],s=p.slides.add();s.background.fill='#FFFFFF';
  const align=lang==='fa'?'right':'left';
  if(src.cover){
   box(s,d.title,76,145,1128,180,58,true,align);
   for(let j=0;j<d.items.length;j++)box(s,d.items[j],76,385+j*105,1128,84,31,false,align);
  }else{
   box(s,d.title,76,42,1128,90,46,true,align);
   const count=d.items.length,gap=count>=5?87:count===4?105:125;
   for(let j=0;j<count;j++)box(s,d.items[j],90,170+j*gap,1100,count>=5?78:93,i===18?28:30,false,align);
   box(s,String(i+1),76,665,65,25,19,false,'left');
  }
  const note=d.note+'\n\n'+src.sources.map(x=>'Source: '+x).join('\n');
  s.speakerNotes.text=note;speaker.push({slide:i+1,title:d.title,notes:note});
 }
 if(p.slides.items.length!==19)throw Error('Expected19slides');
 await (await PresentationFile.exportPptx(p)).save(path.join(root,'private/candidate_'+lang+'_v2.pptx'));
 await fs.writeFile(path.join(root,'private/notes_'+lang+'_v2.json'),JSON.stringify(speaker,null,2));
 console.log('Created19 '+lang+' text-only slides');
}
await fs.writeFile(path.join(root,'private/contract_v2.json'),JSON.stringify({slideCount:19,images:0,charts:0,tables:0,fontPolicy:{basis:'design',families:['Arial']}},null,2));
