process.env.RUNTIME_NODE_MODULES='C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const skill='C:/Users/Mahdi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
for(const lang of ['en']){
 const result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(root,'private/candidate_'+lang+'_v3'+(lang==='fa'?'_RTL':'')+'.pptx'),finalPath:path.join(root,'output/Simple_Alphabet_Partition_'+lang.toUpperCase()+'_Final.pptx'),pythonExecutable:'C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:19,layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(root,'private/final_validation_'+lang+'_v2.json')});
 console.log(JSON.stringify(result));
}
