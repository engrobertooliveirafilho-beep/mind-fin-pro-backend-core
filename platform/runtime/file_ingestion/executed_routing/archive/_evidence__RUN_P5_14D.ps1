Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core"
$P514C = "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P5_14C_SELECTED_SOURCE_PROCESSING_20260615_141635"
$EvidenceRoot = Join-Path $RepoRoot "_evidence\P5_14D_READ_TOP_CANONICAL_SOURCE_CONTENT_$(Get-Date -Format yyyyMMdd_HHmmss)"
New-Item -ItemType Directory -Force $EvidenceRoot | Out-Null

$RemoteName = "gdrive"
$DriveFolderId = "1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

$top = Get-Content "$P514C\P5_14C_TOP20_SELECTED_FILES.json" -Raw | ConvertFrom-Json
$targets = $top | Where-Object { $_.decision -in @("CANONICAL_SOURCE","TEST_EVIDENCE") } | Select-Object -First 15

$Result = @()

foreach ($t in $targets) {
    Write-Host "Reading:" $t.path

    try {
        $content = rclone cat "$RemoteName`:$($t.path)" --drive-root-folder-id $DriveFolderId 2>$null
    } catch {
        $content = $null
    }

    if (-not $content) {
        $Result += [pscustomobject]@{
            path = $t.path
            decision = $t.decision
            read_ok = $false
            reason = "rclone_cat_failed"
        }
        continue
    }

    $text = ($content -join "`n")

    $classes = [regex]::Matches($text, "(?m)^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)") | ForEach-Object { $_.Groups[1].Value }
    $funcs   = [regex]::Matches($text, "(?m)^\s*(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)") | ForEach-Object { $_.Groups[1].Value }
    $imports = [regex]::Matches($text, "(?m)^\s*(?:from|import)\s+.+") | ForEach-Object { $_.Value.Trim() }

    $Result += [pscustomobject]@{
        path = $t.path
        decision = $t.decision
        role = $t.role
        score = $t.score
        read_ok = $true
        bytes = $text.Length
        class_count = @($classes).Count
        function_count = @($funcs).Count
        import_count = @($imports).Count
        has_dataclass = $text -match "@dataclass"
        has_pydantic = $text -match "BaseModel"
        has_enum = $text -match "\bEnum\b"
        classes = @($classes)
        functions = @($funcs)
        imports = @($imports)
        preview = $text.Substring(0, [Math]::Min(4000, $text.Length))
    }
}

$Result | ConvertTo-Json -Depth 30 | Out-File (Join-Path $EvidenceRoot "P5_14D_SOURCE_CONTENT_EXTRACTION.json") -Encoding UTF8
$Result | Select-Object path,decision,read_ok,bytes,class_count,function_count,import_count,has_dataclass,has_pydantic,has_enum,classes,functions |
Export-Csv (Join-Path $EvidenceRoot "P5_14D_SOURCE_CONTENT_SUMMARY.csv") -NoTypeInformation -Encoding UTF8

$ReadOk = @($Result | Where-Object {$_.read_ok -eq $true}).Count

$Final = [pscustomobject]@{
    mission = "P5.14D_READ_TOP_CANONICAL_SOURCE_CONTENT"
    read_targets = @($targets).Count
    read_ok = $ReadOk
    read_failed = @($targets).Count - $ReadOk
    hierarchical_planner_step449_status = if ($ReadOk -gt 0) { "SOURCE_CONTENT_EXTRACTED" } else { "SOURCE_CONTENT_NOT_READ" }
    next_required_action = "P5.14E_STRUCTURAL_DECISION_MATRIX"
    build_allowed = $false
    integration_allowed = $false
    move_allowed = $false
    archive_allowed = $false
    code_changed = $false
}

$Final | ConvertTo-Json -Depth 10 | Out-File (Join-Path $EvidenceRoot "P5_14D_FINAL_STATUS.json") -Encoding UTF8

Write-Host ""
Write-Host "P5.14D COMPLETE"
Write-Host "TARGETS:" @($targets).Count
Write-Host "READ OK:" $ReadOk
Write-Host "OUTPUT:" $EvidenceRoot
