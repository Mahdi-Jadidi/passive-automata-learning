import fs from 'node:fs/promises';
import path from 'node:path';
process.env.RUNTIME_NODE_MODULES='C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const skill='C:/Users/Mahdi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const work='C:/Users/Mahdi/Documents/ChatGPT/passive automata learning/results/2026-11-06/recommendation_checkpoint_v26/presentation';
const {pathToFileURL}=await import('node:url');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const finalPath=path.join(work,'output/C026_Advisor_EN.pptx');
const result=await finalizePresentation({
 workspaceDir:work,
 candidatePath:path.join(work,'build/C026_Advisor_EN.draft.pptx'),
 finalPath,
 pythonExecutable:'C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
 explicitTotalSlideCount:9,
 requiredNativeTableOwnerSlides:[],
 requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'design',families:['Arial']},
 verifyArtifactToolImport:true,
 receiptPath:path.join(work,'build/C026_Advisor_EN.validation.json'),
});
console.log(JSON.stringify(result));
const {PresentationFile,FileBlob}=await import(pathToFileURL(path.join(process.env.RUNTIME_NODE_MODULES,'@oai/artifact-tool/dist/artifact_tool.mjs')));
const deck=await PresentationFile.importPptx(await FileBlob.load(finalPath));
for(const [i,s] of deck.slides.items.entries()){
 const png=await deck.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(work,'build',`final-slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
