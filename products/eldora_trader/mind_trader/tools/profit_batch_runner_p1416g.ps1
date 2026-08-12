param([int]$DelaySeconds = 25)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Mouse {
  [DllImport("user32.dll")]
  public static extern void mouse_event(int dwFlags, int dx, int dy, int cButtons, int dwExtraInfo);
}
"@

$MOUSEEVENTF_LEFTDOWN = 0x02
$MOUSEEVENTF_LEFTUP   = 0x04

$EditorX = 1473
$EditorY = 180
$RunX = 1793
$RunY = 95

$files = @(
  "profit_import_package\p1416c_risk_f3_s21_t100.nts",
  "profit_import_package\p1416c_risk_f3_s21_t200.nts",
  "profit_import_package\p1416c_risk_f8_s34_t100.nts",
  "profit_import_package\p1416c_risk_f8_s34_t200.nts",
  "profit_import_package\p1416c_risk_f13_s55_t200.nts"
)

$outDir = "reports\P14.16G_PROFIT_AUTO_OK_RUNNER\screenshots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function RealClick($x,$y) {
  [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x,$y)
  Start-Sleep -Milliseconds 250
  [Mouse]::mouse_event($MOUSEEVENTF_LEFTDOWN,0,0,0,0)
  Start-Sleep -Milliseconds 100
  [Mouse]::mouse_event($MOUSEEVENTF_LEFTUP,0,0,0,0)
  Start-Sleep -Milliseconds 500
}

function Shot($name) {
  $bounds=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp=New-Object System.Drawing.Bitmap $bounds.Width,$bounds.Height
  $g=[System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($bounds.Location,[System.Drawing.Point]::Empty,$bounds.Size)
  $path=Join-Path $outDir "$name.png"
  $bmp.Save($path,[System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
  return $path
}

Write-Host "Clique no Profit. Automação começa em 5s..."
Start-Sleep 5

$results=@()

foreach ($file in $files) {
  $sid=[IO.Path]::GetFileNameWithoutExtension($file)
  $code=Get-Content $file -Raw
  Set-Clipboard -Value $code

  RealClick $EditorX $EditorY
  [System.Windows.Forms.SendKeys]::SendWait("^a")
  Start-Sleep -Milliseconds 300
  [System.Windows.Forms.SendKeys]::SendWait("^v")
  Start-Sleep -Seconds 1

  RealClick $RunX $RunY
  Start-Sleep -Seconds 3

  # Fecha popup "Erro de Sintaxe" se aparecer
  [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
  Start-Sleep -Milliseconds 700
  [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
  Start-Sleep -Milliseconds 700

  Start-Sleep -Seconds $DelaySeconds

  $shot=Shot $sid

  $results += [pscustomobject]@{
    strategy_id=$sid
    file=$file
    status="EXECUTED_OR_ERROR_CONFIRMED"
    screenshot=$shot
  }
}

$csv="reports\P14.16G_PROFIT_AUTO_OK_RUNNER\batch_results.csv"
$results | Export-Csv $csv -NoTypeInformation -Encoding UTF8
$results | Format-Table -AutoSize
Write-Host "CSV: $csv"
Write-Host "Screenshots: $outDir"
