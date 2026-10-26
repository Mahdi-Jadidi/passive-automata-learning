$ErrorActionPreference = 'Stop'
$c003Root = Split-Path -Parent $PSScriptRoot
$c003Names = @('solver.py','general/general_solver.py','general/fair_reference.py','general/support.py','structural/fixed_word_solver.py','../partition_constraints_v2/baseline/partition_solver.py')
$c003Files = foreach ($c003Name in $c003Names) {
    $c003Path = Join-Path $c003Root $c003Name
    [ordered]@{path=$c003Name;sha256=(Get-FileHash -LiteralPath $c003Path -Algorithm SHA256).Hash.ToLowerInvariant();bytes=(Get-Item -LiteralPath $c003Path).Length}
}
$c003Manifest = [ordered]@{runtime_version='C003-R1';created_utc=(Get-Date).ToUniversalTime().ToString('o');purpose='Freeze candidates for independent comparison; acceptance is recorded separately';files=@($c003Files);capture_sha256=(Get-FileHash -LiteralPath (Join-Path $c003Root 'audit/capture.py') -Algorithm SHA256).Hash.ToLowerInvariant()}
$c003Output = Join-Path $PSScriptRoot 'runtime_manifest.json'
if (Test-Path -LiteralPath $c003Output) { throw 'Refusing to replace frozen runtime manifest' }
$c003Manifest | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $c003Output -Encoding utf8
$c003Manifest | ConvertTo-Json -Depth 7 -Compress
