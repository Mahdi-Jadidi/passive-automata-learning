function equal(a,b){return JSON.stringify(a)===JSON.stringify(b)}

function requireThat(ok,msg){if(!ok)throw new Error(msg)}

function unique(xs){return Array.isArray(xs)&&new Set(xs).size===xs.length}

function project(word,block){const s=new Set(block);return word.filter(x=>s.has(x))}

function validateRequest(q){
 requireThat(q&&Array.isArray(q.alphabet)&&q.alphabet.length>0&&unique(q.alphabet)&&q.alphabet.every(x=>typeof x==="string"),"alphabet");
 requireThat(Array.isArray(q.blocks)&&q.blocks.every(b=>Array.isArray(b)&&b.length>0),"blocks");
 const flat=q.blocks.flat();requireThat(unique(flat)&&equal([...flat].sort(),[...q.alphabet].sort()),"complete partition");
 for(const label of ["positives","negatives"]){const rows=q[label];requireThat(Array.isArray(rows)&&rows.every(r=>typeof r.id==="string"&&Array.isArray(r.word)&&r.word.every(x=>q.alphabet.includes(x)))&&unique(rows.map(r=>r.id)),"trace IDs/tokens")}
 requireThat(q.mode==="unrestricted"||q.mode==="bounded","regime");
 if(q.mode==="bounded")requireThat(Array.isArray(q.bounds)&&q.bounds.length===q.blocks.length&&q.bounds.every(x=>Number.isSafeInteger(x)&&x>0),"bounds");
 else requireThat(q.bounds===null,"unrestricted bounds");
 for(const k of ["requestId","sampleDigest","regimeDigest","serviceVersion","family","schema"])requireThat(typeof q[k]==="string"&&q[k].length>0,"binding "+k);
 return {requestId:q.requestId,sampleDigest:q.sampleDigest,regimeDigest:q.regimeDigest,serviceVersion:q.serviceVersion,family:q.family,schema:q.schema,blocks:q.blocks,mode:q.mode,bounds:q.bounds,negativeIds:q.negatives.map(r=>r.id)};
}

function verifyTable(q,t,b,failed){
 requireThat(t&&t.kind==="unrestricted_base"&&t.complete===true&&equal(t.block,b)&&Array.isArray(t.zeros)&&Array.isArray(t.free),"table type/completeness/block");
 const positive=new Map(q.positives.map(r=>[r.id,JSON.stringify(project(r.word,b))]));
 const neg=new Map(q.negatives.map(r=>[r.id,JSON.stringify(project(r.word,b))]));
 const pset=new Set(positive.values()),seen=new Set(),groups=new Set();
 function take(id){requireThat(neg.has(id)&&!seen.has(id),"missing/duplicate/unknown column");seen.add(id);return neg.get(id)}
 let named=false;
 for(const z of t.zeros){requireThat(z&&Object.hasOwn(z,"positive"),"zero schema");const w=take(z.negative);requireThat(pset.has(w),"false zero");
 if(z.positive!==null)requireThat(positive.has(z.positive)&&positive.get(z.positive)===w,"false named witness");
 if(z.negative===failed&&z.positive!==null)named=true;}
 for(const g of t.free){requireThat(Array.isArray(g)&&g.length>0,"empty group");let w;
 for(const id of g){const v=take(id);requireThat(!pset.has(v),"false free");if(w===undefined)w=v;else requireThat(w===v,"merged distinct projections")}
 requireThat(!groups.has(w),"split equal projections");groups.add(w)}
 requireThat(seen.size===neg.size&&named,"incomplete table or unnamed failed witness");
}

function verifyDFA(q,d,b,i){
 requireThat(d&&equal(d.block,b)&&Array.isArray(d.states)&&d.states.length>0&&unique(d.states)&&d.states.every(x=>typeof x==="string")&&d.states.includes(d.initial)&&unique(d.accepting)&&d.accepting.every(s=>d.states.includes(s))&&Array.isArray(d.transitions),"DFA structure");
 if(q.mode==="bounded")requireThat(d.states.length<=q.bounds[i],"state bound");
 const transitions=new Map();
 for(const t of d.transitions){requireThat(Array.isArray(t)&&t.length===3&&d.states.includes(t[0])&&b.includes(t[1])&&d.states.includes(t[2]),"transition domain");const key=JSON.stringify(t.slice(0,2));requireThat(!transitions.has(key),"nondeterministic");transitions.set(key,t[2])}
 requireThat(transitions.size===d.states.length*b.length,"incomplete DFA");
 function accepts(word){let s=d.initial;for(const x of project(word,b))s=transitions.get(JSON.stringify([s,x]));return d.accepting.includes(s)}
 requireThat(q.positives.every(r=>accepts(r.word)),"positive rejected");return q.negatives.map(r=>accepts(r.word)?0:1);
}

function normalize(q,p,verifyReceipt){
 try{
 const binding=validateRequest(q);
 requireThat(p&&typeof p==="object"&&p.complete===true&&equal(p.binding,binding),"incomplete or mismatched receipt binding");
 requireThat(typeof verifyReceipt==="function"&&verifyReceipt(p)===true,"untrusted receipt");
 if(p.status==="PROJECTION_NO"){
 requireThat(q.negatives.some(r=>r.id===p.failed)&&Array.isArray(p.tables)&&p.tables.length===q.blocks.length,"failed ID/tables");
 q.blocks.forEach((b,i)=>verifyTable(q,p.tables[i],b,p.failed));
 return {kind:"PROJECTION_NO",scope:"refinements",evidence:p.tables,operational:false};
 }
 if(p.status==="BOUNDED_NO"){
 requireThat(q.mode==="bounded"&&p.exact===true,"unconfirmed bounded failure");
 return {kind:"BOUNDED_NO",scope:"exact",operational:false};
 }
 if(p.status==="ACCEPT"){
 requireThat(Array.isArray(p.dfas)&&p.dfas.length===q.blocks.length,"missing DFAs");
 const bits=q.blocks.map((b,i)=>verifyDFA(q,p.dfas[i],b,i));
 requireThat(q.negatives.every((_,i)=>bits.some(row=>row[i]===1)),"negative accepted");
 if(Object.hasOwn(p,"jointRow"))requireThat(equal(bits,p.jointRow),"joint row mismatch");
 return {kind:"ACCEPT",scope:"exact",operational:false};
 }
 throw new Error("ambiguous or unknown status");
 }catch(e){return {kind:"UNKNOWN",scope:"none",operational:false,reason:String(e.message??e)}}
}

function makeFixtures(){
 const q={schema:"audit-v1",requestId:"try-1",sampleDigest:"mock-sample",regimeDigest:"mock-unbounded",serviceVersion:"mock-only",family:"all",alphabet:["a","b","unused"],blocks:[["a"],["b"],["unused"]],positives:[{id:"p7",word:["a","b"]}],negatives:[{id:"n9",word:["b","a"]},{id:"n2",word:["b","a","a"]},{id:"n5",word:["a","b","a"]},{id:"n8",word:["b","a"]}],mode:"unrestricted",bounds:null};
 const t=(block,zeros,free)=>({kind:"unrestricted_base",complete:true,block,zeros,free});const z=(negative,positive)=>({negative,positive});
 const no={status:"PROJECTION_NO",complete:true,binding:validateRequest(q),failed:"n9",tables:[t(["a"],[z("n9","p7"),z("n8",null)],[["n2","n5"]]),t(["b"],[z("n9","p7"),z("n2",null),z("n5",null),z("n8",null)],[]),t(["unused"],[z("n9","p7"),z("n2",null),z("n5",null),z("n8",null)],[])]};
 const aq={...q,requestId:"try-2",blocks:[["a","b"],["unused"]]};
 const d={block:["a","b"],states:["s","a","ok","sink"],initial:"s",accepting:["ok"],transitions:[["s","a","a"],["s","b","sink"],["a","a","sink"],["a","b","ok"],["ok","a","sink"],["ok","b","sink"],["sink","a","sink"],["sink","b","sink"]]};
 const u={block:["unused"],states:["yes"],initial:"yes",accepting:["yes"],transitions:[["yes","unused","yes"]]};
 const yes={status:"ACCEPT",complete:true,binding:validateRequest(aq),dfas:[d,u]};
 const bq={...aq,requestId:"try-3",mode:"bounded",bounds:[1,1],regimeDigest:"mock-bounded"};
 const bn={status:"BOUNDED_NO",complete:true,binding:validateRequest(bq),exact:true};
 const bsuccess={...aq,requestId:"try-4",mode:"bounded",bounds:[4,1],regimeDigest:"mock-bounded-success"};
 const byes={...yes,binding:validateRequest(bsuccess),jointRow:[[1,1,1,1],[0,0,0,0]]};
 return {q,no,aq,yes,bq,bn,bsuccess,byes};
}

function runTests(f){
 const {q,no,aq,yes,bq,bn,bsuccess,byes}=f, results=[];const trust=()=>true;const clone=x=>JSON.parse(JSON.stringify(x));
 function check(name,request,payload,kind,auth=trust){const actual=normalize(request,payload,auth);requireThat(actual.kind===kind&&actual.operational===false,name+": "+JSON.stringify(actual));results.push(name+" PASS")}
 function mutate(name,request,payload,change){const p=clone(payload);change(p);check(name,request,p,"UNKNOWN")}
 check("complete projection NO, anonymous zeros, duplicate words, unused letter",q,no,"PROJECTION_NO");
 check("ACCEPT without tables",aq,yes,"ACCEPT");
 check("exact bounded NO",bq,bn,"BOUNDED_NO");
 check("bounded success and common joint row",bsuccess,byes,"ACCEPT");
 check("missing receipt verification",q,no,"UNKNOWN",()=>false);
 check("timeout",q,null,"UNKNOWN");
 check("omitted unused alphabet", {...q,blocks:[["a"],["b"]]},no,"UNKNOWN");
 check("overlapping blocks",{...q,blocks:[["a","b"],["b","unused"]]},no,"UNKNOWN");
 mutate("untyped NO",q,no,p=>p.status="NO");
 mutate("wrong sample",q,no,p=>p.binding.sampleDigest="other");
 mutate("wrong retry",q,no,p=>p.binding.requestId="old");
 mutate("wrong negative order",q,no,p=>p.binding.negativeIds.reverse());
 mutate("wrong partition",q,no,p=>p.binding.blocks.reverse());
 mutate("wrong regime",bq,bn,p=>p.binding.regimeDigest="other");
 mutate("partial payload",q,no,p=>p.complete=false);
 mutate("missing block table",q,no,p=>p.tables.pop());
 mutate("conditioned table",q,no,p=>p.tables[0].kind="conditioned");
 mutate("unresolved reference",q,no,p=>p.tables[0]={ref:"unknown"});
 mutate("missing column",q,no,p=>p.tables[0].free[0].pop());
 mutate("duplicate column",q,no,p=>p.tables[0].free[0].push("n2"));
 mutate("unknown column",q,no,p=>p.tables[0].free[0][0]="missing");
 mutate("anonymous failed witness",q,no,p=>p.tables[0].zeros[0].positive=null);
 mutate("invalid positive ID",q,no,p=>p.tables[0].zeros[0].positive="p8");
 mutate("split equal free groups",q,no,p=>p.tables[0].free=[["n2"],["n5"]]);
 mutate("false fixed zero",q,no,p=>{p.tables[0].zeros.push({negative:"n2",positive:null});p.tables[0].free=[["n5"]]});
 mutate("false free",q,no,p=>{p.tables[0].zeros.pop();p.tables[0].free.push(["n8"])});
 mutate("missing DFA",aq,yes,p=>delete p.dfas);
 mutate("incomplete transitions",aq,yes,p=>p.dfas[0].transitions.pop());
 mutate("duplicate transition",aq,yes,p=>p.dfas[0].transitions.push(p.dfas[0].transitions[0]));
 mutate("wrong DFA alphabet",aq,yes,p=>p.dfas[0].block=["a"]);
 mutate("positive rejected",aq,yes,p=>p.dfas[0].accepting=[]);
 mutate("negative accepted",aq,yes,p=>p.dfas[0].accepting.push("sink"));
 mutate("incorrect joint row",bsuccess,byes,p=>p.jointRow[0][0]=0);
 mutate("inexact bounded failure",bq,bn,p=>p.exact=false);
 check("bounded NO in unrestricted run",aq,{...bn,binding:validateRequest(aq)},"UNKNOWN");
 check("DFA exceeds bound",bq,{...yes,binding:validateRequest(bq)},"UNKNOWN");
 check("legacy simulator ACCEPT cannot become external",aq,{status:"ACCEPT",blocks:aq.blocks,tables:[],failed:null},"UNKNOWN");
 return results;
}

export { validateRequest, normalize, makeFixtures, runTests };
