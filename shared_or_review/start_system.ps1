Write-Host 'STARTING ELDORA SYSTEM'

Start-Process powershell -ArgumentList 'uvicorn app.api.main:app --reload --port 8000'

Start-Sleep -Seconds 3

Write-Host 'API RUNNING ON http://localhost:8000'
Write-Host 'SYSTEM READY'
