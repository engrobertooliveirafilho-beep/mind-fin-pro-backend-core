from pathlib import Path
import json
from datetime import datetime, timezone

STATUS = "P14.16B_PROFIT_UI_AUTOMATION_HARNESS_IMPLEMENTED"

ROOT = Path(".")
REPORT_DIR = ROOT / "reports" / "P14.16B_PROFIT_UI_AUTOMATION"
SCRIPT = ROOT / "tools" / "profit_compile_clipboard_runner.ps1"

FILES = [
    "profit_import_package/p1416a_l1_trend_filter.nts",
    "profit_import_package/p1416a_l2_stop_points_probe.nts",
    "profit_import_package/p1416a_l3_take_points_probe.nts",
    "profit_import_package/p1416a_l4_stop_take_probe.nts",
]

POWERSHELL = r'''
param(
  [int]$DelaySeconds = 3
)

$ErrorActionPreference="Stop"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$files = @(
  "profit_import_package\p1416a_l1_trend_filter.nts",
  "profit_import_package\p1416a_l2_stop_points_probe.nts",
  "profit_import_package\p1416a_l3_take_points_probe.nts",
  "profit_import_package\p1416a_l4_stop_take_probe.nts"
)

$outDir = "reports\P14.16B_PROFIT_UI_AUTOMATION\screenshots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function Send-KeyCombo($keys) {
  [System.Windows.Forms.SendKeys]::SendWait($keys)
  Start-Sleep -Milliseconds 500
}

function Save-Screenshot($name) {
  $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
  $graphics = [System.Drawing.Graphics]::FromImage($bmp)
  $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
  $path = Join-Path $outDir "$name.png"
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $graphics.Dispose()
  $bmp.Dispose()
  return $path
}

Write-Host "FOCO NECESSÁRIO:"
Write-Host "1. Clique dentro do editor de código do Profit."
Write-Host "2. Deixe o cursor dentro da área branca do código."
Write-Host "3. Não mexa no mouse/teclado durante a execução."
Write-Host "4. Iniciando em 8 segundos..."
Start-Sleep -Seconds 8

$results = @()

foreach ($file in $files) {
  if (!(Test-Path $file)) {
    $results += [pscustomobject]@{
      file=$file; status="FILE_NOT_FOUND"; screenshot=""
    }
    continue
  }

  $code = Get-Content $file -Raw
  Set-Clipboard -Value $code

  Send-KeyCombo("^a")
  Send-KeyCombo("^v")

  Start-Sleep -Seconds 1

  # F9 costuma executar/compilar. Se no seu Profit não funcionar, trocaremos para botão/atalho correto.
  Send-KeyCombo("{F9}")

  Start-Sleep -Seconds $DelaySeconds

  $safe = ($file -replace '[\\/:*?"<>|]', '_')
  $shot = Save-Screenshot $safe

  $results += [pscustomobject]@{
    file=$file
    status="SCREENSHOT_CAPTURED_REQUIRES_REVIEW"
    screenshot=$shot
  }
}

$csv = "reports\P14.16B_PROFIT_UI_AUTOMATION\ui_run_results.csv"
$results | Export-Csv $csv -NoTypeInformation -Encoding UTF8

Write-Host "`nRESULTADOS:"
$results | Format-Table -AutoSize
Write-Host "`nCSV: $csv"
Write-Host "Screenshots em: $outDir"
'''

def run():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPT.parent.mkdir(parents=True, exist_ok=True)
    SCRIPT.write_text(POWERSHELL.strip() + "\n", encoding="utf-8")

    manifest = {
        "STATUS": STATUS,
        "SCRIPT": str(SCRIPT),
        "FILES": FILES,
        "MODE": "UI automation via clipboard + F9 + screenshot capture",
        "LIMITATION": "Requires Profit editor focused manually before run. Does not place real orders.",
        "REAL_ORDERS": "FORBIDDEN",
        "REAL_BROKER": "DISABLED",
        "LIVE": "FORBIDDEN",
        "EDGE": "NOT_PROVEN",
        "CAUSALITY": "NOT_PROVEN",
        "EXPORT_READY": True,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    (REPORT_DIR / "P14.16B_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return manifest

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
