$ErrorActionPreference='Stop'
$here=Split-Path -Parent $MyInvocation.MyCommand.Path
$root=Resolve-Path (Join-Path $here '..\..\..')
$python=Join-Path $root '.venv\Scripts\python.exe'
if(!(Test-Path $python)){
  $python='C:\Programación\AB-individual-v3c-20261110\.venv\Scripts\python.exe'
}
if(!(Test-Path $python)){throw 'Python no encontrado. Consulte README.md'}
$url='http://127.0.0.1:8765'
$running=$false
try{
  $result=Invoke-WebRequest -Uri ($url+'/api/state') -UseBasicParsing -TimeoutSec 2
  $running=$result.StatusCode -eq 200
}catch{}
if(-not $running){
  $p=Start-Process -FilePath $python -WorkingDirectory $here -ArgumentList @('server.py') -RedirectStandardOutput (Join-Path $here 'panel.stdout.log') -RedirectStandardError (Join-Path $here 'panel.stderr.log') -PassThru
  Write-Host ('Servidor local iniciado. PID: '+$p.Id)
  Start-Sleep -Seconds 2
}
Start-Process $url
Write-Host ('Abierto: '+$url)
