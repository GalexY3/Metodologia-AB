$ErrorActionPreference = 'Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$py=Join-Path (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $root))) '.venv\Scripts\python.exe'
$url='http://127.0.0.1:8766/'
$online=$false
try {
  $r=Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 2
  $online=$r.StatusCode -eq 200
} catch {}
if(-not $online) {
  Start-Process -FilePath $py -ArgumentList @('-u','server.py') -WorkingDirectory $root -WindowStyle Hidden | Out-Null
  Start-Sleep -Seconds 2
}
Start-Process $url
