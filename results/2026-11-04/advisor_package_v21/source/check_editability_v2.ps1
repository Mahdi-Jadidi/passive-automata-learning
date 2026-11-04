param([string]$InputDeck,[string]$TestCopy,[string]$Receipt)
$ErrorActionPreference='Stop'
$taskSource=[IO.Path]::GetFullPath($InputDeck)
$taskCopy=[IO.Path]::GetFullPath($TestCopy)
$taskHash=(Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash
if(Test-Path -LiteralPath $taskCopy){throw 'Test copy exists'}
$taskHadPowerPoint=@(Get-Process POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
$taskPP=$null;$taskDeck=$null
try{
 $taskPP=New-Object -ComObject PowerPoint.Application
 Copy-Item -LiteralPath $taskSource -Destination $taskCopy
 $taskDeck=$taskPP.Presentations.Open($taskCopy,0,0,0)
 $taskTable=@($taskDeck.Slides.Item(3).Shapes | Where-Object {$_.HasTable -eq -1})[0].Table
 $taskCell=$taskTable.Cell(2,1).Shape.TextFrame.TextRange
 $taskOriginalText=$taskCell.Text
 $taskCell.Text=$taskOriginalText+' TEST'
 if($taskCell.Text -notmatch 'TEST'){throw 'Native table edit failed'}
 $taskCell.Text=$taskOriginalText
 $taskShape=@($taskDeck.Slides.Item(12).Shapes | Where-Object {$_.HasChart -eq -1})[0]
 $taskWidth=$taskShape.Width
 $taskShape.Width=$taskWidth-1
 $taskShape.Width=[double]$taskWidth
 $taskSeries=$taskShape.Chart.SeriesCollection(1)
 $taskValues=@($taskSeries.Values)
 if($taskValues.Count -ne 2){throw 'Unexpected editable chart series'}
 $taskChanged=@($taskValues);$taskChanged[0]=[double]$taskValues[0]+0.01
 $taskSeries.Values=$taskChanged
 if([math]::Abs([double]@($taskSeries.Values)[0]-[double]$taskChanged[0]) -gt 0.0000001){throw 'Chart edit failed'}
 $taskSeries.Values=$taskValues
 $taskDeck.Save()
 $taskDeck.Close()
 [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDeck)
 $taskDeck=$taskPP.Presentations.Open($taskCopy,-1,0,0)
 $taskReopened=@($taskDeck.Slides.Item(12).Shapes | Where-Object {$_.HasChart -eq -1})[0]
 $taskReopenedValues=@($taskReopened.Chart.SeriesCollection(1).Values)
 if([math]::Abs([double]$taskReopenedValues[0]-[double]$taskValues[0]) -gt 0.0000001){throw 'Saved editable chart values changed'}
 if((Get-FileHash -LiteralPath $taskSource -Algorithm SHA256).Hash -ne $taskHash){throw 'Final source changed'}
 @{status='passed';table_cell_edited_and_restored=$true;chart_resized_edited_restored_and_reopened=$true;final_file_unchanged=$true;final_sha256=$taskHash} | ConvertTo-Json | Set-Content -LiteralPath $Receipt -Encoding utf8
 Write-Output 'Native table and chart editability verified in a separate PowerPoint copy'
}finally{
 if($null -ne $taskDeck){$taskDeck.Close();[void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDeck)}
 if($null -ne $taskPP){if(-not $taskHadPowerPoint){$taskPP.Quit()};[void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskPP)}
}
