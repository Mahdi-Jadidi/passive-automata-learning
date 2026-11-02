import path from 'node:path';
import fs from 'node:fs/promises';
import {pathToFileURL,fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const skill='C:/Users/Mahdi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const contract=JSON.parse(await fs.readFile(path.join(root,'private/build_contract_R4.json'),'utf8'));
const result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(root,'private/candidate_R4_RTL.pptx'),finalPath:path.join(root,'output/Alphabet_Partition_Research_FA.pptx'),pythonExecutable:'C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...contract.tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:contract.tableOwners,fontPolicy:contract.fontPolicy,verifyArtifactToolImport:true,receiptPath:path.join(root,'private/final_validation.json')});
console.log(JSON.stringify(result));

