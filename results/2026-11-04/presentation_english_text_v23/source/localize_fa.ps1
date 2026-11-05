param([string]$InputDeck,[string]$OutputDeck)
$ErrorActionPreference='Stop'
$inputPath=[IO.Path]::GetFullPath($InputDeck)
$outputPath=[IO.Path]::GetFullPath($OutputDeck)
if(Test-Path -LiteralPath $outputPath){throw 'Refusing to overwrite localized candidate'}
$hadPowerPoint=@(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$pp=$null;$deck=$null;$localized=0
try{
 $pp=New-Object -ComObject PowerPoint.Application
 $deck=$pp.Presentations.Open($inputPath,0,0,0)
 foreach($slide in $deck.Slides){
  foreach($shape in $slide.Shapes){
   if($shape.HasTextFrame -and $shape.TextFrame.HasText -and $shape.TextFrame.TextRange.Text -match '[\u0600-\u06FF]'){
    $shape.TextFrame.TextRange.ParagraphFormat.TextDirection=2
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment=3
    $shape.TextFrame.TextRange.Font.Name='Arial'
    $shape.TextFrame.TextRange.Font.NameComplexScript='Arial'
    $localized++
   }
   if($shape.HasTable){
    for($row=1;$row -le $shape.Table.Rows.Count;$row++){
     for($col=1;$col -le $shape.Table.Columns.Count;$col++){
      $range=$shape.Table.Cell($row,$col).Shape.TextFrame.TextRange
      if($range.Text -match '[\u0600-\u06FF]'){$range.ParagraphFormat.TextDirection=2;$range.ParagraphFormat.Alignment=2;$range.Font.Name='Arial';$range.Font.NameComplexScript='Arial';$localized++}
     }
    }
   }
  }
 }
 $deck.SaveAs($outputPath,24)
 Write-Output ('Explicit RTL set on {0} Persian text ranges' -f $localized)
}finally{
 if($null -ne $deck){$deck.Close();[void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck)}
 if($null -ne $pp){if(-not $hadPowerPoint){$pp.Quit()};[void][Runtime.InteropServices.Marshal]::ReleaseComObject($pp)}
}
