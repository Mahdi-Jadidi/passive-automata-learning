param([string]$InputDeck,[string]$RenderDirectory)
$ErrorActionPreference='Stop'
$taskDeckPath=[IO.Path]::GetFullPath($InputDeck)
$taskRenderPath=[IO.Path]::GetFullPath($RenderDirectory)
New-Item -ItemType Directory -Force -Path $taskRenderPath | Out-Null
$taskHadPowerPoint=@(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$taskPowerPoint=$null
$taskDeck=$null
try {
 $taskPowerPoint=New-Object -ComObject PowerPoint.Application
 $taskDeck=$taskPowerPoint.Presentations.Open($taskDeckPath,-1,0,0)
 $flags=@()
 foreach($slide in $taskDeck.Slides){
  $slide.Export((Join-Path $taskRenderPath ('slide-{0:d2}.png' -f $slide.SlideIndex)),'PNG',1280,720)
  foreach($shape in $slide.Shapes){
   if($shape.HasTextFrame -and $shape.TextFrame.HasText){
    $height=$shape.TextFrame2.TextRange.BoundHeight
    if($height -gt $shape.Height+3){$flags+=@{slide=$slide.SlideIndex;shape=$shape.Name;boundHeight=$height;boxHeight=$shape.Height;text=$shape.TextFrame.TextRange.Text}}
   }
  }
 }
 ConvertTo-Json -InputObject @($flags) -Depth 5 | Set-Content -LiteralPath (Join-Path $taskRenderPath 'text_fit.json') -Encoding utf8
 Write-Output ('PowerPoint rendered {0} slides; text-fit flags {1}' -f $taskDeck.Slides.Count,$flags.Count)
}finally{
 if($null -ne $taskDeck){$taskDeck.Close();[void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDeck)}
 if($null -ne $taskPowerPoint){if(-not $taskHadPowerPoint){$taskPowerPoint.Quit()};[void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskPowerPoint)}
}
