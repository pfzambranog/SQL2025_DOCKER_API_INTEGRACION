# Configuración de variables
$host_ip = "127.0.0.1"
$port = "8443"
$cert = "./certs/cert.pem"
$key = "./certs/key.pem"

Write-Host "Iniciando API UC-01 en https://$($host_ip):$($port)..." -ForegroundColor Cyan

# Ejecución de Uvicorn con SSL
# En start_api_https.ps1
uvicorn api.main:app `
    --host 127.0.0.1 `
    --port 8443 `
    --ssl-keyfile ./certs/key.pem `
    --ssl-certfile ./certs/cert.pem `
    --reload