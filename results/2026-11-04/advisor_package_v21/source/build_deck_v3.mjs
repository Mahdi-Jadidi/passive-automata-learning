import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const runtime='C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const skill='C:/Users/Mahdi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const {Presentation,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const {applyPresentationChartFont}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const ROOT=fileURLToPath(new URL('../',import.meta.url));
const REPO=path.resolve(ROOT,'../../..');
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={ink:'#142A3B',teal:'#027D83',paper:'#F7F7F2',white:'#FFFFFF',gray:'#526471',line:'#D9E0E3',red:'#A74332'};
const notes=[],tables=[],charts=[];
const SOURCE_URL='https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/';
function text(s,t,x,y,w,h,{size=34,font='Arial',color=C.ink,align='right',bold=false}={}){
 const a=s.shapes.add({name:'text-'+s.id+'-'+s.shapes.items.length,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 a.text=t;a.text.style={fontSize:size,typeface:font,color,alignment:align,verticalAlignment:'middle',bold,autoFit:'none',wrap:'square',insets:0};return a;
}
function base(title,{note='',sources=[],appendix=false,dark=false}={}){
 const s=p.slides.add();s.background.fill=dark?C.ink:C.paper;
 text(s,title,72,42,1136,90,{size:47,bold:true,color:dark?C.white:C.ink});
 text(s,String(p.slides.items.length).padStart(2,'0'),72,665,70,28,{size:20,font:'Consolas',align:'left',color:dark?'#C2D8DF':C.gray});
 if(appendix)text(s,'پشتیبان',1070,665,138,28,{size:20,color:dark?'#C2D8DF':C.gray});
 s.speakerNotes.text=note+'\n\n'+sources.map(x=>'منبع: '+(x.startsWith('http')?x:SOURCE_URL+x)).join('\n');
 notes.push({slide:p.slides.items.length,title,notes:s.speakerNotes.text});return s;
}
function lines(s,items,{y=185,gap=110,size=34,color=C.ink}={}){items.forEach((a,i)=>text(s,a,90,y+i*gap,1100,86,{size,color}));}
function formula(s,t,y=240,{size=43,color=C.teal}={}){text(s,t,82,y,1116,110,{size,font:'Cambria Math',align:'center',color});}
function caption(s,t,{y=590,color=C.gray,size=26}={}){text(s,t,90,y,1100,60,{size,color});}
function table(s,values,{y=175,h=370,widths,size=28,latin=[],highlight=[]}={}){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:75,top:y,width:1130,height:h,values,...(widths?{columnWidths:widths}:{})});
 t.borders.assign({fill:C.line,width:1});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
  const q=t.getCell(r,c);q.fill=r===0?C.ink:(highlight.includes(r)?'#E0F0EC':C.white);
  q.text.style={typeface:latin.includes(c)&&r>0&&!/[\u0600-\u06ff]/.test(values[r][c])?'Consolas':'Arial',fontSize:size,color:r===0?C.white:C.ink,bold:r===0,alignment:'center',verticalAlignment:'middle',insets:8};
 }
 tables.push(p.slides.items.length);return t;
}
const report='results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md';
const proof='results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md';
{
 const s=p.slides.add();s.background.fill=C.ink;
 s.images.add({blob:new Uint8Array(await fs.readFile(path.join(REPO,'results/2026-11-02/presentation_v1/assets/cover.png'))),contentType:'image/png',position:{left:0,top:0,width:1280,height:720},fit:'cover',alt:'تصویر مفهومی تولیدشده با هوش مصنوعی از رشته‌های رویداد درهم‌تنیده'});
 text(s,'افراز الفبا از\nتریس‌های درهم‌تنیده',480,175,725,205,{size:65,bold:true,color:C.white});
 text(s,'شرایط شناسایی، الگوریتم دقیق و ارزیابی مقیاس',470,405,730,100,{size:33,color:'#BEE5E1'});
 text(s,'گزارش پیشرفت پژوهش برای جلسه با استاد',520,560,680,55,{size:27,color:'#C2D8DF'});
 s.speakerNotes.text='زمان اصلی حدود۲۰دقیقه است و سه اسلاید آخر برای پرسش‌ها نگه داشته شده‌اند. هدف اولیه کاهش مسئلهٔ یادگیری اتوماتای چند مؤلفه با افراز الفبا بود. امروز بخش افراز، شرایط قطعیت و آزمایش دقیق را ارائه می‌کنیم. اثر انتهابه‌انتها بر RPNI هنوز آزمایش نشده است. تصویر جلد از ارائهٔ قبلی پروژه و تولیدشده با هوش مصنوعی است؛ داده یا تصویر سامانهٔ واقعی نیست.';
 notes.push({slide:1,title:'افراز الفبا از تریس‌های درهم‌تنیده',notes:s.speakerNotes.text});
}
{
 const s=base('مسئله و دستاورد فعلی',{note:'انگیزه، جلوگیری از آمیختن رفتار مؤلفه‌ها پیش از یادگیری محلی است. انفجار فضای حالت RPNI در این بسته نتیجهٔ تجربی نیست. سهم قابل‌دفاع فعلی: یک صورت‌بندی صریح، شرط لازم‌وکافیِ وجود توضیح منظم، گواه‌های قابل‌بررسی برای شناسایی، حل‌گر دقیق و بهینه‌سازی‌های هم‌ارز با ممیزی مستقل. اصالت علمی نسبت به تمام پیشینه هنوز اثبات نشده است.',sources:[report]});
 lines(s,['ورودی: تریس‌های برچسب‌دار از رویدادهای درهم‌تنیده','خروجی: افراز یکتا، ابهامِ شاهددار، ناسازگاری یا ناتمام','دستاورد فعلی: حل دقیق و گواه قابل‌بررسی تحت فرض‌های صریح'],{gap:115,size:34});
 caption(s,'ارزیابیِ اثر افراز بر یادگیری RPNI، مرحلهٔ بعدی پژوهش است.');
}
{
 const s=base('مدل و فرض‌های پژوهش',{note:'الفبای مشاهده‌شده معلوم است ولی مالکیت نمادها مجهول است. هر نماد دقیقاً یک مالک دارد. فرض مدل این است که پذیرش کل، هم‌زمانی پذیرش همهٔ تصاویر محلی باشد. این فرض با برچسب موفقیت آخرین رویداد یکی نیست. مثبت و منفی، برچسب کل کلمه‌اند؛ نبود یک تریس در لاگ، منفی نیست. تعداد حالت عامل‌ها کران ندارد. اگر K داده شود، صحتش فرض خارجی است.',sources:[report,proof]});
 table(s,[['معنا','فرض'],['الفبا معلوم است و هر نماد یک مالک دارد','مالکیت مجزا'],['پذیرش کل برابر پذیرش همهٔ تصاویر محلی است','عوامل مستقل'],['مثبت و منفی، برچسب دقیقِ کل کلمه‌اند','دادهٔ بدون نویز'],['کران حالت نداریم؛ تعدادِ داده‌شده باید معتبر باشد','زبان‌های منظم']],{h:365,widths:[760,370],size:29});
 caption(s,'این مدل باید پیش از کاربرد روی لاگ واقعی با معنای داده تطبیق داده شود.');
}
{
 const s=base('تصویر تریس روی یک بلوک',{note:'π_B تمام نمادهای خارج بلوک را حذف می‌کند و ترتیب نمادهای داخل بلوک را حفظ می‌کند. برای بلوک ab اختلاف مثبت و منفی آشکار است؛ بلوک ac اختلاف را از دست می‌دهد. مسئله پیدا کردن بلوک‌هایی است که تمام برچسب‌ها را هم‌زمان توضیح بدهند، نه صرفاً خوشه‌بندی شباهت رشته‌ها.',sources:['docs/ALGORITHM_TUTORIAL_FA.md']});
 table(s,[['تصویر محلی','بلوک','تریس'],['ab','{a,b}','abcd'],['ba','{a,b}','bacd'],['ac','{a,c}','abcd'],['ac','{a,c}','bacd']],{h:365,widths:[380,370,380],latin:[0,1,2],size:34,highlight:[1,2]});
 caption(s,'تصویر فقط رویدادهای خارج بلوک را حذف می‌کند.');
}
{
 const s=base('شرط لازم و کافیِ سازگاری',{dark:true,note:'قضیه برای زبان‌های منظم بدون کران حالت و دادهٔ متناهی است. ضرورت: هر عامل باید همهٔ تصاویر مثبت را بپذیرد؛ هر منفی باید در یک عامل رد شود، پس تصویرش در همان عامل جزو تصاویر مثبت نیست. کفایت: زبان عامل را خود مجموعهٔ متناهی H(B) قرار دهید؛ متناهی و در نتیجه منظم است. این زبان شاهد، زبان واقعی دستگاه را بازیابی نمی‌کند. ترتیب کمیت‌گذارها حیاتی است: برای یک منفی، یک بلوک باید از تمام مثبت‌ها متمایزش کند.',sources:[proof]});
 formula(s,'H(B) = { π_B(p) : p ∈ P }',170,{color:C.white});
 formula(s,'∀n ∈ N   ∃B ∈ Π   ∀p ∈ P : π_B(n) ≠ π_B(p)',325,{size:37,color:'#BEE5E1'});
 caption(s,'هر منفی باید در یک بلوک از همهٔ مثبت‌ها متمایز شود.',{color:'#C2D8DF'});
}
{
 const s=base('مثالِ افراز یکتا با تعداد معلوم',{note:'P فقط abcd است. منفی bacd تنها با جابه‌جایی a,b فرق دارد؛ اگر دو نماد در بلوک‌های جدا باشند، هر بلوک همان تصویر مثبت را می‌بیند، پس a,b مجبورند هم‌مالک باشند. منفی abdc همین را برای c,d ثابت می‌کند. با K2 تنها افراز ab/cd می‌ماند و با معیار تصویر سازگار است. بدون K، افراز تک‌بلوکی نیز سازگار است و نتیجه مبهم می‌شود.',sources:[proof]});
 formula(s,'P = {abcd}     N = {bacd, abdc}     K = 2',150,{size:38});
 table(s,[['نتیجهٔ لازم','شاهد برچسب‌دار'],['{a,b}','abcd / bacd'],['{c,d}','abcd / abdc'],['{a,b} / {c,d}','با تعدادِ دو، تنها نامزد سازگار']],{y:295,h:270,widths:[520,610],size:29,latin:[1],highlight:[3]});
 caption(s,'بدون K معتبر، ادغام هر دو گروه نیز توضیح سازگاری است.');
}
{
 const s=base('پیش‌آزمونِ گواه‌دار پیش از جست‌وجوی کامل',{note:'از جابه‌جایی‌های مثبت/منفی، گراف هم‌مالکی لازم می‌سازیم و مؤلفه‌ها را اتم می‌نامیم. هر جواب باید ادغامی از اتم‌ها باشد. اگر r<K هیچ جواب نیست. اگر r=K دقیقاً یک نامزد داریم؛ سازگاری آن یکتایی و ناسازگاری آن عدم وجود جواب را ثابت می‌کند. اگر افراز اتم‌ها سازگار و1<K<r باشد، تمام S(r,K) ادغام سازگارند و ابهام ثابت است. اگر افراز اتم‌ها ناسازگار وK<r باشد، پیش‌آزمون تصمیم نمی‌گیرد. K1 حالت جدا و مستقیم است.',sources:[proof]});
 table(s,[['نتیجه','شرط روی تعداد اتم‌ها r'],['ناسازگار','r < K'],['یکتا اگر سازگار؛ ناسازگار اگر رد شود','r = K'],['مبهم، اگر افراز اتم‌ها سازگار باشد','1 < K < r'],['نیازمند جست‌وجو، اگر افراز اتم‌ها ناسازگار باشد','K < r']],{h:360,widths:[710,420],size:27,latin:[1]});
 caption(s,'وجود گواه کافی تصمیم می‌دهد؛ نبود آن، ابهام داده را اثبات نمی‌کند.');
}
{
 const s=base('یکتا، مبهم و ناتمام معنای متفاوت دارند',{note:'یکتایی فقط با اثبات گواهی یا پایان جست‌وجوی دقیق اعلام می‌شود. دو افراز متفاوت با شاهد سازگاری برای اثبات ابهام کافی‌اند. ناسازگاری به صفر جواب با گواه کامل نیاز دارد. پایان مهلت نتیجهٔ اطلاعاتی نیست و وضعیت unresolved می‌دهد. بدون K، هر نمونهٔ متناهی بدون تناقض P∩Nتهی، توضیح تک‌بلوکی با زبان P دارد؛ پس وجود هر توضیح چندبلوکی، ابهام معماری ایجاد می‌کند.',sources:[report,proof]});
 table(s,[['شاهد لازم','وضعیت'],['تنها افراز سازگار، با گواه یا جست‌وجوی کامل','یکتا'],['دو افراز متفاوتِ مستقلاً سازگار','مبهم'],['اثبات نبود هیچ افراز تحت فرض‌ها','ناسازگار'],['کار محاسباتی به پایان نرسیده است','ناتمام']],{h:360,widths:[810,320],size:29});
 caption(s,'ناتمام‌بودن اجرا، ابهامِ داده یا شکستِ قضیه نیست.');
}
{
 const s=base('الگوریتم دقیقِ فعلی',{note:'ابتدا schema، نمادها، برچسب‌های متناقض و شمارش بررسی می‌شوند. اگر برای هر منفی یک نماد با شمارش غایب از تمام مثبت‌ها وجود داشته باشد، همهٔ افرازها سازگارند و میان‌بُر دقیق داریم. سپس گراف جابه‌جایی و اتم‌ها ساخته می‌شوند. برای بلوکB مجموعهٔ R(B)منفی‌های قابل رد ذخیره می‌شود. اگر افراز اتم‌ها جواب ندهد، DFS با نمایش restricted-growth همهٔ ادغام‌های اتم‌ها را بدون دوباره‌شماری جست‌وجو می‌کند. تعداد بلوک‌ها کران ایمن می‌دهد، cacheماسک‌ها سقف4096دارد، جست‌وجو با دو شاهد متوقف می‌شود. سقف زمان خروجی ناتمام دارد. این نسخه gateاست و همهٔ جواب‌ها را فهرست نمی‌کند؛ حل‌گر مرجع قدیمی برای خانواده‌های کوچک باقی مانده است.',sources:['results/2026-11-04/scaling_v20/implementation/candidate_c2_v1/gate_v1.py']});
 lines(s,['۱. اعتبارسنجی و میان‌بُرهای اثبات‌شده','۲. گراف هم‌مالکی، اتم‌ها و آزمون سازگاری آن‌ها','۳. در صورت نیاز، جست‌وجوی دقیقِ ادغام اتم‌ها','۴. توقف با گواه یکتایی، دو شاهد، نبود جواب یا پایان مهلت'],{y:160,gap:101,size:32});
 caption(s,'خروجی فعلی تصمیم و گواه است؛ فهرست تمام افرازها را تولید نمی‌کند.');
}
{
 const s=base('دو بهینه‌سازی با حفظ جواب دقیق',{note:'C1از Counterهای مرحلهٔ اعتبارسنجی، طول و بردار دقیق شمارش را نگه می‌دارد. جابه‌جایی مجاور این امضا را حفظ می‌کند، پس فقط زوج‌های هم‌امضا به آزمون دقیق swap می‌روند. ترتیب P,N و شاهدها حفظ است و کل داده در قیود باقی می‌ماند. C2بعد از اعتبارسنجی کامل، با نگاشت ord(symbol)بهNoneنمادهای خارج بلوک را حذف می‌کند. translateروی قطعات16384کدپوینتی، با اتصال همان ترتیب، دقیقاً projectionاست چون تصویر همریختیِ الحاق است. هیچ تصمیم تقریبی بر اساس برخورد هش نداریم. این تغییرها ضریب اجرای محاسبه را هدف می‌گیرند، نه حذف نمایی جست‌وجو.',sources:['results/2026-11-04/scaling_v20/theory/SOURCE_REVIEW_C1_V1.md','results/2026-11-04/scaling_v20/theory/SOURCE_REVIEW_C2_V1.md']});
 text(s,'فیلتر دقیقِ شمارش نمادها',90,165,1100,70,{size:38,bold:true});
 text(s,'جفت‌های با شمارش متفاوت، شاهدِ جابه‌جایی مجاور نیستند.',90,245,1100,80,{size:32});
 text(s,'تصویرسازی بومیِ رشته',90,365,1100,70,{size:38,bold:true});
 text(s,'حذف نمادهای خارج بلوک، با حفظ ترتیب و بررسی مهلت.',90,445,1100,80,{size:32});
 caption(s,'هر دو تغییر، مجموعهٔ افرازهای سازگار را حفظ می‌کنند.');
}
{
 const s=base('مجموعهٔ ارزیابی و شیوهٔ تولید',{note:'۴ورودی و۶حالت زمان‌گیری ثابت بودند. پایهٔ A512، B128 وC16کلمه در هر برچسب دارد؛ سپس1مثبت وKمنفیِ شاهد افزوده می‌شود. دستگاه‌ها چرخهٔ کامل aو جایگشت تصادفی ناجابجاپذیرbدارند، فقط حالت0پذیرنده است. aهمهٔ حالت‌ها را قابل‌دسترسی و با پسوندهای متفاوت متمایز می‌کند؛ همهٔ حالت‌ها در دادهٔ پایه بازدید شده‌اند. پیشوندهای تصادفی با ادامهٔ ترمیمی تولید مثبت/منفی می‌کنند و لنگرهای جابه‌جایی عمدی‌اند. این نمونه‌گیری منفعلِ بدون شرط از دنیای واقعی نیست. Dعامل متناهی{epsilon,a^128b^128}با258حالت کمینه و گرافswapخالی است. اطلاعات worldهرگز به حل‌گر وارد نمی‌شود.',sources:['results/2026-11-04/scaling_v20/audit/FIXTURE_AUDIT_V1.json','results/2026-11-04/scaling_v20/audit/PROTOCOL_V1.md']});
 table(s,[['کل نمادهای تریس‌ها','حالت کمینهٔ هر دستگاه','تعداد دستگاه','ورودی'],['4,066,861','64','4','A'],['16,537,492','256','8','B'],['32,338,004','1024','20','C'],['2,048','258','4','D']],{h:340,widths:[390,340,260,140],latin:[0,1,2,3],size:29});
 caption(s,'داده‌ها شرطی و شاهددارند؛ بلندترین تریس واقعی ۹۹۲٬۶۲۲ نماد دارد.');
}
{
 const s=base('کاهش زمان روی ورودی A',{note:'نمودار فقط اجراهای کامل و میانهٔ۳فرایند تازه را مقایسه می‌کند. باK4، پایه6.4033247,C1=5.6533418,C2=.6578987ثانیه؛ نسبت پایه/C2=9.73299است. بدونK، پایه8.5326166,C1=7.107165,C2=.6479559؛ نسبت13.1685است و نتیجه مبهم صحیح است. زمان انتهابه‌انتها شامل خواندن و پیش‌پردازش و خروجی است. این نمودار، پروفایل یا میانگین همهٔ ورودی‌ها نیست.',sources:[report]});
 const ch=s.charts.add('bar',{position:{left:90,top:170,width:1100,height:375},categories:['K unknown','K = 4'],series:[{name:'C018',values:[8.5326166,6.4033247],fill:'#536372'},{name:'C1',values:[7.107165,5.6533418],fill:'#B87819'},{name:'C2',values:[.6479559,.6578987],fill:'#027D83'}],hasLegend:true,barOptions:{direction:'column',grouping:'clustered'},legend:{position:'bottom',textStyle:{fontSize:22}},xAxis:{textStyle:{fontSize:24}},yAxis:{min:0,max:10,majorUnit:2,numberFormatCode:'0',textStyle:{fontSize:22}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.00',textStyle:{fontSize:24}},chartFill:C.paper,plotAreaFill:C.paper});
 applyPresentationChartFont(ch,{fontFamily:'Arial'});charts.push(p.slides.items.length);
 caption(s,'زمان کل بر حسب ثانیه، میانهٔ سه اجرا؛ با K=4 حدود ۹٫۷۳ برابر سریع‌تر.');
}
{
 const s=base('تکمیل اجراهای بزرگ و بازیابی ۲۰ دستگاه',{note:'سقف نرم20و سخت25ثانیه بود. B_K8پایه وC1درهر۳تکرارunresolvedوC2درهر۳unique؛ میانه C2=3.1736438s. C_unknownپایه وC1درهر۳unresolvedوC2درهر۳ambiguous؛ میانه7.9419305s. برای موارد سانسورشده ضریب سرعت عددی نمی‌سازیم. کنترلC_K20بعد از پذیرش مجموعه، جداگانه و ازپیش‌ثبت‌شده اجرا شد:unique،5.2844308sیک اجرا، نه میانه و نه بخشی از54زمان‌گیری. شاهد20مؤلفه به‌علاوه K20و سازگاری، یکتایی را اثبات کرد. نتیجه نسبت به مدل و شاهدهای عمدی شرطی است، نه نرخ بازیابی عمومی.',sources:[report,'results/2026-11-04/scaling_v20/coordination/k20_functional_control_v1/result.json']});
 table(s,[['نتیجهٔ C2','C2، ثانیه','مبنا','حالت'],['یکتا','3.174','ناتمام در ۲۰ ثانیه','B / K=8'],['مبهم','7.942','ناتمام در ۲۰ ثانیه','C / unknown K']],{y:175,h:245,widths:[250,230,390,260],size:28,latin:[1,3]});
 text(s,'با تعداد معلومِ ۲۰: افراز یکتا در ۵٫۲۸۴ ثانیه',90,455,1100,83,{size:35,bold:true,color:C.teal});
 caption(s,'کنترل ۲۰دستگاهی یک اجراست و در نسبت‌های سه‌تکراری وارد نشده است.');
}
{
 const s=base('صحت مستقل و نتیجهٔ منفیِ کارایی',{note:'۱۷۱۰حالت برای هر۳provider، جمع۵۱۳۰بررسی مستقل با صفرخطا؛ مرجع کاملِ خانوادهٔ افرازها برای نمونه‌های کوچک و replayگواه برای همهٔ اجراهای کامل. 54زمان‌گیری و6اجرای حافظه انجام شد. این اعداد نرخ دقت روی دنیای واقعی نیستند. DباknownK4هرسهuniqueشدند اما زمانwallپایه.8118161وC2.9735871یعنی19.93درصد افزایشزمان. pipelineهمانDاز.247363به.0695816کاهش یافت؛ داده برای تبیین علّی هزینهٔ بیرونpipelineکافی نیست. tracemallocDاز1,868,664به1,967,923بایت افزایش یافت؛RSSنیست. Aزیرtracemallocپایه/C1ناتمام وC2کاملند، پس نسبت اوج حافظهٔ کامل معتبر نیست.',sources:[report,'results/2026-11-04/scaling_v20/audit/benchmark_runs/20261104T120316.506188Z/validation_report.json']});
 text(s,'۵۱۳۰ بررسی مستقل، بدون اختلاف ثبت‌شده',90,160,1100,85,{size:40,bold:true,color:C.teal});
 table(s,[['C2','مبنا','کنترل کوچک D'],['0.974 s','0.812 s','زمان کل'],['1.968 MB','1.869 MB','اوج حافظهٔ پایتون']],{y:295,h:220,widths:[340,340,450],latin:[0,1],size:31});
 caption(s,'در کنترل کوچک، زمان کل حدود ۲۰٪ افزایش یافت.');
}
{
 const s=base('مرتبهٔ زمانی و مرز مقیاس‌پذیری',{note:'Tتعدادکلنمادها,mاندازهالفبا,rاتم‌هاوLmaxطولبلندترینواژه است. خواندنورودیحداقلخطی در حجمآن است. فیلترParikhدر بدترین حالت امضاهای برابر زوج‌هایP*Nرا حذفنمی‌کند و اسکنswapتاO(P*N*Lmax)می‌رود. تصویرها همچنان خطی در حجمپردازش‌شده‌اند ولی عملیاتnativeضریب را کم کرده است. تعداد افرازهایاتم‌هاBell(r)، درلایهK برابرS(r,K)است؛ نمایشRGSو توقفدو شاهد بدترینحالتترکیبی را حذفنمی‌کند. روی A/B/Cگواهفوراًکافی است وDFSصفرگره دارد؛ پس اینها شاهد حل جست‌وجوی سختنیستند. حالت زیاد دستگاه مولد را نباید با تعداد گره‌های جست‌وجو یکی گرفت.',sources:[report,'results/2026-11-04/scaling_v20/theory/EXACT_SCALING_PROPOSAL_v1.md']});
 formula(s,'T = input characters       r = forced components',160,{size:37});
 lines(s,['خواندن و تصویرسازی همچنان حجم ورودی را پردازش می‌کنند.','فیلتر شمارش در بدترین حالت، همهٔ جفت‌ها را نگه می‌دارد.','شمار افرازهای بالقوه، ترکیبی است و با تعداد اتم‌ها رشد می‌کند.'],{y:290,gap:94,size:32});
 caption(s,'بزرگیِ DFA مولد، به‌تنهایی شاهدِ سختی جست‌وجوی مشاهده‌شده نیست.');
}
{
 const s=base('مسیر پژوهش برای تصمیم استاد',{note:'نتیجهٔ قابل ارائه امروز: معیار سازگاری و گواه شناسایی تحت مدل صریح، حل‌گر دقیق با وضعیت ناتمام صادقانه، بهینه‌سازی اثبات‌شده و ممیزی بازتولیدپذیر. بررسی جامع نوآوری هنوز باز است و نباید اینها را قضیهٔ جدید نسبت به تمام ادبیات معرفی کنیم. پیشنهاد تصمیم جلسه: آیا تمرکز پایان‌نامه روی شناسایی‌پذیری و گواه‌ها باشد یا کاهش هزینهٔ جست‌وجوی دقیق یا کاربرد روی لاگ طبیعی؟ کارآزمایش بعدی باید اثر افراز برRPNIرا رویخطپایۀهمسان بسنجدو شاهدهایطبیعی را ازلنگرهایعمدی جدا کند. مدلبرچسبمقالهLANCERباپذیرشANDیکساننیست؛ هدفمقالهفعلاًبهدرخواستکاربرمتوقفاست.',sources:[report]});
 lines(s,['تعیین سهم نوآورانه با مقایسهٔ دقیقِ پیشینه','ارزیابی افراز در کنار RPNI روی دادهٔ همسان','کاهش وابستگی به شاهدهای عمدی و تطبیق مدل با لاگ طبیعی'],{gap:115,size:35});
 caption(s,'حل‌گر و شواهد آمادهٔ بررسی‌اند؛ ادعای حل عمومیِ مالکیت واقعی نداریم.');
}
{
 const s=base('پشتیبان: ترتیب کمیت‌گذارها',{appendix:true,note:'P={bacd,abdc}وN={abcd}،K2. swapهاabوcdرا مجبور می‌کنند. اماπ_ab(n)=abبرابر تصویرمثبتabdcاستوπ_cd(n)=cdبرابر تصویربهpositivۀbacdاست. پس هیچ بلوکیمنفیراازهمهٔمثبت‌هاجدا نمی‌کندوافرازاجباریناسازگاراست. بررسیِبرایهرمثبتیکبلوکمتمایز،به‌اشتباهقبولمی‌کند. اینیکمثالنقضِمستقلبه جابه‌جایی∃Bو∀pاست.',sources:[proof]});
 formula(s,'P = {bacd, abdc}     N = {abcd}     K = 2',160,{size:38});
 table(s,[['مثبت هم‌تصویر','تصویر منفی','بلوک'],['abdc','ab','{a,b}'],['bacd','cd','{c,d}']],{y:310,h:210,widths:[420,340,370],latin:[0,1,2],size:33});
 caption(s,'دو گروه اجباری داریم، اما هیچ افراز سازگاری با K=2 نداریم.');
}
{
 const s=base('پشتیبان: تعداد نمونه تضمین یکتایی نیست',{appendix:true,note:'برای هرp,qمثبت،نمونه‌هایP_i=a^(2i)bcdوN_j=a^(2j+1)bcdهمهٔنمادها رادارند ویکتاهستند. درهرمنفی تعدادaفرد ودرتماممثبت‌ها زوجاست؛ هر افراز بلوکی شاملaدارد که آنمنفیرا رد می‌کند. برایΣabcd,K2هر۷افراز سازگار است. پس حداقلِصرفِتعدادمثبت/منفییاطول نمی‌تواندیکتاییرا تضمینکند. مثال فشردهٔهم‌خلاصه: Pabcd,Nbacd/abdcیکتاولیNbacd/badcسه جوابab/cd,abc/d,abd/cدارد؛ تعدادنمونه وطولوشمارهرنمادیکساناست.',sources:[proof,'results/2026-11-04/preflight_certificates_v19/theory/MATCHED_SUMMARY_COUNTEREXAMPLE_v1.md']});
 formula(s,'P_i = a^(2i)bcd       N_j = a^(2j+1)bcd',185,{size:43});
 lines(s,['هر تعداد نمونهٔ یکتا و هر طول دلخواه ممکن است مبهم بماند.','نوعِ شاهدهای مشاهده‌شده تعیین‌کننده است.'],{y:360,gap:110,size:35});
 caption(s,'برای افراز دوبخشیِ چهار نماد، این خانواده هر ۷ جواب را حفظ می‌کند.');
}
{
 const s=base('منابع و جایگاه در پیشینه',{appendix:true,note:'منابع بیرونی این اسلاید پس از بررسی مستقل در audit/SOURCES_V1.jsonثبت می‌شوند. مسیرهای پروژه، اثبات و آزمایش را ثبت می‌کنند و جای مرور جامع نوآوری را نمی‌گیرند. RPNIمرجع بخش یادگیری محلی آینده است. منابع شناسایی‌پذیری را نباید بدون بررسیِتفاوت مدل، اثبات مشکل خاص ما معرفی کرد.',sources:[report,proof,'docs/ALGORITHM_TUTORIAL_FA.md']});
 ['Oncina & Garcia (1992): passive DFA inference','Gold (1967): language identification in the limit','Angluin (1987): queries and counterexamples','Jecker et al. (2021): permutation automata decomposition'].forEach((v,i)=>text(s,v,90,170+i*88,1100,75,{size:29,align:'left'}));
 caption(s,'ارجاع‌های دقیق و پیوندها در یادداشت این اسلاید و راهنمای همراه آمده‌اند.');
}
if(p.slides.items.length!==19)throw Error('expected19slides');
const polished=JSON.parse(await fs.readFile(path.join(ROOT,'theory/SPEAKER_NOTES_POLISHED_V1.json'),'utf8'));
const refs=JSON.parse(await fs.readFile(path.join(ROOT,'audit/SOURCES_V1.json'),'utf8'));
for(let i=0;i<19;i++){
 let n=polished[i].notes;
 if(i===18)n+='\n\n'+refs.map(z=>z.authors.join(', ')+' ('+z.year+'). '+z.title+'. '+z.url+'\n'+z.relevance).join('\n\n');
 p.slides.items[i].speakerNotes.text=n;notes[i].notes=n;
}
await fs.writeFile(path.join(ROOT,'private/speaker_notes_v2.json'),JSON.stringify(notes,null,2));
await fs.writeFile(path.join(ROOT,'private/build_contract_v1.json'),JSON.stringify({slides:19,tableOwners:tables,chartOwners:charts,fontPolicy:{basis:'design',families:['Arial','Consolas','Cambria Math']},size:{width:1280,height:720}},null,2));
await (await PresentationFile.exportPptx(p)).save(path.join(ROOT,'private/candidate_v2.pptx'));
await fs.writeFile(path.join(ROOT,'private/deck_v2.json'),JSON.stringify(p.toProto()));
await fs.writeFile(path.join(ROOT,'source/SPEAKER_SCRIPT_FA.md'),'# متن همراه ارائه\n\nزمان پیشنهادی بخش اصلی:۲۰دقیقه. اسلایدهای۱۷تا۱۹ پشتیبان‌اند.\n\n'+notes.map(n=>'## '+n.slide+'. '+n.title+'\n\n'+n.notes).join('\n\n'));
console.log(JSON.stringify({slides:19,tables,charts,candidate:'private/candidate_v2.pptx'}));
