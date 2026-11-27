// Independent EDR-BB, rank, literal optimum and certificate audit. Node.js >=16.
// Run: node tests/reference/region_rank_audit.js
function regionAudit(){
 const check=(v,m)=>{if(!v)throw Error(m)};
 function partitions(n){const out=[];function rec(p,k){if(p.length===n){out.push(p);return}for(let i=0;i<=k;i++)rec([...p,i],Math.max(k,i+1))}rec([],0);return out}
 const pairs=n=>Array.from({length:n},(_,i)=>Array.from({length:i},(_,j)=>[j,i])).flat();
 const mask=(p,es)=>es.reduce((m,[a,b],i)=>m|(p[a]===p[b]?1<<i:0),0);
 const pop=m=>{let c=0;for(;m;m&=m-1)c++;return c};
 const bits=m=>Array.from({length:31},(_,i)=>i).filter(i=>m&(1<<i));
 const rank=(p,S)=>pop(S)-new Set(p.filter((_,i)=>S&(1<<i))).size;
 const cost=p=>p.length-new Set(p).size;
 const results={regionConflictCases:0,regionMembershipChecks:0,fractionalChecks:0,corpora:0,optimumComparisons:0,mutantsRejected:0};
 for(let n=0;n<=4;n++){
  const P=partitions(n),es=pairs(n),all=(1<<es.length)-1,ms=P.map(p=>mask(p,es));
  for(const E of ms)for(let D=0;D<=all;D++){if(E&D)continue;
   const R=ms.filter(m=>(m&E)===E&&!(m&D)),allowed=all&~(E|D);
   for(let C=allowed;;C=(C-1)&allowed){
    const order=bits(C);if(pop(D)%2)order.reverse();
    // Child membership is checked against the independently enumerated universe.
    for(const m of ms){
      let prefix=0,count=0;for(const i of order){const e=1<<i;const child=((m&(E|e))===(E|e))&&!(m&(D|prefix));if(child)count++;prefix|=e}
      const parent=(m&E)===E&&!(m&D), residual=parent&&!(m&C);
      check(count===(parent&&(m&C)?1:0),"first-true coverage");
      check(count+Number(residual)===Number(parent),"residual coverage");results.regionMembershipChecks++;
    }
    check(R.every(m=>!(m&C)||order.some(i=>m&(1<<i))),"ordering");results.regionConflictCases++;
    if(C===0)break;
   }
  }
 }
 // Exhaustive support triples with equal half or third weights, plus unequal (1,1,2)/3.
 // Integer arithmetic directly checks weighted rank <= global rank.
 for(let n=1;n<=5;n++){
  const P=partitions(n),limit=1<<n;
  for(let a=1;a<limit;a++)for(let b=a;b<limit;b++)for(let c=b;c<limit;c++)
   for(const [d,wa,wb,wc] of [[2,1,1,1],[3,1,1,1],[3,1,1,2],[3,1,2,1],[3,2,1,1]]){
    let valid=true;for(let v=0;v<n;v++)if(wa*Number(Boolean(a&(1<<v)))+wb*Number(Boolean(b&(1<<v)))+wc*Number(Boolean(c&(1<<v)))>d)valid=false;
    if(!valid)continue;
    for(const p of P){check(wa*rank(p,a)+wb*rank(p,b)+wc*rank(p,c)<=d*cost(p),"fractional rank");results.fractionalChecks++}
   }
 }
 const proj=(w,S)=>w.filter(a=>S&(1<<a)).join(",");
 const blockMasks=p=>Array.from(new Set(p),k=>p.reduce((S,v,i)=>S|(v===k?1<<i:0),0));
 const compatible=(X,Y,p)=>Y.every(y=>blockMasks(p).some(S=>X.every(x=>proj(x,S)!==proj(y,S))));
 function auditCorpus(n,X,Y){
  const P=partitions(n),ok=P.filter(p=>compatible(X,Y,p)),opt=ok.length?Math.min(...ok.map(cost)):Infinity;
  // Independent witness-choice enumeration: for each negative choose a separating subset,
  // merge its members and minimize induced rank; no producer code.
  const alternatives=Y.map(y=>Array.from({length:(1<<n)-1},(_,i)=>i+1).filter(S=>X.every(x=>proj(x,S)!==proj(y,S))));
  let found=Infinity;
  function rec(i,p){if(i===Y.length){found=Math.min(found,cost(p));return}
   for(const S of alternatives[i]){const ids=bits(S),labels=new Set(ids.map(j=>p[j])),first=p[ids[0]];rec(i+1,p.map(k=>labels.has(k)?first:k))}
  }
  rec(0,Array.from({length:n},(_,i)=>i));check(found===opt,"literal RGS vs witness choices");results.corpora++;results.optimumComparisons++;
  // Verify downward closure of NO and every same-negative deletion obligation.
  const es=pairs(n);for(const p of P){const pm=mask(p,es);for(const q of P)if((mask(q,es)&pm)===pm&&compatible(X,Y,p))check(compatible(X,Y,q),"structural monotonicity")}
  for(const y of Y){const required=[];for(let a=0;a<n;a++)if(X.some(x=>proj(x,((1<<n)-1)^(1<<a))===proj(y,((1<<n)-1)^(1<<a))))required.push(a);for(const p of ok)check(required.every(a=>p[a]===p[required[0]]),"mandatory deletion")}
 }
 for(const n of [1,2,3]){
  const words=[[],...Array.from({length:n},(_,a)=>[a]),...Array.from({length:n},(_,a)=>Array.from({length:n},(_,b)=>[a,b])).flat()];
  if(n<=2){for(let k=0;k<3**words.length;k++){let z=k;const X=[],Y=[];for(const w of words){const d=z%3;z=Math.floor(z/3);if(d===1)X.push(w);if(d===2)Y.push(w)}auditCorpus(n,X,Y)}}
  else for(let a=0;a<words.length;a++)for(let b=0;b<words.length;b++)for(let c=b+1;c<words.length;c++)if(a!==b&&a!==c){auditCorpus(n,[words[a]],[words[b],words[c]]);auditCorpus(n,[words[b],words[c]],[words[a]])}
 }
 // Degenerate empty alphabet: only the empty partition; no block can separate a negative.
 auditCorpus(0,[],[]);auditCorpus(0,[],[[]]);auditCorpus(2,[[0]],[[0]]);auditCorpus(2,[[0,1],[0,1]],[[1,0],[1,0]]);
 const w=s=>[...s].map(c=>c.charCodeAt(0)-97);
 const X=[w("abcdef")],Y=["badcef","abdcfe","bacdfe"].map(w);
 const opt=Math.min(...partitions(6).filter(p=>compatible(X,Y,p)).map(cost));check(opt===2,"strict packing example");results.strictPackingOptimum=opt;
 // Minimal adversarial examples.
 check(compatible([w("ab"),w("cd")],[[]],[0,0,0,0]),"dead union counterexample");
 check(compatible([[]],[w("a"),w("b")],[0,1]),"mixed negative counterexample");
 check(compatible([w("ab")],[w("ba")],[0,0]),"counts miss order");
 check(compatible([w("b")],[[]],[0,1]),"truncating support {a,b} to {a} invalid (a unused)");
 // Exact reference certificate: explicit child sets and residual, with coverage checked over all partitions.
 function validateSplit(n,E,D,C,claims){
  const es=pairs(n),P=partitions(n),all=(1<<es.length)-1;
  if(!Number.isInteger(E)||!Number.isInteger(D)||(E|D)&~all||E&D||!P.some(p=>mask(p,es)===E))return false;
  if(!Array.isArray(C)||new Set(C).size!==C.length||C.some(i=>!Number.isInteger(i)||i<0||i>=es.length||((E|D)&(1<<i))))return false;
  if(!Array.isArray(claims)||claims.length!==C.length+1)return false;
  const actual=Array.from({length:C.length+1},()=>[]);
  for(const p of P){const m=mask(p,es);if((m&E)!==E||m&D)continue;const j=C.findIndex(i=>m&(1<<i));actual[j<0?C.length:j].push(p.join(","))}
  return actual.every((a,i)=>Array.isArray(claims[i])&&JSON.stringify(a.slice().sort())===JSON.stringify(claims[i].slice().sort()));
 }
 const good=[["0,0,0","0,0,1"],["0,1,0"],["0,1,1","0,1,2"]];
 // Pair order [0,1], [0,2], [1,2].
 check(validateSplit(3,0,0,[0,1],good),"valid coverage");
 const bad=[good.slice(0,2),[good[0],good[0],good[2]],[good[0],good[1],[]],[good[0],["0,1,1"],good[2]],[["0,0,1"],good[1],good[2]]];
 for(const b of bad){check(!validateSplit(3,0,0,[0,1],b),"accepted mutant");results.mutantsRejected++}
 for(const C of [[0,0],[0,3],[0,1.5]]){check(!validateSplit(3,0,0,C,good),"invalid pair");results.mutantsRejected++}
 // With all three pairs decided false, singleton representative remains; UNKNOWN cannot remove it.
 check(!validateSplit(3,0,0,[0,1,2],[good[0],good[1],["0,1,1"],[]]),"missing pending singleton");results.mutantsRejected++;
 // Rank certificate toy kernel recomputes each floor from the complete literal feasible set.
 function verifyRank(n,feasible,cert){
  const D=cert.den;if(typeof D!=="bigint"||D<=0n||!Array.isArray(cert.terms)||!feasible.length)return false;
  const loads=Array(n).fill(0n);let sum=0n;
  for(const {S,l,w} of cert.terms){if(!Number.isSafeInteger(S)||S<=0||S>=2**n||!Number.isSafeInteger(l)||l<0||typeof w!=="bigint"||w<0n)return false;
   if(feasible.some(p=>rank(p,S)<l))return false;for(let v=0;v<n;v++)if(S&(1<<v))loads[v]+=w;sum+=BigInt(l)*w}
  return loads.every(x=>x<=D)&&cert.claim===(sum+D-1n)/D;
 }
 const F=partitions(6).filter(p=>compatible(X,Y,p)),terms=[{S:15,l:1,w:1n},{S:60,l:1,w:1n},{S:51,l:1,w:1n}];
 const valid={den:2n,terms,claim:2n};check(verifyRank(6,F,valid),"valid rational proof");
 for(const mut of [{...valid,den:1n},{...valid,den:0n},{...valid,claim:3n},{...valid,terms:[{...terms[0],l:2},...terms.slice(1)]},{...valid,terms:[{...terms[0],w:-1n},...terms.slice(1)]},{...valid,terms:[{...terms[0],S:64},...terms.slice(1)]},{...valid,terms:[{...terms[0],w:0.5},...terms.slice(1)]}]){
  check(!verifyRank(6,F,mut),"accepted rank mutation");results.mutantsRejected++
 }
 return results
}
console.log(JSON.stringify(regionAudit(), null, 2));
// Observed in independent V8 execution: {"regionConflictCases":2600,"regionMembershipChecks":38370,"fractionalChecks":811537,"corpora":3934,"optimumComparisons":3934,"mutantsRejected":16,"strictPackingOptimum":2}
