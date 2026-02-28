import os
import base64
import pyodbc
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from dotenv import load_dotenv
from typing import Dict, Any

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="SQL Bridge API UC-01")

# --- CONFIGURACIÓN Y SEGURIDAD ---
API_KEY_EXPECTED = os.getenv("API_KEY", "").strip()

def get_db_credentials(server_name: str):
    """Extrae y decodifica credenciales desde el .env con limpieza estricta"""
    # Reemplazamos puntos por guiones bajos para coincidir con nombres de variables .env
    clean_name = server_name.replace(".", "_").upper()
    user = os.getenv(f"DB_SERVER_{clean_name}_USER")
    b64_pass = os.getenv(f"DB_SERVER_{clean_name}_PASS")
    
    if not user or not b64_pass:
        raise ValueError(f"Configuración no encontrada para el servidor: {server_name}")
        
    # Decodificación y limpieza de posibles espacios/saltos de línea
    password = base64.b64decode(b64_pass.strip()).decode('utf-8').strip()
    return user.strip(), password

async def verify_api_key(api_key: str = Header(None, alias="api-key")):
    """Valida la API Key enviada en el header"""
    if not api_key or api_key.strip() != API_KEY_EXPECTED:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado: API Key inválida"
        )

# --- SISTEMA DE AUDITORÍA ---

def log_to_database(ip: str, operation: str, server: str, status: str, error_msg: str = None):
    """Registra auditoría en el SQL Server local con debug activo"""
    print(f"DEBUG: Intentando registrar log para {operation}...")
    try:
        user, password = get_db_credentials("127.0.0.1")
        
        # Usamos IP y puerto explícito para evitar fallos de resolución
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER=127.0.0.1,15000;' 
            f'DATABASE=ERP_DB;'
            f'UID={user};PWD={{{password}}};'
            f'TrustServerCertificate=yes;'
            f'Connection Timeout=5;'
        )
        
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO [ERP_DB].[dbo].[Sistema_Logs_API] 
                (Cliente_IP, Operacion, Servidor_Destino, Estado, Detalle_Error, Fecha_Hora, Fecha_Registro)
                VALUES (?, ?, ?, ?, ?, GETDATE(), GETDATE())
            """
            params = (ip, operation, server, status, error_msg)
            cursor.execute(query, params)
            conn.commit()
            print(f"✅ AUDITORÍA EXITOSA: Registro insertado en SQL Local.")
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN AUDITORÍA:")
        print(f"Causa: {str(e)}")
        # Si el error es de login, imprimimos el usuario que intentamos usar
        print(f"Contexto: User={user} | Server=127.0.0.1,15000")
        

# --- ENDPOINTS ---

@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_query(payload: Dict[str, Any], request: Request):
    client_ip = request.client.host
    server = payload.get("server")
    database = payload.get("database")
    operation = payload.get("operation")
    query_text = payload.get("procedure")
    params = payload.get("parameters", {})

    # Resolución de dirección para Docker
    server_address = server
    if server == "SQL2025_DOCKER":
        server_address = f"{server},15000"

    try:
        user, password = get_db_credentials(server)
        
        # Connection String optimizada con protección de password y TrustCertificate
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server_address};'
            f'DATABASE={database};'
            f'UID={user};PWD={{{password}}};'
            f'TrustServerCertificate=yes;'
            f'Connection Timeout=15;'
        )
        
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            
            if operation == "Procedimiento":
                placeholders = ', '.join(['?' for _ in params])
                sql = f"{{CALL {query_text} ({placeholders})}}"
                cursor.execute(sql, list(params.values()))
            else:
                cursor.execute(query_text)

            # Si la consulta no devuelve filas (como un INSERT/UPDATE), evitar error de fetch
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                results = [{"message": "Operación completada exitosamente"}]

            log_to_database(client_ip, operation, server, "success")
            return {"status": "success", "data": results}

    except Exception as e:
        error_desc = str(e)
        log_to_database(client_ip, operation, server, "error", error_desc)
        return {
            "status": "error",
            "data": [{"error": type(e).__name__, "descripcion": error_desc}]
        }

@app.get("/health")
async def health_check():
    return {"status": "online", "message": "Bridge API UC-01 is operational"}