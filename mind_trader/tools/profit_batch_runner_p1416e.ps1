param([int]$DelaySeconds = 20)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$EditorX = 1473
$EditorY = 180
$RunX = 1793
$RunY = 95
$StopX = 1907
$StopY = 92

$files = @(
  "profit_import_package\p1416c_risk_f3_s21_t100.nts",
  "profit_import_package\p1416c_risk_f3_s21_t200.nts",
  "profit_import_package\p1416c_risk_f8_s34_t100.nts",
  "profit_import_package\p1416c_risk_f8_s34_t200.nts",
  "profit_import_package\p1416c_risk_f13_s55_t200.nts"
)

$outDir = "reports\P14.16E_PROFIT_BATCH_RUNNER\screenshots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function ClickAt($x,$y) {
  [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x,$y)
  Start-Sleep -Milliseconds 300
  [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
  Start-Sleep -Milliseconds 500
}

function Shot($name) {
  $bounds=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp=New-Object System.Drawing.Bitmap $bounds.Width,$bounds.Height
  $g=[System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($bounds.Location,[System.Drawing.Point]::Empty,$bounds.Size)
  $path=Join-Path $outDir "$name.png"
  $bmp.Save($path,[System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose()
  $bmp.Dispose()
  return $path
}

Write-Host "Clique no Profit e não mexa em nada. Começando em 5s..."
Start-Sleep 5

$results=@()

foreach ($file in $files) {
  $sid=[IO.Path]::GetFileNameWithoutExtension($file)
  $code=Get-Content $file -Raw
  Set-Clipboard -Value $code

  [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($EditorX,$EditorY)
  Start-Sleep -Milliseconds 500
  [System.Windows.Forms.SendKeys]::SendWait("^a")
  Start-Sleep -Milliseconds 300
  [System.Windows.Forms.SendKeys]::SendWait("^v")
  Start-Sleep -Seconds 1

  ClickAt $RunX $RunY
  Start-Sleep -Seconds $DelaySeconds

  $shot=Shot $sid

  $results += [pscustomobject]@{
    strategy_id=$sid
    file=$file
    status="EXECUTED_SCREENSHOT_CAPTURED"
    screenshot=$shot
  }
}

$csv="reports\P14.16E_PROFIT_BATCH_RUNNER\batch_results.csv"
$results | Export-Csv $csv -NoTypeInformation -Encoding UTF8
$results | Format-Table -AutoSize
Write-Host "CSV: $csv"
Write-Host "Screenshots: $outDir"
