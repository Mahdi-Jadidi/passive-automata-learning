process.env.RUNTIME_NODE_MODULES='C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
import path from 'node:path';
import fs from 'node:fs/promises';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const skill='C:/Users/Mahdi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const contract=JSON.parse(await fs.readFile(path.join(root,'private/build_contract_v1.json'),'utf8'));
const result=await finalizePresentation({
 workspaceDir:root,candidatePath:path.join(root,'private/candidate_v3_RTL_normalized.pptx'),
 finalPath:path.join(root,'output/Advisor_Briefing_FA.pptx'),
 pythonExecutable:'C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 explicitTotalSlideCount:19,
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...contract.tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:contract.tableOwners,requiredNativeChartOwnerSlides:contract.chartOwners,
 materializeLiteralChartWorkbooks:true,fontPolicy:contract.fontPolicy,verifyArtifactToolImport:true,
 receiptPath:path.join(root,'private/final_validation_v3.json')
});
console.log(JSON.stringify(result));
