param([int]$DelaySeconds = 10)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$EditorX=2043
$EditorY=76
$RunX=1446
$RunY=139

$files = @(
"profit_import_package\p1416c_risk_f3_s21_t100.nts",
"profit_import_package\p1416c_risk_f3_s21_t200.nts",
"profit_import_package\p1416c_risk_f8_s34_t100.nts",
"profit_import_package\p1416c_risk_f8_s34_t200.nts",
"profit_import_package\p1416c_risk_f13_s55_t200.nts"
)

$outDir="reports\P14.16D_PROFIT_BATCH_AUTOMATION\screenshots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function ClickAt($x, $y) {
  [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x, $y)
  Start-Sleep -Milliseconds 300
  [System.Windows.Forms.SendKeys]::SendWait("{LEFTCLICK}")
}

function SaveShot($name) {
  $bounds=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp=New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
  $g=[System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($bounds.Location,[System.Drawing.Point]::Empty,$bounds.Size)
  $path=Join-Path $outDir "$name.png"
  $bmp.Save($path,[System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
  return $path
}

$results=@()

foreach ($file in $files) {
  $sid=[IO.Path]::GetFileNameWithoutExtension($file)
  $code=Get-Content $file -Raw
  Set-Clipboard $code

  [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($EditorX, $EditorY)
  Start-Sleep -Milliseconds 500
  [System.Windows.Forms.SendKeys]::SendWait("^a")
  Start-Sleep -Milliseconds 300
  [System.Windows.Forms.SendKeys]::SendWait("^v")
  Start-Sleep -Milliseconds 700

  [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($RunX, $RunY)
  Start-Sleep -Milliseconds 500
  [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

  Start-Sleep -Seconds $DelaySeconds

  $shot=SaveShot $sid

  $results += [pscustomobject]@{
    strategy_id=$sid
    file=$file
    screenshot=$shot
    status="RUN_ATTEMPTED"
  }
}

$results | Export-Csv "reports\P14.16D_PROFIT_BATCH_AUTOMATION\batch_results.csv" -NoTypeInformation -Encoding UTF8
$results | Format-Table -AutoSize
