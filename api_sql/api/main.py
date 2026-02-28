import os
import base64
import pyodbc
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from dotenv import load_dotenv
from typing import Dict, Any

# Cargar variables de entorno desde el archivo.env
load_dotenv()

# --- Configuración de la aplicación FastAPI ---
app = FastAPI(title="SQL Bridge API UC-01")

# --- CONFIGURACIÓN DE SEGURIDAD Y CREDENCIALES ---

# Cargar la API Key esperada desde las variables de entorno
# Se asume que el archivo.env está en el directorio padre de 'api',
# donde se ejecuta el script start_api_https.ps1.
API_KEY_EXPECTED = os.getenv("API_KEY", "").strip()

# --- DEBUG: Verifica que la API Key se carga correctamente ---
print(f"DEBUG: API_KEY_EXPECTED cargada: '{API_KEY_EXPECTED}'")

def get_db_credentials(server_name: str):
    """Extrae y decodifica credenciales desde el.env con limpieza estricta.
    
    server_name debe coincidir con el sufijo en DB_SERVER_{server_name_limpio}_USER/PASS
    Ej: "127.0.0.1" -> DB_SERVER_127_0_0_1_USER
        "SQL2025_DOCKER" -> DB_SERVER_SQL2025_DOCKER_USER
    """
    clean_name = server_name.replace(".", "_").replace(",", "_").upper() # También limpia comas para nombres como "localhost,15000"
    user = os.getenv(f"DB_SERVER_{clean_name}_USER")
    b64_pass = os.getenv(f"DB_SERVER_{clean_name}_PASS")
    
    if not user or not b64_pass:
        raise ValueError(f"Configuración de credenciales no encontrada para el servidor: {server_name}. "
                         f"Buscando con clave: DB_SERVER_{clean_name}_USER/PASS")
        
    password = base64.b64decode(b64_pass.strip()).decode('utf-8').strip()
    return user.strip(), password

async def verify_api_key(api_key: str = Header(None, alias="api-key")):
    """Valida la API Key enviada en el header."""
    if not api_key or api_key.strip()!= API_KEY_EXPECTED:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado: API Key inválida"
        )

# --- SISTEMA DE AUDITORÍA ---

def log_to_database(ip: str, operation: str, server_destination: str, status: str, error_msg: str = None):
    """Registra auditoría en el SQL Server de Docker (local) con debug activo."""
    print(f"DEBUG: Intentando registrar log para {operation} en servidor de auditoría...")
    try:
        # Se asume que el servidor de auditoría es la instancia de SQL Server en Docker,
        # accesible vía 127.0.0.1:15000 con el usuario SA.
        # Las credenciales se buscan con el nombre "127.0.0.1" en el.env
        user_audit, password_audit = get_db_credentials("127.0.0.1") # Busca DB_SERVER_127_0_0_1_USER/PASS
        
        conn_str_audit = (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};' # Actualizado a Driver 18
            f'SERVER=127.0.0.1,15000;' # Puerto 15000 para Docker
            f'DATABASE=master;' # Usamos 'master' por ahora, asegúrate de que exista ERP_DB y la tabla.
            f'UID={user_audit};PWD={{{password_audit}}};'
            f'TrustServerCertificate=yes;'
            f'Connection Timeout=5;'
        )
        
        with pyodbc.connect(conn_str_audit) as conn_audit:
            cursor_audit = conn_audit.cursor()
            query_audit = """
                -- Asegúrate de que esta tabla exista en la DB 'master' o la DB que uses para auditoría
                -- CREATE TABLE [dbo].[Sistema_Logs_API] (
                -- ID INT IDENTITY(1,1) PRIMARY KEY,
                -- Cliente_IP VARCHAR(50),
                -- Operacion VARCHAR(255),
                -- Servidor_Destino VARCHAR(255),
                -- Estado VARCHAR(50),
                -- Detalle_Error NVARCHAR(MAX),
                -- Fecha_Hora DATETIME,
                -- Fecha_Registro DATETIME
                -- );
                INSERT INTO master.[dbo].[Sistema_Logs_API] -- Modificado para usar master.dbo
                (Cliente_IP, Operacion, Servidor_Destino, Estado, Detalle_Error, Fecha_Hora, Fecha_Registro)
                VALUES (?,?,?,?,?, GETDATE(), GETDATE())
            """
            params_audit = (ip, operation, server_destination, status, error_msg)
            cursor_audit.execute(query_audit, params_audit)
            conn_audit.commit()
            print(f"✅ AUDITORÍA EXITOSA: Registro insertado en SQL Docker Local.")
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN AUDITORÍA (NO PUDO LOGGEAR):")
        print(f"Causa: {str(e)}")
        # Para evitar exponer contraseñas en logs de prod, solo en debug.
        # print(f"Contexto: User={user_audit} | Server=127.0.0.1,15000") 
        # print(f"Conexión usada: {conn_str_audit}")

# --- ENDPOINTS ---

@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_query(payload: Dict[str, Any], request: Request):
    client_ip = request.client.host
    server_from_payload = payload.get("server") # Nombre del servidor recibido en el payload
    database = payload.get("database")
    operation = payload.get("operation")
    query_text = payload.get("procedure")
    params = payload.get("parameters", {})

    # Variables para construir la cadena de conexión
    server_address_for_conn = server_from_payload # Usado en la propiedad SERVER= de la conexión
    server_name_for_creds = server_from_payload # Usado para get_db_credentials

    # Lógica para manejar el SQL Server en Docker, asumiendo que la API corre fuera de Docker.
    # Si la API se ejecutara DENTRO del mismo Docker Compose, la resolución sería diferente (usando el nombre del servicio 'sqlserver').
    if server_from_payload in ["SQL2025_DOCKER", "127.0.0.1", "localhost"]:
        server_address_for_conn = "127.0.0.1,15000" # Mapea al puerto externo del Docker
        # Para obtener las credenciales, usaremos el nombre que tengamos en el.env para este servidor
        # Por ejemplo, si usas "127.0.0.1" en el payload, busca DB_SERVER_127_0_0_1_USER/PASS
        # Si usas "SQL2025_DOCKER" en el payload, busca DB_SERVER_SQL2025_DOCKER_USER/PASS
        # Ya ambos deberían apuntar a las credenciales del SA.

    try:
        user, password = get_db_credentials(server_name_for_creds) # Obtiene credenciales

        # Connection String optimizada con protección de password y TrustCertificate
        conn_str = (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};' # Actualizado a Driver 18
            f'SERVER={server_address_for_conn};'
            f'DATABASE={database};'
            f'UID={user};PWD={{{password}}};'
            f'TrustServerCertificate=yes;'
            f'Connection Timeout=15;'
        )
        
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            
            if operation == "Procedimiento":
                # Si el procedimiento no tiene parámetros, `placeholders` será vacío
                if params:
                    placeholders = ', '.join(['?' for _ in params])
                    sql = f"{{CALL {query_text} ({placeholders})}}"
                    cursor.execute(sql, list(params.values()))
                else:
                    sql = f"{{CALL {query_text}}}"
                    cursor.execute(sql)
            else: # Asumimos "Consulta" u otra operación directa
                cursor.execute(query_text)

            # Si la consulta no devuelve filas (como un INSERT/UPDATE), evitar error de fetch
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                results = [{"message": "Operación completada exitosamente"}]

            log_to_database(client_ip, operation, server_from_payload, "success")
            return {"status": "success", "data": results}

    except Exception as e:
        error_desc = str(e)
        log_to_database(client_ip, operation, server_from_payload, "error", error_desc)
        return {
            "status": "error",
            "data": [{"error": type(e).__name__, "descripcion": error_desc}]
        }

@app.get("/health")
async def health_check():
    return {"status": "online", "message": "Bridge API UC-01 is operational"}
