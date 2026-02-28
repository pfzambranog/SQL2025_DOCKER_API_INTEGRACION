# SQL Bridge API - Caso de Uso UC-01

Esta API actúa como puente de comunicación seguro entre instancias de SQL Server (2017 y 2025). Permite ejecutar procedimientos almacenados y consultas directas mediante una interfaz RESTful sobre HTTPS, facilitando la integración de ambientes on-premiss y contenedores Docker.

## 📁 Estructura del Proyecto
api/
├ start_api_https.ps1    # Script de inicio (PowerShell)
├ README.md              # Documentación técnica
├ .env                   # Variables de entorno y credenciales
├ certs/                 # Certificados SSL (.pem)
├  ├── key.pem            # Clave privada
│  ├── cert.pem           # Certificado público
│  ├── cert_config.cnf   # Configuración para generación de certificados
| api/
│  ├── main.py           # Lógica principal y endpoints
│  ├── security.py       # Validación de API Key y Base64
│  ├── config.py         # Configuración de conexiones
│  └── requirements.txt  # Dependencias de Python
└ logs/                  # Logs locales del sistema

## Configuracion de la generacion de certificados SSL

import os
import base64
from dotenv import load_dotenv

load_dotenv()

def get_db_credentials(server_name):
    # Limpiar el nombre del servidor para el formato de variable de entorno
    clean_name = server_name.replace(".", "_").upper()
    user = os.getenv(f"DB_SERVER_{clean_name}_USER")
    b64_pass = os.getenv(f"DB_SERVER_{clean_name}_PASS")
    
    if not user or not b64_pass:
        raise ValueError(f"Configuración no encontrada para el servidor: {server_name}")
        
    password = base64.b64decode(b64_pass).decode('utf-8')
    return user, password
    
## 🛠 Configuración del Entorno (.env)
Las credenciales deben estar en Base64. Para el servidor Docker, se especifica el puerto 15000.
.env
API_KEY=tu_clave_secreta_aqui
DB_SERVER_127_0_0_1_USER=sa
DB_SERVER_127_0_0_1_PASS=UGFzc3dvcmQxMjM=
DB_SERVER_SQL2025_DOCKER_USER=sa
DB_SERVER_SQL2025_DOCKER_PASS=RG9ja2VyUGFzczQ1Ng==

🔐 Seguridad y Auditoría
HTTPS: Obligatorio mediante certificados en puerto 8443.

Autenticación: Header obligatorio api-key.

Auditoría: Todas las peticiones se registran en la tabla Sistema_Logs_API en la base de datos ERP_DB.

🚀 Endpoints Principales
1. Ejecución de Consultas (POST /execute)
Entrada (Request JSON):

JSON
{ 
  "server": "SQL2025_DOCKER",
  "database": "ERP_DB",
  "operation": "Procedimiento",
  "procedure": "sp_consultaAPI",
  "parameters": {"Parametro1": "1111", "Parametro2": "AAA"}
}
Salida (Response JSON):

JSON
{
  "status": "success",
  "data": [
    { "criterio": "diaSemana", "descripcion": "Miercoles", "valor": 3 }
  ]
}
2. Salud del Sistema (GET /health)
Verifica la disponibilidad de la API y versión actual.

💻 Instalación Rápida
Instalar dependencias: pip install -r api/requirements.txt

Generar certificados en la carpeta certs/: openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -nodes -days 365

Iniciar el servicio: ./start_api_https.ps1
