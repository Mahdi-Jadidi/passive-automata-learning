$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot 'output\Exact_Alphabet_Partitioning_Article_FA_Exact.docx'
$qaDir = Join-Path $PSScriptRoot 'qa_fa_exact'
New-Item -ItemType Directory -Path $qaDir -Force | Out-Null
$pdf = Join-Path $qaDir 'translation.pdf'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($source, $false, $true, $false)
    $document.ExportAsFixedFormat($pdf, 17)
    $document.Close(0)
    $document = $null
    $word.Quit()
    $word = $null
    Get-Item -LiteralPath $pdf | Select-Object FullName,Length
}
finally {
    if ($null -ne $document) { $document.Close(0) }
    if ($null -ne $word) { $word.Quit() }
}
