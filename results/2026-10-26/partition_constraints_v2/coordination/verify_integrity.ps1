param()
$ErrorActionPreference = 'Stop'
$c002Root = Split-Path -Parent $PSScriptRoot
$c002Checks = [System.Collections.Generic.List[object]]::new()
function Add-C002HashCheck([string]$Kind, [string]$Path, [string]$Expected) {
    $c002Actual = if (Test-Path -LiteralPath $Path -PathType Leaf) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
    $c002Checks.Add([ordered]@{kind=$Kind; path=$Path; expected=$Expected; actual=$c002Actual; matches=($c002Actual -eq $Expected)})
}
$c002RunId = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffffffZ') + '_' + [guid]::NewGuid().ToString('N').Substring(0,8)
$c002RunDir = Join-Path $PSScriptRoot ('integrity_runs/' + $c002RunId)
New-Item -ItemType Directory -Path $c002RunDir -ErrorAction Stop | Out-Null
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $c002RunDir 'verify_integrity.ps1')
$c002Runtime = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'runtime_manifest.json') -Raw | ConvertFrom-Json -AsHashtable
foreach ($c002Item in $c002Runtime.files) { Add-C002HashCheck 'runtime' (Join-Path $c002Root $c002Item.path) $c002Item.sha256 }
$c002Baseline = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'baseline_manifest.json') -Raw | ConvertFrom-Json -AsHashtable
foreach ($c002Item in $c002Baseline.files) {
    Add-C002HashCheck 'baseline_copy' (Join-Path $c002Root ('baseline/' + $c002Item.path)) $c002Item.sha256
    Add-C002HashCheck 'baseline_original' (Join-Path (Split-Path -Parent $c002Root) ('alphabet_partition_research/' + $c002Item.path)) $c002Item.sha256
}
$c002CorpusRoot = Join-Path $c002Root 'audit/corpus/frozen_v1'
Add-C002HashCheck 'frozen_corpus_anchor' (Join-Path $c002CorpusRoot 'manifest.json') 'a4ef5c7124b9852cb30c5eb8e86f6e8bd1fa53bf3d4e9ab5d89d70f9b48efd13'
$c002Corpus = Get-Content -LiteralPath (Join-Path $c002CorpusRoot 'manifest.json') -Raw | ConvertFrom-Json -AsHashtable
foreach ($c002Group in @('datasets','truth_sidecars')) {
    foreach ($c002Item in $c002Corpus[$c002Group].Values) { Add-C002HashCheck 'frozen_corpus_file' (Join-Path $c002CorpusRoot $c002Item.path) $c002Item.sha256 }
}
$c002LegacyRoot = Join-Path $c002Root 'audit/corpus/legacy_generator_extension_v1'
if (Test-Path -LiteralPath (Join-Path $c002LegacyRoot 'manifest.json')) {
    $c002Legacy = Get-Content -LiteralPath (Join-Path $c002LegacyRoot 'manifest.json') -Raw | ConvertFrom-Json -AsHashtable
    foreach ($c002Name in $c002Legacy.files.Keys) { Add-C002HashCheck 'legacy_corpus_file' (Join-Path $c002LegacyRoot $c002Name) $c002Legacy.files[$c002Name].sha256 }
}
foreach ($c002Blob in (Get-ChildItem -LiteralPath $c002Root -File -Recurse | Where-Object { $_.FullName -match '[\\/]source_blobs[\\/][0-9a-f]{2}[\\/][0-9a-f]{64}$' })) {
    Add-C002HashCheck 'content_addressed_blob' $c002Blob.FullName $c002Blob.Name
}
foreach ($c002ResultFile in (Get-ChildItem -LiteralPath $c002Root -File -Recurse -Filter 'result.json')) {
    $c002Result = Get-Content -LiteralPath $c002ResultFile.FullName -Raw | ConvertFrom-Json -AsHashtable
    foreach ($c002Stream in @('stdout','stderr')) {
        if ($c002Result.ContainsKey($c002Stream + '_sha256')) {
            Add-C002HashCheck 'captured_stream' (Join-Path $c002ResultFile.DirectoryName ($c002Stream + '.bin')) $c002Result[$c002Stream + '_sha256']
        }
    }
}
$c002Failed = @($c002Checks | Where-Object { -not $_.matches })
$c002Report = [ordered]@{
    run_id=$c002RunId; at_utc=(Get-Date).ToUniversalTime().ToString('o');
    command_argv=@('pwsh','-NoProfile','-File',$PSCommandPath); cwd=(Get-Location).Path;
    script_sha256=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant();
    powershell_version=$PSVersionTable.PSVersion.ToString(); runtime=$c002Runtime.runtime_version;
    execution_status='success'; scientific_status='byte_integrity_only';
    check_count=$c002Checks.Count; failure_count=$c002Failed.Count; all_match=($c002Failed.Count -eq 0);
    checks=$c002Checks; limitations='Hash integrity does not establish mathematical correctness or completeness of missing historical evidence.'
}
if ($c002Failed.Count -gt 0) { $c002Report.execution_status = 'integrity_mismatch' }
$c002Report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $c002RunDir 'result.json') -Encoding utf8
[ordered]@{run_dir=$c002RunDir; checks=$c002Checks.Count; failed=$c002Failed.Count; all_match=($c002Failed.Count -eq 0)} | ConvertTo-Json -Compress
if ($c002Failed.Count -gt 0) { exit 1 }
