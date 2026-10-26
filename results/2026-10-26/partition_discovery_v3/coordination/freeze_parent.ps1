$ErrorActionPreference = 'Stop'
$c003Root = Split-Path -Parent $PSScriptRoot
$c003Parent = Join-Path (Split-Path -Parent $c003Root) 'partition_constraints_v2'
$c003Runtime = Get-Content -LiteralPath (Join-Path $c003Parent 'coordination/runtime_manifest.json') -Raw | ConvertFrom-Json -AsHashtable
$c003Files = [System.Collections.Generic.List[object]]::new()
foreach ($c003Item in $c003Runtime.files) {
    $c003Actual = (Get-FileHash -LiteralPath (Join-Path $c003Parent $c003Item.path) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($c003Actual -ne $c003Item.sha256) { throw ('Changed parent runtime: ' + $c003Item.path) }
    $c003Files.Add([ordered]@{path=('../partition_constraints_v2/' + $c003Item.path);sha256=$c003Actual;role='frozen_parent_runtime'})
}
$c003Refs = @('coordination/runtime_manifest.json','coordination/baseline_manifest.json','baseline/THEORY_NOTE.md','baseline/partition_solver.py','audit/corpus/frozen_v1/manifest.json','audit/correctness_runs/20261026T125503.860658Z_805e5494/summary.json','audit/correctness_validation/20261026T133346.038161Z_8ba0e9bf/validation_report.json','audit/benchmark_validation/20261026T142254.406767Z_079436eb/validation_report.json','MASTER_DECISION_FA.md')
foreach ($c003Ref in $c003Refs) {
    $c003Path = Join-Path $c003Parent $c003Ref
    $c003Files.Add([ordered]@{path=('../partition_constraints_v2/' + $c003Ref);sha256=(Get-FileHash -LiteralPath $c003Path -Algorithm SHA256).Hash.ToLowerInvariant();role='parent_reference'})
}
$c003Record = [ordered]@{cycle='C003';parent_commit='96f03adccea5e3d41278b8a7047a39e57639e15a';created_utc=(Get-Date).ToUniversalTime().ToString('o');copied_capture_sha256=(Get-FileHash -LiteralPath (Join-Path $c003Root 'audit/capture.py') -Algorithm SHA256).Hash.ToLowerInvariant();script_sha256=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant();files=$c003Files;copies_of_parent_logs_created=$false;all_runtime_hashes_match=$true}
$c003Output = Join-Path $PSScriptRoot 'parent_manifest.json'
if (Test-Path -LiteralPath $c003Output) { throw 'Refusing to replace the parent manifest' }
$c003Record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $c003Output -Encoding utf8
[ordered]@{path=$c003Output;references=$c003Files.Count;all_match=$true} | ConvertTo-Json -Compress
