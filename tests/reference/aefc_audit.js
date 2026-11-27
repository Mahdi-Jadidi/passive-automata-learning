// Independent finite audit, issue #3. Node.js >= 16; no dependencies.
// Run: node tests/reference/aefc_audit.js
// Enumerates all equivalence families for stated finite domains; not a producer import.
function aefcAudit(){
  const check=(c,m)=>{if(!c)throw Error(m)};
  function parts(n){const out=[];function rec(a,k){if(a.length===n){out.push(a.slice());return}for(let j=0;j<=k;j++)rec([...a,j],Math.max(k,j+1))}rec([],0);return out}
  const atoms=n=>Array.from({length:(1<<n)-1},(_,i)=>i+1).filter(m=>m.toString(2).replace(/0/g,"").length<=2);
  const contained=(a,b)=>(a&b)===a;
  function models(n,t){
    const A=atoms(n), P=parts(t), out=[];
    function rec(m){if(m.length===A.length){out.push(m.slice());return}const a=A[m.length];for(const p of P){let valid=true;for(let k=0;k<m.length;k++)if(contained(A[k],a))for(let i=0;i<t;i++)for(let j=0;j<i;j++)if(p[i]===p[j]&&m[k][i]!==m[k][j])valid=false;if(valid)rec([...m,p])}}
    rec([]);return out
  }
  function eq(A,m,b,u,v){return A.every((a,i)=>!contained(a,b)||m[i][u]===m[i][v])}
  function words(n,t,A,m){
    const h=Math.ceil(Math.log2(Math.max(2,t))), w=Array.from({length:t},()=>[]);
    for(let k=0;k<A.length;k++){const a=A[k];if((a&(a-1))===0)continue;const ids=Array.from({length:n},(_,i)=>i).filter(i=>a&(1<<i));for(let u=0;u<t;u++)for(let bit=0;bit<h;bit++)w[u].push(...((m[k][u]>>bit)&1?[ids[1],ids[0]]:ids))}
    for(let a=0;a<n;a++)for(let u=0;u<t;u++)for(let j=0;j<m[A.indexOf(1<<a)][u];j++)w[u].push(a);
    return w
  }
  const proj=(w,b)=>w.filter(s=>b&(1<<s)).join(",");
  const results={realizationSystems:0,projectionChecks:0,historyChecks:0,consistentHistories:0,targetChecks:0,anonymousChoices:0,strictAnonymousTargets:0};
  for(const [n,t] of [[0,3],[1,4],[2,4],[3,3]]){
    const A=atoms(n);
    for(const m of models(n,t)){const w=words(n,t,A,m);results.realizationSystems++;for(let b=0;b<(1<<n);b++)for(let u=0;u<t;u++)for(let v=0;v<u;v++){check(eq(A,m,b,u,v)===(proj(w[u],b)===proj(w[v],b)),"realization");results.projectionChecks++}}
  }
  function least(A,t,edges){
    return A.map(a=>{const p=Array.from({length:t},(_,i)=>i);const find=u=>{while(p[u]!==u)u=p[u];return u};for(const [b,u,v] of edges)if(contained(a,b))p[find(u)]=find(v);return p.map((_,i)=>find(i))})
  }
  for(const [n,t] of [[2,3],[2,4]]){
    const A=atoms(n), M=models(n,t), Bs=Array.from({length:(1<<n)-1},(_,i)=>i+1), pos=[0,1],neg=Array.from({length:t-2},(_,i)=>i+2);
    const pairs=Bs.flatMap(b=>Array.from({length:t},(_,u)=>Array.from({length:u},(_,v)=>[b,u,v])).flat());
    const Z=Bs.flatMap(b=>neg.map(y=>[b,y]));
    const Zsets=[[],...Z.map(z=>[z]),...Z.flatMap((z,i)=>Z.slice(i+1).map(z2=>[z,z2]))];
    const targets=parts(n).map(p=>Array.from({length:Math.max(...p)+1},(_,k)=>p.reduce((b,v,i)=>b|(v===k?1<<i:0),0)));
    const no=(m,P)=>neg.some(y=>P.every(b=>pos.some(x=>eq(A,m,b,x,y))));
    // Truth tables from complete equivalence-model enumeration, not DSU closure.
    const flags=M.map(m=>({m, e:pairs.map(([b,u,v])=>eq(A,m,b,u,v)),z:Z.map(([b,y])=>pos.some(x=>eq(A,m,b,x,y))),no:targets.map(P=>no(m,P))}));
    for(let ei=-1;ei<pairs.length;ei++)for(let di=-1;di<pairs.length;di++)for(const zs of Zsets){
      const zi=zs.map(z=>Z.indexOf(z));const matching=flags.filter(f=>(ei<0||f.e[ei])&&(di<0||!f.e[di])&&zi.every(i=>f.z[i]));
      const edges=ei<0?[]:[pairs[ei]], diff=di<0?[]:[pairs[di]], surviving=[];
      function branch(k,e){if(k===zs.length){results.anonymousChoices++;const l=least(A,t,e);if(diff.every(([b,u,v])=>!eq(A,l,b,u,v)))surviving.push(l);return}const [b,y]=zs[k];for(const x of pos)branch(k+1,[...e,[b,y,x]])}
      branch(0,edges);results.historyChecks++;check(Boolean(matching.length)===Boolean(surviving.length),"history consistency");
      if(!matching.length)continue;results.consistentHistories++;
      for(let k=0;k<targets.length;k++){const expected=matching.every(f=>f.no[k]), actual=surviving.every(l=>no(l,targets[k]));check(expected===actual,"forced NO");results.targetChecks++;if(actual&&!no(least(A,t,edges),targets[k]))results.strictAnonymousTargets++}
    }
  }
  // Strict named and anonymous cases independently checked by literal words and closure.
  const A=atoms(5), bits=s=>[...s].reduce((m,c)=>m|(1<<(c.charCodeAt(0)-97)),0);
  const w=["abcd","bace","abcde","abced"].map(s=>[...s].map(c=>c.charCodeAt(0)-97));
  const rows=[["acd","b","e"],["bcd","a","e"],["ace","b","d"],["bce","a","d"],["ab","c","d","e"]];
  const witness=[[0,0,1],[0,0,1],[1,0,0],[1,0,0],[0,0,0,1]];
  const edges=[];for(let k=0;k<rows.length;k++)for(let j=0;j<rows[k].length;j++){const b=bits(rows[k][j]),y=k===4?3:2,x=witness[k][j];check(proj(w[x],b)===proj(w[y],b),"literal named edge");edges.push([b,y,x]);for(const z of [2,3])check([0,1].some(p=>proj(w[p],b)===proj(w[z],b)),"literal zero")}
  const target=["abc","d","e"].map(bits);
  const no=m=>[2,3].some(y=>target.every(b=>[0,1].some(x=>eq(A,m,b,x,y))));
  check(!no(least(A,4,edges)),"strict named insufficiency");for(const x of [0,1]){const l=least(A,4,[...edges,[bits("ab"),2,x]]);check(no(l),"strict anonymous");check(![0,1].some(p=>[2,3].some(y=>eq(A,l,31,p,y))),"strict branch opposite-label distinctness")}
  results.targetedStrictAnonymous=1;
  return results;
}
console.log(JSON.stringify(aefcAudit(), null, 2));
// Observed in independent V8 execution: {"realizationSystems":1035,"projectionChecks":24639,"historyChecks":8642,"consistentHistories":7614,"targetChecks":15228,"anonymousChoices":28253,"strictAnonymousTargets":7095,"targetedStrictAnonymous":1}
