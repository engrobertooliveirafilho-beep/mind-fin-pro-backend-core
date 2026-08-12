Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Mouse {
 [DllImport("user32.dll")]
 public static extern void mouse_event(int dwFlags,int dx,int dy,int cButtons,int dwExtraInfo);
}
"@

$LEFTDOWN=0x02
$LEFTUP=0x04
$EditorX=1473
$EditorY=180
$RunX=1793
$RunY=95
$StopX=1907
$StopY=92

$pkg="profit_import_package"
$outDir="reports\P14.16P_NTSL_FUNCTION_PROBE\screenshots"
New-Item -ItemType Directory -Force -Path $pkg | Out-Null
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$tests=@(
@{id="p1416p_t01_media_close"; code="begin`r`n  if Media(9, Close) > Media(21, Close) then`r`n    BuyAtMarket;`r`nend;"},
@{id="p1416p_t02_media_no_space"; code="begin`r`n  if Media(9,Close) > Media(21,Close) then`r`n    BuyAtMarket;`r`nend;"},
@{id="p1416p_t03_media_open"; code="begin`r`n  if Media(9, Open) > Media(21, Open) then`r`n    BuyAtMarket;`r`nend;"},
@{id="p1416p_t04_mediaexp_close"; code="begin`r`n  if MediaExp(9, Close) > MediaExp(21, Close) then`r`n    BuyAtMarket;`r`nend;"},
@{id="p1416p_t05_mediaexp_no_space"; code="begin`r`n  if MediaExp(9,Close) > MediaExp(21,Close) then`r`n    BuyAtMarket;`r`nend;"},
@{id="p1416p_t06_mme_close"; code="begin`r`n  if MME(9, Close) > MME(21, Close) then`r`n    BuyAtMarket;`r`nend;"},
@{id="p1416p_t07_mma_close"; code="begin`r`n  if MMA(9, Close) > MMA(21, Close) then`r`n    BuyAtMarket;`r`nend;"},
@{id="p1416p_t08_media_movel"; code="begin`r`n  if MediaMovel(9, Close) > MediaMovel(21, Close) then`r`n    BuyAtMarket;`r`nend;"},
@{id="p1416p_t09_average"; code="begin`r`n  if Average(Close, 9) > Average(Close, 21) then`r`n    BuyAtMarket;`r`nend;"},
@{id="p1416p_t10_ema"; code="begin`r`n  if EMA(Close, 9) > EMA(Close, 21) then`r`n    BuyAtMarket;`r`nend;"}
)

foreach($t in $tests){
  $t.code | Set-Content -Encoding UTF8 "$pkg\$($t.id).nts"
}

function Click($x,$y){
 [System.Windows.Forms.Cursor]::Position=New-Object System.Drawing.Point($x,$y)
 Start-Sleep -Milliseconds 300
 [Mouse]::mouse_event($LEFTDOWN,0,0,0,0)
 Start-Sleep -Milliseconds 100
 [Mouse]::mouse_event($LEFTUP,0,0,0,0)
 Start-Sleep -Milliseconds 600
}

function Shot($name){
 $b=[System.Windows.Forms.SystemInformation]::VirtualScreen
 $bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height
 $g=[System.Drawing.Graphics]::FromImage($bmp)
 $g.CopyFromScreen($b.Left,$b.Top,0,0,$b.Size)
 $p=Join-Path $outDir "$name.png"
 $bmp.Save($p,[System.Drawing.Imaging.ImageFormat]::Png)
 $g.Dispose(); $bmp.Dispose()
 return $p
}

Write-Host "P14.16P: $($tests.Count) testes. Clique no Profit. Iniciando em 5s..."
Start-Sleep 5

$results=@()

foreach($t in $tests){
 $sid=$t.id
 $file="$pkg\$sid.nts"
 $raw=Get-Content $file -Raw
 $lines=$raw -split "`r?`n"

 Click $EditorX $EditorY
 [System.Windows.Forms.SendKeys]::SendWait("^a")
 Start-Sleep -Milliseconds 500
 [System.Windows.Forms.SendKeys]::SendWait("{DELETE}")
 Start-Sleep -Milliseconds 500

 foreach($line in $lines){
   if($line.Trim().Length -gt 0){
     Set-Clipboard -Value $line
     [System.Windows.Forms.SendKeys]::SendWait("^v")
   }
   [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
   Start-Sleep -Milliseconds 120
 }

 Start-Sleep -Seconds 2
 Click $RunX $RunY
 Start-Sleep -Seconds 5
 Click $StopX $StopY
 Start-Sleep -Seconds 1
 [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
 Start-Sleep -Milliseconds 800

 $shot=Shot $sid
 Write-Host "OK: $sid -> $shot"

 $results += [pscustomobject]@{
   strategy_id=$sid
   file="$sid.nts"
   screenshot=$shot
 }
}

$csv="reports\P14.16P_NTSL_FUNCTION_PROBE\results.csv"
$results | Export-Csv $csv -NoTypeInformation -Encoding UTF8
Write-Host "CSV: $csv"
Write-Host "Screenshots: $outDir"
