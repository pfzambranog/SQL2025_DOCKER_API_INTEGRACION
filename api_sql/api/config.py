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