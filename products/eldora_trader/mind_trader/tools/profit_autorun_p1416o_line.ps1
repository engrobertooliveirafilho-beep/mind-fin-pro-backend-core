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

$files=@(
"profit_import_package\p1416i_t01_buy_only.nts",
"profit_import_package\p1416i_t02_close_open.nts",
"profit_import_package\p1416i_t03_media_9_21.nts",
"profit_import_package\p1416i_t04_media_no_space.nts",
"profit_import_package\p1416i_t05_media_one_arg.nts",
"profit_import_package\p1416i_t06_mediaexp_two_args.nts",
"profit_import_package\p1416i_t07_mediaexp_one_arg.nts"
)

$outDir="reports\P14.16O_LINE_BY_LINE_AUTORUN\screenshots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

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

Write-Host "Clique no Profit. Iniciando em 5s..."
Start-Sleep 5

$results=@()

foreach($file in $files){
 $sid=[IO.Path]::GetFileNameWithoutExtension($file)
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
   screenshot=$shot
 }
}

$csv="reports\P14.16O_LINE_BY_LINE_AUTORUN\results.csv"
$results | Export-Csv $csv -NoTypeInformation -Encoding UTF8
Write-Host "CSV: $csv"
Write-Host "Screenshots: $outDir"
