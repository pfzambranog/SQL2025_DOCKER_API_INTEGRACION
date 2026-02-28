# Usa la imagen oficial de Docker de SQL Server en Linux
FROM mcr.microsoft.com/mssql/server:2025-latest

# Configuración de SQL Server mediante variables de entorno
# Estas variables son LEÍDAS por el script de entrada de la imagen oficial
ENV ACCEPT_EULA=Y
# Usa la contraseña de tu docker-compose.yml
ENV SA_PASSWORD="Yape2025!"
# Edición de SQL Server (Developer, Express, Standard, Enterprise)
ENV MSSQL_PID="Developer"
# Puedes añadir otras variables de entorno de SQL Server aquí, si las necesitas.

# NOTA: No es necesario instalar ML Services o Python/R con mssql-conf en el Dockerfile
# para la funcionalidad de llamadas a API externas (EXTERNAL MODEL) en SQL Server 2025.
# La habilitación se hará via T-SQL en init.sql.

# Si tu aplicación Python necesita conectar a SQL Server desde *fuera* del motor,
# y quieres que este contenedor sirva para eso, puedes instalar pyodbc aquí.
# Esto NO es para que SQL Server ejecute Python internamente.
# RUN apt-get update && apt-get install -y python3 python3-pip unixodbc-dev && rm -rf /var/lib/apt/lists/* && apt-get clean
# RUN pip install --no-cache-dir pyodbc requests pandas # Ejemplo de librerías para Python externo

# Exponer los puertos necesarios
EXPOSE 1433
EXPOSE 5000