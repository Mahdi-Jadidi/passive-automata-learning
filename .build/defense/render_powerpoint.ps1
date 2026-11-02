param([string]$InputDeck,[string]$RenderDirectory)
$ErrorActionPreference='Stop'
$resolvedDeck=[IO.Path]::GetFullPath($InputDeck)
$resolvedRender=[IO.Path]::GetFullPath($RenderDirectory)
New-Item -ItemType Directory -Path $resolvedRender -Force | Out-Null
$hadPowerPoint=@(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$powerPoint=$null
$deck=$null
try {
    $powerPoint=New-Object -ComObject PowerPoint.Application
    $deck=$powerPoint.Presentations.Open($resolvedDeck,-1,0,0)
    $overflow=@()
    foreach($slide in $deck.Slides) {
        $target=Join-Path $resolvedRender ('slide-{0:d2}.png' -f $slide.SlideIndex)
        $slide.Export($target,'PNG',1600,900)
        foreach($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
                $bh=$shape.TextFrame2.TextRange.BoundHeight
                if($bh -gt ($shape.Height+3)) {
                    $overflow+=@{slide=$slide.SlideIndex;name=$shape.Name;boundHeight=$bh;shapeHeight=$shape.Height;text=$shape.TextFrame.TextRange.Text}
                }
            }
        }
    }
    $overflow | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $resolvedRender 'text-fit.json') -Encoding utf8
    $deck.SaveAs((Join-Path $resolvedRender 'deck-preview.pdf'),32)
    Write-Output ('Rendered {0} slides. Text-fit flags: {1}' -f $deck.Slides.Count,$overflow.Count)
}
finally {
    if($null -ne $deck){$deck.Close()}
    if($null -ne $powerPoint -and -not $hadPowerPoint){$powerPoint.Quit()}
    if($null -ne $deck){[void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck)}
    if($null -ne $powerPoint){[void][Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint)}
}
