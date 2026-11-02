import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const {Presentation,PresentationFile}=await import(pathToFileURL('C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const ROOT=fileURLToPath(new URL('../',import.meta.url));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#101E2E',teal:'#027D83',amber:'#B87819',paper:'#F7F7F2',gray:'#536372',line:'#D9E0E3',white:'#FFFFFF',red:'#A74332'};
const SRC='https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/';
const notes=[]; const tableOwners=[];
function box(s,text,x,y,w,h,{size=32,font='Arial',color=C.navy,align='right',bold=false}={}){
 const q=s.shapes.add({name:`text-${s.id}-${s.shapes.items.length}`,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 q.text=text;q.text.style={fontSize:size,typeface:font,color,alignment:align,verticalAlignment:'middle',bold,autoFit:'none',wrap:'square',insets:0};return q;
}
function base(title,{dark=false,appendix=false,note='',sources=[]}={}){
 const s=p.slides.add();s.background.fill=dark?C.navy:C.paper;
 box(s,title,70,42,1140,90,{size:48,bold:true,color:dark?C.white:C.navy});
 box(s,String(p.slides.items.length).padStart(2,'0'),70,663,75,28,{size:20,color:dark?'#AFC2CB':C.gray,align:'left',font:'Consolas'});
 if(appendix)box(s,'پشتیبان',1080,663,130,28,{size:20,color:dark?'#AFC2CB':C.gray});
 const n=[note,...sources.map(x=>'منبع: '+SRC+x)].join('\n\n');s.speakerNotes.text=n;notes.push({slide:p.slides.items.length,title,notes:n});return s;
}
function lines(s,items,{y=185,gap=105,size=34,color=C.navy}={}){items.forEach((t,i)=>box(s,t,90,y+i*gap,1100,85,{size,color}));}
function formula(s,t,y=245,{size=43,dark=false}={}){return box(s,t,85,y,1110,115,{size,font:'Cambria Math',align:'center',color:dark?C.white:C.teal});}
function caption(s,t,{dark=false,y=603,color}={}){box(s,t,90,y,1100,52,{size:26,color:color??(dark?'#C2D8DF':C.gray)});}
function table(s,values,{x=75,y=185,w=1130,h=390,widths,latin=[],size=27,highlightRows=[]}={}){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,...(widths?{columnWidths:widths}:{})});
 t.borders.assign({fill:C.line,width:1});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?C.navy:(highlightRows.includes(r)?'#E0F0EC':C.white);
  cell.text.style={typeface:latin.includes(c)&&r>0?'Consolas':'Arial',fontSize:size,color:r===0?C.white:C.navy,bold:r===0,alignment:'center',verticalAlignment:'middle',insets:7};
 }
 tableOwners.push(p.slides.items.length);return t;
}
// 01 Cover. Abstract art is decorative, never an evidence figure.
{
 const s=p.slides.add();s.background.fill=C.navy;s.images.add({blob:new Uint8Array(await fs.readFile(path.join(ROOT,'assets/cover.png'))),contentType:'image/png',position:{left:0,top:0,width:1280,height:720},fit:'cover',alt:'تصویر انتزاعی درهم‌تنیدگی و جداسازی رشته‌های رویداد؛ اثر مفهومی تولیدشده با هوش مصنوعی'});
 box(s,'کشف افراز الفبا\nاز تریس‌های درهم‌تنیده',470,190,735,195,{size:63,bold:true,color:C.white});
 box(s,'شناسایی کامل و جزئی با گواه ریاضی',520,420,680,72,{size:34,color:'#C0E5E3'});
 box(s,'یادگیری غیرفعال اتوماتا',690,560,510,48,{size:28,color:'#C0CAD6'});
 s.speakerNotes.text='موضوع ارائه کشف گروه‌های مالکیت نمادها پیش از یادگیری عامل‌های محلی است. حدود ۱۵ دقیقه برای بخش اصلی؛ اسلایدهای پایانی پشتیبان‌اند. تصویر جلد مفهومی و تولیدشده با ابزار داخلی image_gen است، نه تصویر سامانهٔ واقعی. منبع تصویر: assets/cover.png. محتوای علمی از پژوهش‌های C008 تا C010 با ذکر فرض‌ها می‌آید.';
 notes.push({slide:1,title:'کشف افراز الفبا',notes:s.speakerNotes.text});
}
// 02
{
 const s=base('ساختار مجهول پیش از یادگیری اتوماتا',{note:'تریس سراسری رویدادهای مؤلفه‌ها را درهم می‌آمیزد. هدف اولیه کاهش مسئله به یادگیری عامل‌های محلی است. آزمایش‌های این پروژه فعلاً صحت افراز و شناسایی‌پذیری را بررسی کرده‌اند؛ کاهش زمان یا فضای حالت RPNI هنوز نتیجهٔ اندازه‌گیری‌شده نیست.',sources:['results/2026-11-02/partition_coverage_v9/RESEARCH_REPORT_FA.md']});
 lines(s,['رویدادهای چند مؤلفه در یک تریس دیده می‌شوند.','الفبای هر مؤلفه از ابتدا مشخص نیست.','پیش از یادگیری محلی، مالکیت نمادها را بررسی می‌کنیم.'],{gap:110});
 caption(s,'اثر افراز بر هزینهٔ یادگیری محلی هنوز ارزیابی نشده است.');
}
// 03
{
 const s=base('مدل مشاهده و فرض‌ها',{note:'هر نماد یک مالک دارد. عوامل مستقل‌اند و تصویر ترتیب محلی را حفظ می‌کند. زبان‌ها منظم‌اند، با کران حالت نامعلوم. ورودی مثبت و منفیِ کلمهٔ کامل دارد. نبود یک تریس در لاگ برچسب منفی نمی‌سازد. نسخهٔ اصلی بحث تعداد دستگاه‌ها را نامعلوم می‌گیرد؛ برش t=2 بعداً فقط برای توضیح محاسبه است. دادهٔ اجرایی prefix-closed به قرارداد متفاوتی نیاز دارد.',sources:['results/2026-11-02/partition_unrestricted_v10/coordination/CONTRACT.md','results/2026-11-02/partition_coverage_v9/theory/PROOFS_v1.md']});
 table(s,[['معنای فرض','بخش مدل'],['هر نماد متعلق به یک مؤلفه است','الفبای معلوم و مجزا'],['رویدادهای محلی ترتیب خود را حفظ می‌کنند','استقلال مؤلفه‌ها'],['پذیرش و ردِ کلمهٔ کامل معتبر است','برچسب‌های دقیق'],['تعداد حالت و تعداد مؤلفه از ابتدا معلوم نیست','عامل‌های منظم']],{h:370,widths:[670,460],size:29});
 caption(s,'با دادهٔ فقط مثبت، تمام افرازها سازگارند؛ غیبتِ تریس، منفی نیست.');
}
// 04
{
 const s=base('تصویر تریس روی یک بلوک',{note:'π_B تمام رویدادهای خارج از B را حذف می‌کند و ترتیب بقیه را تغییر نمی‌دهد. مثال نشان می‌دهد تفکیک ab تفاوت مثبت و منفی را می‌بیند، ولی بلوک ac همان تصویر را می‌بیند.',sources:['docs/ALGORITHM_TUTORIAL_FA.md']});
 table(s,[['تصویر محلی','بلوک','تریس'],['ab','{a,b}','abcd'],['ba','{a,b}','bacd'],['ac','{a,c}','abcd'],['ac','{a,c}','bacd']],{h:360,widths:[380,370,380],latin:[0,1,2],size:33,highlightRows:[1,2]});
 caption(s,'تفاوتِ سراسری فقط وقتی قابل رد است که یک عامل آن را ببیند.');
}
// 05
{
 const s=base('معیار دقیق سازگاری افراز',{dark:true,note:'H(B) تصویر تمام مثبت‌هاست. هر عامل سازگار مجبور است H(B) را بپذیرد. پس برای هر منفی، دست‌کم یک بلوک باید تصویر ناموجود در H(B) داشته باشد. کفایت: خود H(B) را زبان عامل انتخاب می‌کنیم؛ متناهی و منظم است. این شاهد وجود مدل است و زبان واقعی عامل را تعیین نمی‌کند.',sources:['results/2026-11-02/partition_coverage_v9/theory/PROOFS_v1.md']});
 formula(s,'H(B) = { π_B(p) : p ∈ P }',175,{dark:true});
 formula(s,'∀ n ∈ N   ∃ B ∈ Π :  π_B(n) ∉ H(B)',335,{dark:true,size:42});
 caption(s,'هر منفی باید دست‌کم در یک بلوک قابل رد کردن باشد.',{dark:true});
}
// 06
{
 const s=base('مثال آموزشی با تعداد مؤلفهٔ نامعلوم',{note:'این مثال محور ادامه است. هیچ تعداد واقعی دستگاه به ورودی نمی‌دهیم. برای فهم DP ابتدا سهم لایهٔ دوبلوکی را می‌شماریم، سپس تمام تعدادها را جمع می‌زنیم. k یا t در آن محاسبه، متغیر شمارش است، نه فرضی دربارهٔ دستگاه واقعی.',sources:['docs/ALGORITHM_TUTORIAL_FA.md','results/2026-11-02/partition_unrestricted_v10/coordination/CONTRACT.md']});
 formula(s,'Σ = { a, b, c, d }',180,{size:49});
 formula(s,'P = { abcd }       N = { bacd }',330,{size:48});
 caption(s,'سؤال: کدام تقسیمِ نمادها می‌تواند هر دو برچسب را توضیح بدهد؟');
}
// 07
{
 const s=base('سه جواب در لایهٔ دوبلوکی',{note:'بلوک شامل a را سمت چپ می‌نویسیم تا دوباره‌شماری نشود. هر دو تصویر در چهار افراز ردشده با مثبت برابرند. سه افراز دیگر تصویر ab یا abc یا abd را متفاوت می‌بینند. این بررسی C_2 است، نه اعلام اینکه تعداد واقعی دستگاه‌ها دو است.',sources:['docs/ALGORITHM_TUTORIAL_FA.md']});
 table(s,[['نتیجه','تصاویر منفی','تصاویر مثبت','افراز'],['رد','a , bcd','a , bcd','a / bcd'],['سازگار','ba , cd','ab , cd','ab / cd'],['رد','ac , bd','ac , bd','ac / bd'],['رد','ad , bc','ad , bc','ad / bc'],['سازگار','bac , d','abc , d','abc / d'],['سازگار','bad , c','abd , c','abd / c'],['رد','acd , b','acd , b','acd / b']],{y:160,h:442,widths:[190,310,310,320],latin:[1,2,3],size:26,highlightRows:[2,5,6]});
 caption(s,'این جدول فقط افرازهای دوبلوکی را می‌شمارد.',{y:613});
}
// 08
{
 const s=base('خانوادهٔ کامل بدون دانستن تعداد دستگاه‌ها',{note:'a,b در هر جواب کنار هم‌اند. جواب‌ها دقیقاً ادغام‌های سه اتم ab,c,d هستند. با t=1 یک جواب، t=2 سه جواب، t=3 یک جواب و t=4 هیچ جواب نداریم. عدد پنج تعداد افرازهاست، نه تعداد DFAها و نه تعداد دستگاه‌های واقعی.',sources:['docs/ALGORITHM_TUTORIAL_FA.md','results/2026-11-02/partition_unrestricted_v10/coordination/CONTRACT.md']});
 table(s,[['افرازهای سازگار','تعداد جواب','تعداد بلوک'],['abcd','1','1'],['ab / cd     abc / d     abd / c','3','2'],['ab / c / d','1','3'],['—','0','4']],{h:350,widths:[690,220,220],latin:[0,1,2],size:29});
 caption(s,'جمع جواب‌ها ۵ است؛ انتخابِ بیشترین تعداد بلوک، کشف تعداد واقعی نیست.');
}
// 09
{
 const s=base('ماسک‌های ردِ منفی‌ها',{note:'هر منفی یک بیت دارد. R(B) به معنی توان ردکردن در یک توضیح سازگار است، نه اینکه عامل واقعیِ ناشناخته حتماً آن تصویر را رد می‌کند. بلوک‌های نمادی باید افراز باشند؛ ماسک‌های منفی می‌توانند هم‌پوشان باشند.',sources:['results/2026-11-02/partition_coverage_v9/theory/PROOFS_v1.md']});
 formula(s,'R(B) = { n ∈ N : π_B(n) ∉ H(B) }',155,{size:39});
 table(s,[['ماسک رد','بلوک‌های نمونه'],['1','ab , abc , abd , abcd'],['0','a , ac , ad , cd']],{y:310,h:205,widths:[290,840],latin:[0,1],size:32});
 caption(s,'نمادها بدون هم‌پوشانی؛ منفی‌ها با اجتماعِ ماسک‌ها پوشش داده می‌شوند.');
}
// 10
{
 const s=base('حالت برنامه‌ریزی پویا',{dark:true,note:'S نمادها یا اتم‌های باقی‌مانده، U ماسک منفی‌های از قبل ردشده و t تعداد بلوک‌های مورد نیاز در ادامه است. در خروجی بدون K، روی تمام tهای ممکن جمع می‌زنیم. حالت DP وضعیت جست‌وجوست و با حالت DFA واقعی فرق دارد.',sources:['results/2026-11-02/partition_coverage_v9/implementation/ownership_solver_v1.py','results/2026-11-02/partition_coverage_v9/theory/PROOFS_v1.md']});
 formula(s,'C(S, U, t)',175,{size:65,dark:true});
 table(s,[['معنا','نماد'],['نمادها یا اتم‌های باقی‌مانده','S'],['منفی‌های پوشش‌داده‌شده','U'],['تعداد بلوک‌های باقی‌مانده','t']],{y:330,h:240,widths:[900,230],latin:[1],size:30});
 caption(s,'پایان معتبر: هیچ نمادی نمانده، همهٔ منفی‌ها رد شده و بلوکی باقی نمانده است.',{dark:true,y:607});
}
// 11
{
 const s=base('هر افراز فقط یک مسیر دارد',{note:'در هر گام بلوک B حاوی کوچک‌ترین عضو S را انتخاب می‌کنیم. هر افراز دقیقاً یک چنین بلوکی دارد. این تناظرِ یک‌به‌یک هم کامل‌بودن و هم نبودِ دوباره‌شماری را ثابت می‌کند. حافظهٔ DP جواب حالت‌های تکراری را بازاستفاده می‌کند؛ بدترین حالت همچنان نمایی است.',sources:['results/2026-11-02/partition_coverage_v9/theory/PROOFS_v1.md']});
 formula(s,'C(S,U,t) = Σ C(S∖B, U ∪ R(B), t−1)',155,{size:40});
 box(s,'جمع روی همهٔ بلوک‌های حاوی کوچک‌ترین نماد',110,285,1060,60,{size:30});
 table(s,[['abcd','acd','abd','abc','ad','ac','ab','a'],['0','0','1','1','0','0','1','0']],{y:390,h:130,widths:Array(8).fill(141.25),latin:[0,1,2,3,4,5,6,7],size:29});
 caption(s,'در لایهٔ دوبلوکیِ مثال، جمع سهم شاخه‌ها برابر سه است.');
}
// 12
{
 const s=base('مالکیت قطعی در میان چند افراز',{note:'اینجا دیگر روی همهٔ تعدادهای مجاز، یعنی تمام تعدادها، کار می‌کنیم. از پنج افراز، a,b در هر پنج با هم‌اند. هر زوج دیگر در دو افراز با هم است. برای ابهام باید دو افراز شاهد با رابطهٔ مخالف ارائه شود. نسبت q/Z احتمال فیزیکی نیست.',sources:['docs/ALGORITHM_TUTORIAL_FA.md','results/2026-11-02/partition_coverage_v9/theory/PROOFS_v1.md']});
 table(s,[['نتیجه','شمار هم‌بلوکی از ۵','زوج'],['قطعاً هم‌بلوک','5','a,b'],['مبهم','2','a,c'],['مبهم','2','a,d'],['مبهم','2','b,c'],['مبهم','2','b,d'],['مبهم','2','c,d']],{y:165,h:420,widths:[440,430,260],latin:[1,2],size:29,highlightRows:[1]});
 caption(s,'قطعیت از تمام جواب‌ها می‌آید؛ کسرِ شمارش، احتمال نیست.',{y:609});
}
// 13
{
 const s=base('دو گروه اجباری، دو معماریِ ممکن',{note:'منفی تازه abdc باید واقعاً برچسب معتبر داشته باشد. منفی قبلی ab را و منفی تازه cd را اجبار می‌کند. بدون تعداد واقعی، هنوز یک دستگاه abcd و دو دستگاه ab,cd هر دو توضیح می‌دهند. با فرض خارجی معتبر k=2 فقط دومی می‌ماند، اما در این ارائه چنین فرضی را تحمیل نمی‌کنیم.',sources:['results/2026-11-02/partition_identification_v8/theory/PROOFS_v1.md']});
 formula(s,'P = { abcd }     N = { bacd, abdc }',155,{size:40});
 table(s,[['تعداد بلوک','مالکیت سازگار'],['1','abcd'],['2','ab / cd']],{y:325,h:195,widths:[350,780],latin:[0,1],size:38});
 caption(s,'بدون اطلاعات اضافه، ادغامِ دستگاه‌ها از رفتار قابل تشخیص نیست.');
}
// 14
{
 const s=base('حد شناساییِ مالکیت با تعداد نامعلوم',{dark:true,note:'برای هر دادهٔ سازگار P∩N=∅، مدل تک‌بلوکی با زبان P وجود دارد. اگر یک افراز غیرتک‌بلوکی هم سازگار باشد، دو مالکیت ممکن داریم و هیچ الگوریتمی از همان داده نمی‌تواند بین آن‌ها با تضمین همگانی انتخاب کند. این محدودیت اطلاعاتی است و با جست‌وجوی بیشتر حل نمی‌شود. نمونه‌های قابل شناسایی مثل Pab,Nba با تنها افراز تک‌بلوکی همچنان وجود دارند.',sources:['results/2026-11-02/partition_identification_v8/theory/PROOFS_v1.md','results/2026-11-02/partition_unrestricted_v10/coordination/CONTRACT.md']});
 lines(s,['هر نمونهٔ بدون تناقض، یک توضیح تک‌بلوکی دارد.','وجود یک توضیح چندبلوکی، مالکیت را مبهم می‌کند.','دادهٔ بیشتر یا فرض معتبر می‌تواند بعضی ابهام‌ها را حذف کند.'],{y:190,gap:117,size:35,color:C.white});
 caption(s,'تعداد خارجی را حذف می‌کنیم؛ ابهامِ معماری واقعی می‌تواند باقی بماند.',{dark:true});
}
// 15
{
 const s=base('گواهِ شناسایی و خروجیِ ناتمام',{note:'نسخه‌فضا تصویر تمام مدل‌های مجاز و سازگار روی مالکیت است. فقط اگر این تصویر یک عضو داشته باشد، مالکیت شرطی شناسایی شده. در خانوادهٔ چندعضوی روابط زوجی می‌توانند قطعی باشند. صفر عضو نشانهٔ تناقض فرض‌ها/داده است، نه یکتاییِ تهی. قطع پیش از اثبات به unknown می‌انجامد.',sources:['results/2026-11-02/partition_identification_v8/theory/PROOFS_v1.md']});
 table(s,[['تفسیر','حالت'],['مالکیت مشروط تعیین شده است','دقیقاً یک افراز'],['روابط قطعیِ جزئی و شاهدهای ابهام','چند افراز'],['فرض‌ها یا داده با مدل سازگار نیستند','هیچ افراز'],['هیچ حکم نهایی از نبودِ پاسخ نمی‌دهیم','جست‌وجوی ناتمام']],{h:365,widths:[740,390],size:30});
 caption(s,'مدل تک‌بلوکی برای هر مجموعهٔ برچسبِ بدون تناقض ممکن است.');
}
// 16
{
 const s=base('محاسبه روی گروه‌های اجباری',{note:'اگر مثبت و منفی فقط با تعویض دو نماد مجاور فرق کنند، جدا بودن مالک آن‌ها همهٔ تصاویر را یکسان می‌کرد و تناقض می‌داد. یال‌های معتبر در گراف، گروه‌های غیرقابل شکستن می‌سازند. مؤلفه‌ها را اتم می‌کنیم؛ هر جواب سازگار ادغام اتم‌هاست. نبود یال به معنی استقلال نیست و آزمون کامل تصویر باید برقرار بماند.',sources:['results/2026-11-02/partition_finest_v7/theory/PROOFS_v1.md','results/2026-11-02/partition_unrestricted_v10/coordination/CONTRACT.md']});
 table(s,[['نتیجه','زوج','شاهد مثبت / منفی'],['هم‌مالک','a,b','abcd / bacd'],['هم‌مالک','c,d','abcd / abdc']],{y:205,h:200,widths:[330,230,570],latin:[1,2],size:32});
 lines(s,['گروهِ اجباری را به یک اتم تبدیل می‌کنیم.','فضای جست‌وجو برحسب تعداد اتم‌ها کوچک می‌شود.'],{y:440,gap:80,size:31});
}
// 17
{
 const s=base('شمارش بستهٔ تمام ادغام‌ها',{dark:true,note:'قضیه: اگر افراز اتم‌های sound خودش معیار تصویر را پاس کند، هر افراز سازگار ادغام آن است و هر ادغام هم سازگار می‌ماند. در نتیجه تعدادهای بلوکی با اعداد استرلینگ و کل با بل محاسبه می‌شوند. دو اتم متفاوت با چسباندنشان در یک اتم موقت، Bell(r−1) افراز هم‌بلوکی دارند. این شمارش بدون فهرست کردن Bell(r) جواب است. اگر آزمون مستقیم شکست خورد، این فرمول نباید به کار رود.',sources:['results/2026-11-02/partition_finest_v7/theory/PROOFS_v1.md','results/2026-11-02/partition_unrestricted_v10/coordination/CONTRACT.md']});
 box(s,'اگر افرازِ اتم‌ها خودش سازگار باشد',90,165,1100,65,{size:35,color:C.white});
 formula(s,'count(k) = S(r,k)     total = Bell(r)',265,{size:43,dark:true});
 formula(s,'q(distinct atoms) = Bell(r−1)',405,{size:43,dark:true});
 caption(s,'تعداد اتم‌ها از داده استنتاج می‌شود؛ تعداد واقعی دستگاه‌ها معلوم فرض نمی‌شود.',{dark:true});
}
// 18
{
 const s=base('هرسِ دقیقِ حالت ناممکن',{note:'اگر B زیرمجموعهٔ S باشد و منفی روی S با مثبتی هم‌تصویر شود، روی B هم همان هم‌تصویری می‌ماند؛ پس R(B)⊆R(S). تمام بلوک‌های آینده زیرمجموعهٔ rem هستند. اگر منفی‌ای نه قبلاً رد شده و نه با کل rem قابل رد باشد، هیچ تکمیلی آن را رد نمی‌کند و شمار حالت صفر است. عبور از این شرط فقط لازم است، کافی نیست. بدترین حالت نمایی پابرجاست.',sources:['results/2026-11-02/partition_coverage_v9/theory/FUTURE_PRUNE_v1.md','results/2026-11-02/partition_unrestricted_v10/coordination/CONTRACT.md']});
 formula(s,'B ⊆ S   ⇒   R(B) ⊆ R(S)',165,{size:48});
 formula(s,'covered ∪ R(rem) ≠ ALL   ⇒   count = 0',345,{size:40});
 caption(s,'این شاخه به‌طور ریاضی بی‌جواب است؛ هیچ افراز سازگاری حذف نمی‌شود.');
}
// 19 Accepted C010 correctness results; build only after independent scale validation.
{
 const s=base('ممیزی مستقل پس از حذف تعداد خارجی',{note:'گیت مستقل C010 شامل ۱۲۵ ورودی یکتای ثابت و سه پیش‌آزمون است. ۱۲۸ فراخوانی با کل مجموعهٔ افرازهای مرجع برابر شد؛ ۲۲۳۱۰ سطر افراز و ۲۲۴۳۸ شاهد تصویر بازپخش شد. چهار آزمون مقیاس مستقل پس از گیت اجرا و اعتبارسنجی شدند. ۱۴ و ۶۴ نمادی با گراف sound و آزمون اتم‌ها، شمارش بسته دارند. ۱۰ نمادی گراف خالی دارد و DP دقیق ۵۲ جواب می‌دهد. طول ۴۰۹۶ یک ورودی جدا با چهار نماد است. هیچ نتیجهٔ دقت آماری روی سخت‌افزار واقعی، مقایسهٔ سرعت یا تضمین ظرفیت عمومی ادعا نمی‌شود.',sources:['results/2026-11-02/partition_unrestricted_v10/audit/provider_validation_v2.json','results/2026-11-02/partition_unrestricted_v10/audit/AUDIT_FINAL_V1.md']});
 box(s,'برابریِ کل خانوادهٔ جواب‌ها در صدوبیست‌وهشت آزمون',90,160,1100,65,{size:35,bold:true});
 table(s,[['افراز سازگار','روش','اندازه','نوع ورودی'],['877','شمارش بسته','14','تعداد نماد'],['4140','شمارش بسته','64','تعداد نماد'],['52','برنامه‌ریزی پویا','10','تعداد نماد'],['5','برنامه‌ریزی پویا','4096','طول تریس']],{y:260,h:295,widths:[240,410,200,280],latin:[0,2],size:29});
 caption(s,'این چهار آزمون، تضمین پوششِ همهٔ داده‌های هم‌اندازه نیستند.');
}
// 20 Conclusion
{
 const s=base('مالکیت جزئیِ قطعی با تعدادِ نامعلوم',{note:'جمع‌بندی: شمار و روابط مالکیت را می‌توان بدون تعداد خارجی محاسبه کرد. در کلاس نامقید، مالکیت واقعی چندبلوکی به‌طور عمومی شناسایی نمی‌شود، اما forced-same و countermodels قطعی می‌مانند. اتم‌سازی sound و فرمول بسته یا DP هرس‌شده هزینه را کم می‌کنند؛ تضمین چندجمله‌ای یا برتری عمومی ادعا نمی‌شود. منابع و اجرای بازتولیدپذیر در مخزن خصوصی پروژه‌اند.',sources:['results/2026-11-02/partition_identification_v8/RESULT_FA.md','results/2026-11-02/partition_unrestricted_v10/coordination/CONTRACT.md']});
 lines(s,['تمام توضیح‌های سازگار را مبنای نتیجه قرار می‌دهیم.','از اجبارهای اثبات‌شده برای کاهش محاسبه استفاده می‌کنیم.','هر ابهام یا اجرای ناتمام را صریح گزارش می‌کنیم.'],{y:175,gap:116,size:35});
 box(s,'github.com/Mahdi-Jadidi/passive-automata-learning',90,600,1100,45,{size:25,font:'Consolas',align:'center',color:C.teal});
}
// 21 Backup: exact quantifier order.
{
 const s=base('ترتیب کمیت‌گذارها در شرط سازگاری',{appendix:true,note:'برای هر منفی باید یک بلوک وجود داشته باشد که آن منفی را از تمام مثبت‌ها جدا کند. انتخاب یک بلوک متفاوت برای هر مثبت کافی نیست. مثال P={a,b},N={epsilon} و افراز a|b: روی هر بلوک epsilon مثبتاً مجبور است، اما تأمین‌کنندهٔ تصویر در دو بلوک دو مثبت متفاوت است. در نتیجه split مردود است.',sources:['results/2026-11-02/partition_coverage_v9/theory/PROOFS_v1.md']});
 formula(s,'∀ n   ∃ B   ∀ p : π_B(n) ≠ π_B(p)',160,{size:43});
 table(s,[['روی b','روی a','کلمهٔ مثبت'],['ε','a','a'],['b','ε','b']],{y:375,h:195,widths:[380,380,370],latin:[0,1,2],size:35});
 formula(s,'P = {a,b}     N = {ε}',267,{size:35});caption(s,'پذیرشِ تصویر تهی در هر دو بلوک اجبار شده است.');
}
// 22 Backup: correctness proof.
{
 const s=base('اثباتِ شمارش دقیق',{appendix:true,note:'استقرا روی تعداد نمادهای باقی‌مانده: تهی فقط با پوشش تمام منفی‌ها و t0 یک جواب دارد. در حالت ناتهی هر افراز یک بلوک یکتا حاوی کمینه دارد. حذفش، زیرمسئلهٔ کوچکتری می‌دهد. بالعکس هر تکمیل فرزند با بلوک انتخاب‌شده یک افراز معتبر است. شاخه‌های متفاوت بلوک کمینهٔ متفاوت دارند، پس دوباره‌شماری نداریم. lazy mask باید دقیق و مبتنی بر تمام مثبت‌های ثابت باشد.',sources:['results/2026-11-02/partition_coverage_v9/theory/PROOFS_v1.md']});
 lines(s,['پایه: افراز تهی تنها در پایانِ کامل یک جواب می‌دهد.','گام: هر افراز، یک بلوکِ یکتا حاوی کمینه دارد.','تناظرِ شاخه و تکمیل، هم کامل است و هم بدون تکرار.'],{y:185,gap:120,size:35});
 caption(s,'اثبات صحت الگوریتم با آزمون تجربیِ پیاده‌سازی دو نقش متفاوت دارند.');
}
// 23 Backup: pair recurrence.
{
 const s=base('بازگشتِ شمارش هم‌مالکیت',{appendix:true,note:'در شاخهٔ B اگر هر دو نماد داخل B باشند، تمام childCount تکمیل هم‌بلوکی دارند. اگر هر دو در rem\B باشند childQ را حمل می‌کنیم. در صورت تقسیم بین B و مابقی سهم صفر است. اگر نماد از state خارج شده childQ آن زوج باید صفر باشد؛ در پیاده‌سازی این invariant جلوی دوباره‌شماری را می‌گیرد. بعد روی همهٔ تعدادها جمع می‌شود.',sources:['results/2026-11-02/partition_coverage_v9/theory/PROOFS_v1.md']});
 table(s,[['سهم هم‌بلوکی','وضعیت دو نماد'],['تعداد کل تکمیل‌های فرزند','هر دو در بلوک انتخابی'],['شمار هم‌بلوکیِ فرزند','هر دو در باقی‌مانده'],['0','یکی در بلوک انتخابی و دیگری بیرون']],{h:330,widths:[630,500],size:31});
 caption(s,'برای زوج مبهم، یک شاهد هم‌بلوک و یک شاهدِ جدا ارائه می‌شود.');
}
// 24 Backup: stronger finite-data limit.
{
 const s=base('مثال نقض با عوامل تجزیه‌ناپذیر',{appendix:true,note:'برای هر طول مشاهده L، عدد M با4M>L انتخاب کنید. E_xy زبان زوجیت هر دو حرف است. F_xy=E_xy منهای تنها واژه x^(2M)y^(2M) منظم، نامتناهی و prime است، چون تصویرهای تک‌حرفی همان even stars هستند ولی حاصل‌ضربشان واژه حذف‌شده را می‌پذیرد. دو مدل ab|cd و ac|bd با این عوامل روی تمام واژه‌های طول≤L یکسان‌اند و در a^(2M)b^(2M) تفاوت دارند. بنابراین حتی معلوم بودن k2 و prime بودن عوامل برای تضمین عمومی از هر افق متناهی کافی نیست، با DFA size نامحدود. این ناممکنی برای همهٔ نمونه‌ها نیست؛ گواه‌های خاص ممکن‌اند.',sources:['results/2026-11-02/partition_identification_v8/theory/PROOFS_v1.md','results/2026-11-02/partition_identification_v8/audit/COUNTEREXAMPLE_AUDIT_REPORT_V1.md']});
 box(s,'زبان پایه: تعداد هر دو نماد زوج است.',90,145,1100,55,{size:30});formula(s,'F_xy = E_xy ∖ { x^(2M) y^(2M) }',215,{size:41});
 formula(s,'ab / cd             ac / bd',345,{size:54});
 box(s,'دو سامانه تا افقِ متناهیِ مشاهده هم‌رفتارند.',90,465,1100,70,{size:33});formula(s,'4M > L       w = a^(2M)b^(2M)',525,{size:36});
}

assertCount();
function assertCount(){if(p.slides.items.length!==24)throw Error('Expected 24 authored slides');}
await fs.writeFile(path.join(ROOT,'private/speaker_notes_R5.json'),JSON.stringify(notes,null,2));
await fs.writeFile(path.join(ROOT,'private/build_contract_R5.json'),JSON.stringify({slides:24,tableOwners,fontPolicy:{basis:'design',families:['Arial','Consolas','Cambria Math']},size:{width:1280,height:720},sources:'Research C008/C009/C010; C010 exact gate and four scale cells independently accepted'},null,2));
await (await PresentationFile.exportPptx(p)).save(path.join(ROOT,'private/candidate_R5.pptx'));
await fs.writeFile(path.join(ROOT,'private/deck_R5.json'),JSON.stringify(p.toProto()));
console.log(JSON.stringify({createdSlides:p.slides.items.length,nativeTableSlides:tableOwners,candidate:path.join(ROOT,'private/candidate_R5.pptx')}));
