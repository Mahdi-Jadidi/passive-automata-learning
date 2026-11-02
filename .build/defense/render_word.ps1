param([string]$InputDocument,[string]$PdfPath)
$ErrorActionPreference='Stop'
$resolvedDocument=[IO.Path]::GetFullPath($InputDocument)
$resolvedPdf=[IO.Path]::GetFullPath($PdfPath)
$hadWord=@(Get-Process WINWORD -ErrorAction SilentlyContinue).Count -gt 0
$word=$null;$document=$null
try {
    $word=New-Object -ComObject Word.Application
    if(-not $hadWord){$word.Visible=$false}
    $document=$word.Documents.Open($resolvedDocument,$false,$true)
    $document.ExportAsFixedFormat($resolvedPdf,17)
    Write-Output ('Word rendered {0} pages' -f $document.ComputeStatistics(2))
}
finally {
    if($null -ne $document){$document.Close(0)}
    if($null -ne $word -and -not $hadWord){$word.Quit()}
    if($null -ne $document){[void][Runtime.InteropServices.Marshal]::ReleaseComObject($document)}
    if($null -ne $word){[void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)}
}
