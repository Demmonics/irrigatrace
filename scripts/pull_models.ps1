# Usage: .\scripts\pull_models.ps1 qwen3:4b nomic-embed-text
# Starts each model download in the BACKGROUND and returns immediately. Never block on this.
New-Item -ItemType Directory -Force .logs,.state | Out-Null
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { Write-Host "ollama not installed -> https://ollama.com/download"; exit 1 }
try { Invoke-WebRequest http://localhost:11434/api/tags -UseBasicParsing | Out-Null } catch { Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden; Start-Sleep 4 }
foreach ($m in $args) {
  if (ollama list | Select-String -SimpleMatch $m) { Write-Host "present: $m"; continue }
  $log = ".logs\pull-" + ($m -replace '[:/]','_') + ".log"
  Start-Process -FilePath ollama -ArgumentList "pull",$m -RedirectStandardOutput $log -RedirectStandardError "$log.err" -WindowStyle Hidden
  Write-Host "started in background: $m (log: $log)"
}
