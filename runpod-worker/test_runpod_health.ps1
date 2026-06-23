$ErrorActionPreference = "Stop"

$ApiKey = Read-Host "RUNPOD_API_KEY"
$EndpointId = Read-Host "RUNPOD_ENDPOINT_ID"

$BaseUrl = "https://api.runpod.ai/v2/$EndpointId"
$Headers = @{
  "Authorization" = "Bearer $ApiKey"
  "Content-Type"  = "application/json"
}

$Body = @{
  input = @{
    task = "health"
  }
} | ConvertTo-Json -Depth 10

$r = Invoke-RestMethod -Uri "$BaseUrl/run" -Method Post -Headers $Headers -Body $Body
$JobId = $r.id

Write-Host "JOB ID: $JobId"

do {
  Start-Sleep -Seconds 3
  $s = Invoke-RestMethod -Uri "$BaseUrl/status/$JobId" -Method Get -Headers $Headers
  $s | ConvertTo-Json -Depth 20
} while ($s.status -in @("IN_QUEUE","IN_PROGRESS"))
