param()

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

$files=Get-ChildItem profit_import_package\p1416i_*.nts | Sort-Object Name

$outDir="reports\P14.16L_DUAL_MONITOR_AUTORUN\screenshots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function Click($x,$y){
 [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x,$y)
 Start-Sleep -Milliseconds 250
 [Mouse]::mouse_event($LEFTDOWN,0,0,0,0)
 Start-Sleep -Milliseconds 100
 [Mouse]::mouse_event($LEFTUP,0,0,0,0)
 Start-Sleep -Milliseconds 500
}

function Shot($name){
 $b=[System.Windows.Forms.SystemInformation]::VirtualScreen
 $bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height
 $g=[System.Drawing.Graphics]::FromImage($bmp)
 $g.CopyFromScreen($b.Left,$b.Top,0,0,$b.Size)
 $p=Join-Path $outDir "$name.png"
 $bmp.Save($p,[System.Drawing.Imaging.ImageFormat]::Png)
 $g.Dispose()
 $bmp.Dispose()
 return $p
}

Write-Host "Clique no Profit. Iniciando em 5 segundos..."
Start-Sleep 5

$results=@()

foreach($file in $files){
 $sid=$file.BaseName
 $code=Get-Content $file.FullName -Raw
 Set-Clipboard $code

 Click $EditorX $EditorY
 [System.Windows.Forms.SendKeys]::SendWait("^a")
 Start-Sleep -Milliseconds 300
 [System.Windows.Forms.SendKeys]::SendWait("{DELETE}")
 Start-Sleep -Milliseconds 300
 [System.Windows.Forms.SendKeys]::SendWait("^v")
 Start-Sleep -Seconds 1

 Click $RunX $RunY
 Start-Sleep -Seconds 5

 Click $StopX $StopY
 Start-Sleep -Seconds 1

 [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
 Start-Sleep -Milliseconds 500

 $shot=Shot $sid

 $results += [pscustomobject]@{
   strategy_id=$sid
   screenshot=$shot
 }
}

$csv="reports\P14.16L_DUAL_MONITOR_AUTORUN\results.csv"
$results | Export-Csv $csv -NoTypeInformation -Encoding UTF8

Write-Host "CSV: $csv"
Write-Host "Screenshots: $outDir"
