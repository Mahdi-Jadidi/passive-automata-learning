import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation, PresentationFile} from 'file:///C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const root='C:/Users/Mahdi/Documents/ChatGPT/passive automata learning/results/2026-11-06/recommendation_checkpoint_v26';
const work=path.join(root,'presentation');
await fs.mkdir(path.join(work,'build'),{recursive:true});
await fs.mkdir(path.join(work,'output'),{recursive:true});
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
const navy='#142D4E';
const source='Source: C026 theory/PROOFS_V1.md and CONTRACT_V1.md, 6 November 2026. ';
function text(slide,content,x,y,w,h,size=32,bold=false){
 const box=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 box.text=content;box.text.style={typeface:'Arial',fontSize:size,color:navy,bold};return box;
}
function slide(title,rows,note){
 const s=presentation.slides.add();s.background.fill='#FFFFFF';
 text(s,title,76,56,1128,104,46,true);
 rows.forEach((row,i)=>text(s,row,80,190+i*108,1110,90,32));
 s.speakerNotes.text=source+note;
 return s;
}
const cover=presentation.slides.add();cover.background.fill='#FFFFFF';
text(cover,'Unknown Device\nAlphabet Partitioning',76,150,1120,210,60,true);
text(cover,'Passive automata learning\nC026 research checkpoint',80,414,1100,110,32);
text(cover,'Advisor discussion · 6 November 2026',80,590,1100,55,28);
cover.speakerNotes.text=source+'We observe anonymous input symbols and complete-word acceptance labels. The study recommends the largest compatible partition while preserving ambiguity about actual devices. External novelty remains unassessed.';
slide('Problem and observation model',[
 'Input: alphabet Σ and finite word sets P and N',
 'P contains accepted words. N contains rejected words.',
 'Ownership, device count and local machines are unknown.',
 'Each symbol belongs to one independent component.'
],'No external K, host map, true machine or state bound enters inference. The global word succeeds iff every local projected word succeeds. Local factors are arbitrary regular languages. This is AND acceptance, not C025 selected-current-output semantics.');
slide('Exact compatibility by projection',[
 'πB(w) keeps only the symbols in block B.',
 'HB = {πB(p) : p ∈ P}',
 'Π fits exactly when  ∀n ∈ N, ∃B ∈ Π: πB(n) ∉ HB',
 'Different blocks may reject different negative words.'
],'The quantifier order is essential: each negative needs some rejecting block, which may differ between negatives. Necessity follows because every local factor must contain all positive projections. Sufficiency uses the finite regular factors HB. Prior work: C008 T10 and C009 T1.');
slide('Ambiguity and the recommendation',[
 'Merging compatible blocks preserves compatibility.',
 'A single block always fits consistent finite labels.',
 'Recommendation: maximize the number of blocks.',
 'The recommended count is a convention about the data.'
],'Report all-K ambiguity separately from optimal ties. A unique maximum with more than one block still has compatible coarser explanations. Tie break: the least canonical restricted-growth string over sorted symbols. Counting recommended blocks does not identify the number of physical devices.');
slide('A small example',[
 'Σ = {a,b,c,d}     P = {ε, ab, cd}     N = {ba, dc}',
 'The evidence forces a with b, and c with d.',
 'Maximum recommendation: {a,b}, {c,d}',
 'One block {a,b,c,d} also fits. Ownership is ambiguous.'
],'Constructed example. Swapping adjacent a,b changes ab accepted to ba rejected, so their owners cannot differ. Likewise c,d. The two-block partition rejects ba via ab and dc via cd. Its finite local witness languages are {epsilon,ab} and {epsilon,cd}. Those forced pairs prove that two is maximal. Oneblock language P is an alternative witness.');
slide('Exact search with honest stopping',[
 'Finalize a block containing the least remaining atom.',
 'Memo state: remaining atoms and uncovered negatives.',
 'Maximize block count. Track optimal ties separately.',
 'At a deadline, report any feasible incumbent and bounds.'
],'This max-plus DP adapts the C009 count recurrence. F(R,U)=max over anchored B of 1+F(R minus B,U minus r(B)). An empty uncovered mask allows the singleton-atom completion. The entire remaining union must reject all uncovered negatives. Two incumbents establish ambiguity, not optimality while larger possibilities remain. Deadlines and memo quotas preserve only replayed feasible witnesses.');
slide('Finite evidence leaves prime alternatives',[
 'Every compatible partition has prime regular factors.',
 'Construction: exclude finitely many local words.',
 'These factors remain nonempty and infinite.',
 'Primeness alone cannot certify a nontrivial device map.'
],'C026 candidate Theorem 1, direct proof. Assign each negative to a block with an unseen positive projection. Exclude those assigned projections plus one additional unobserved local word. The resulting cofinite nonuniversal language projects universally to every proper subalphabet, making it alphabet-prime. A prime oneblock completion exists at every finite consistent sample. Unrestricted automaton sizes are essential. External novelty is unassessed.');
slide('Eventual behavioral recovery',[
 'A fixed nonempty regular L has a finest partition.',
 'A finite sample can eliminate every incompatible split.',
 'Bound: ≤ 3(2^(m−1) − 1) words, length < Q³\nQ = target DFA states (proof parameter only)',
 'Convergence does not certify when to stop.'
],'C008 supplies complete-language meet closure and the unique finest disjoint factorization. C026 candidate Theorem 3 supplies one negative and two accepted projection lifts for every invalid cut. A three-copy epsilon product of a complete Q-state target DFA bounds all three word lengths by Q^3 minus one. Q is only a proof parameter, never solver input. An exhaustive informant eventually contains this finite sample, so the exact maximum recommendation converges. The learner cannot generally certify its arrival at a finite time. Physical coincidence additionally requires true nonempty prime factors.');
let finalSlide={rows:['Checkpoint validation is still in progress.','Final audit counts will replace this private draft.','No empirical speed or physical recovery claim.','External novelty remains unassessed.'],notes:'Private draft. Validation metrics pending independent audit.'};
try {finalSlide=JSON.parse(await fs.readFile(path.join(work,'final_slide.json'),'utf8'));}catch{}
slide('Validation and current checkpoint',finalSlide.rows,finalSlide.notes);
const draft=path.join(work,'build','C026_Advisor_EN.draft.pptx');
await (await PresentationFile.exportPptx(presentation)).save(draft);
for(const [i,s] of presentation.slides.items.entries()){
 const png=await presentation.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(work,'build',`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
await fs.writeFile(path.join(work,'build','presentation.inspect.ndjson'),(await presentation.inspect({kind:'slide,textbox,notes',maxChars:200000})).ndjson);
console.log(JSON.stringify({draft,slides:presentation.slides.items.length}));
