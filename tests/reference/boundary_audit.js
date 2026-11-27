// Independent boundary/adversarial tests. Node.js >=16.
// Run: node tests/reference/boundary_audit.js
function boundaryAudit(){
 const check=(c,m)=>{if(!c)throw Error(m)};
 function parts(n){const out=[];function rec(p,k){if(p.length===n){out.push(p);return}for(let i=0;i<=k;i++)rec([...p,i],Math.max(k,i+1))}rec([],0);return out}
 const pop=m=>{let k=0;for(;m;m&=m-1)k++;return k};
 const blocks=p=>Array.from(new Set(p),k=>p.reduce((m,v,i)=>m|(v===k?1<<i:0),0));
 const proj=(w,b)=>w.filter(v=>b&(1<<v));
 const same=(a,b)=>a.join(",")===b.join(",");
 const eq=(x,y,b)=>same(proj(x,b),proj(y,b));
 const cost=p=>p.length-new Set(p).size;
 const compatible=(X,Y,p)=>Y.every(y=>blocks(p).some(b=>X.every(x=>!eq(x,y,b))));
 function words(n,L){const o=[[]];for(let l=1;l<=L;l++)for(const w of o.filter(x=>x.length===l-1))for(let a=0;a<n;a++)o.push([...w,a]);return o}
 const stats={descriptorChecks:0,descriptorSupportChecks:0,quotientOptima:0,boundedCorpora:0,conditionalScoreChecks:0};
 // Independent occurrence rank construction vs literal comparison on every block.
 for(const n of [2,3]){
  const W=words(n,3),full=(1<<n)-1;
  for(const x of W)for(const y of W){
   const cx=Array(n).fill(0),cy=Array(n).fill(0);for(const a of x)cx[a]++;for(const a of y)cy[a]++;
   let D=0;for(let a=0;a<n;a++)if(cx[a]!==cy[a])D|=1<<a;
   const xs=x.filter(a=>!(D&(1<<a))),ys=y.filter(a=>!(D&(1<<a)));
   const positions=Array.from({length:n},()=>[]);ys.forEach((a,i)=>positions[a].push(i));
   const cursor=Array(n).fill(0),z=xs.map(a=>positions[a][cursor[a]++]);let T=D;
   for(let k=0;k<z.length;k++)if(z.slice(0,k).some(q=>q>z[k])||z.slice(k+1).some(q=>q<z[k]))T|=1<<xs[k];
   let exactSupport=0;
   for(let b=0;b<=full;b++){
    const q=z.filter((_,i)=>b&(1<<xs[i]));const differs=Boolean(b&D)||q.some((v,i)=>i>0&&q[i-1]>v);
    check(differs===!eq(x,y,b),"descriptor");stats.descriptorChecks++;
    if(!eq(x,y,b)&&(pop(b)===1||(pop(b)===2&&!(D&b))))exactSupport|=b;
   }
   check(T===exactSupport&&eq(x,y,full^T),"discrepancy support");stats.descriptorSupportChecks++;
  }
 }
 // Exact alternative-family rank with original IDs, mandatory equality E and disequality D.
 const P=parts(3),W=words(3,2),es=[[0,1],[0,2],[1,2]],m=p=>es.reduce((v,[a,b],i)=>v|(p[a]===p[b]?1<<i:0),0);
 const merge=(p,S)=>{const v=p.filter((_,i)=>S&(1<<i)),head=v[0];return p.map(k=>v.includes(k)?head:k)};
 for(const x of W)for(const y of W)for(const z of W){
  if(same(x,y)||same(x,z)||same(y,z))continue;
  const X=[x],Y=[y,z],families=Y.map(t=>Array.from({length:7},(_,i)=>i+1).filter(b=>!eq(x,t,b)&& (pop(b)===1||(pop(b)===2&&[1,2,4].filter(a=>a&b).every(a=>eq(x,t,a))))));
  for(const E of P)for(let D=0;D<8;D++){
   if(m(E)&D)continue;
   const feasible=P.filter(p=>(m(p)&m(E))===m(E)&&!(m(p)&D)&&compatible(X,Y,p));
   const expected=feasible.length?Math.min(...feasible.map(cost)):Infinity;
   let best=Infinity;for(const a of families[0])for(const b of families[1]){const q=merge(merge(E,a),b);if(!(m(q)&D))best=Math.min(best,cost(q))}
   check(best===expected,"quotient witness rank");stats.quotientOptima++;
  }
 }
 // Enumerate total deterministic DFAs with <=2 states, start state 0.
 function rejectionMasks(W,X,Y,B){
  const A=[0,1].filter(a=>B&(1<<a)),out=new Set();
  for(let k=1;k<=2;k++)for(let code=0;code<k**(k*A.length);code++){
   let c=code;const tr=Array.from({length:k},()=>A.map(()=>{const v=c%k;c=Math.floor(c/k);return v}));
   const end=w=>{let s=0;for(const a of proj(w,B))s=tr[s][A.indexOf(a)];return s};
   for(let f=0;f<(1<<k);f++){if(!X.every(w=>f&(1<<end(w))))continue;out.add(Y.reduce((m,w,i)=>m|((f&(1<<end(w)))?0:1<<i),0))}
  }return out
 }
 const W2=words(2,2),all=parts(2),boundedExamples={fineYesCoarseNo:null,fineNoCoarseYes:null};
 for(let k=0;k<3**W2.length;k++){
  let c=k;const X=[],Y=[];for(const w of W2){const l=c%3;c=Math.floor(c/3);if(l===1)X.push(w);if(l===2)Y.push(w)}
  if(!X.length||!Y.length)continue;
  const need=(1<<Y.length)-1, R1=rejectionMasks(W2,X,Y,1),R2=rejectionMasks(W2,X,Y,2),R3=rejectionMasks(W2,X,Y,3);
  const fine=[...R1].some(a=>[...R2].some(b=>(a|b)===need)),coarse=R3.has(need);stats.boundedCorpora++;
  const repr=w=>w.map(a=>"ab"[a]).join("")||"ε";
  if(fine&&!coarse&&!boundedExamples.fineYesCoarseNo)boundedExamples.fineYesCoarseNo={X:X.map(repr),Y:Y.map(repr)};
  if(!fine&&coarse&&!boundedExamples.fineNoCoarseYes)boundedExamples.fineNoCoarseYes={X:X.map(repr),Y:Y.map(repr)};
  // Unit-weight CDAQ floor: compare exact residual removal under each conclusive structural outcome.
  const C=all;for(const Q of C){
   const A=C.filter(p=>cost(p)>=cost(Q)).length,N=C.filter(p=>(p[0]!==p[1]||Q[0]===Q[1])).length;
   const yes=compatible(X,Y,Q),removed=yes?A:N;
   if(!yes)for(const p of C)if(p[0]!==p[1]||Q[0]===Q[1])check(!compatible(X,Y,p),"NO cone");
   check(removed>=Math.min(A,N),"conditional floor");stats.conditionalScoreChecks++;
  }
 }
 check(boundedExamples.fineYesCoarseNo!==null&&boundedExamples.fineNoCoarseYes!==null,"bounded counterexamples");
 // Exact boundary: no nonempty block exists in the empty alphabet, even with zero positives.
 check(!compatible([], [[]], []),"empty alphabet negative");
 // Distinct least-model atom signatures do not establish actual inequality.
 check(eq([0],[0],1),"same literal words despite unconstrained opaque IDs");
 return {...stats,boundedExamples}
}
console.log(JSON.stringify(boundaryAudit(), null, 2));
// Observed in independent V8 execution: {"descriptorChecks":13700,"descriptorSupportChecks":1825,"quotientOptima":36036,"boundedCorpora":1932,"conditionalScoreChecks":3864,"boundedExamples":{"fineYesCoarseNo":{"X":["ab"],"Y":["ε","a","b"]},"fineNoCoarseYes":{"X":["a","b"],"Y":["ε"]}}}
