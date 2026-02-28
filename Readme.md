--SQL2025_DOCKER_API_INTEGRACION

Luego, puedes seguir tus pasos habituales para crear la rama y hacer el commit.

# Configuración de SQL Server 2025 en Docker para Integración con API Python y Funcionalidades de IA
**ID de Proyecto / Clave de Referencia:** `SQL2025_DOCKER_API_INTEGRACION`
---
## 1. Visión General del Proyecto
Este proyecto establece una integración bidireccional entre una instancia de SQL Server 2017 On-Premise y un SQL Server 2025 desplegado en Docker. La comunicación se canaliza a través de una API Python centralizada que actúa como mediador, permitiendo que SQL Server 2017 envíe y reciba datos JSON. La API Python procesa estos datos y los utiliza para interactuar con el SQL Server 2025 en Docker para operaciones CRUD y ejecución de procedimientos almacenados.
El SQL Server 2025 en Docker está configurado para soportar las nuevas capacidades de Inteligencia Artificial (IA), incluyendo la invocación de `EXTERNAL MODEL` y llamadas a APIs externas directamente desde T-SQL.
**Flujo de Integración (Según Diagrama):**
1.  **SQL Server 2017 On-Premise:** Un `SQL Agent Job` o `PowerShell Script` genera un `JSON Request` y lo envía a la API Python.
2.  **API Python (en la Nube/Contenedor):**
    *   Recibe y realiza "Validación y Parsing JSON".
    *   Establece "Conexión a SQL Server 2025".
    *   "Ejecuta CRUD / SP" en SQL Server 2025.
    *   Genera un `JSON Response` o `Archivo JSON`.
3.  **SQL Server 2025 en Docker:** Recibe "Consulta / SP" de la API Python para ejecutar "Procedimientos Almacenados" y "Operaciones CRUD".
4.  **Respuesta Bidireccional:** La API Python retorna un `JSON Result` al SQL Server 2017 On-Premise.
---
## 2. Archivos Clave del Proyecto
Este repositorio contiene los siguientes archivos esenciales para desplegar y configurar el entorno:
*   `Dockerfile`: Define la imagen personalizada de SQL Server 2025.
*   `docker-compose.yml`: Orquesta el despliegue del contenedor de SQL Server.
*   `init.sql`: Contiene los comandos T-SQL para la configuración inicial de la instancia de SQL Server 2025.
### 2.1. `Dockerfile`
Este `Dockerfile` construye la imagen personalizada de SQL Server 2025. Utiliza la imagen oficial de Microsoft, que está optimizada para Docker, y configura las variables de entorno necesarias para la configuración inicial.
37 líneas en total (23 líneas de código) · 2.2 KB
Utiliza la imagen oficial de Docker de SQL Server en Linux
FROM mcr.microsoft.com/mssql/server:2025-latest

Configuración de SQL Server mediante variables de entorno
Estas variables son LEÍDAS por el script de entrada de la imagen oficial de MSSQL Server.
ENV ACCEPT_EULA=Y

¡Usa una contraseña segura y sin caracteres especiales al final, como '!' para evitar problemas de parsing!
ENV SA_PASSWORD="Yape2025!"

Define la edición de SQL Server (Developer, Express, Standard, Enterprise).
ENV MSSQL_PID="Developer"

Puedes añadir otras variables de entorno de SQL Server aquí si las necesitas.
NOTA IMPORTANTE sobre Machine Learning Services (ML Services) en SQL Server 2025:
La forma de integrar capacidades de IA en SQL Server 2025 ha evolucionado significativamente.
Los comandos de instalación de ML Services tradicionales como 'mssql-conf install python-3.9' o 'install-setup-tools'
(utilizados en versiones anteriores de SQL Server) ya NO son válidos ni necesarios para las nuevas
capacidades de IA de SQL Server 2025.
SQL Server 2025 se centra en el nuevo tipo de datos 'VECTOR' y la invocación de 'EXTERNAL MODEL'
o servicios REST externos directamente desde T-SQL.
La habilitación de esta funcionalidad se realiza mediante comandos T-SQL en el 'init.sql', no en el Dockerfile.
Si tu aplicación Python (la API Python en tu diagrama, u otra aplicación cliente)
necesita conectar a SQL Server desde fuera del motor de la base de datos (por ejemplo, para leer/escribir datos),
y quisieras instalar librerías como pyodbc dentro de ESTE contenedor de SQL Server
(aunque generalmente es mejor tener las aplicaciones cliente en contenedores separados),
podrías descomentar y usar las siguientes líneas.
Sin embargo, para la funcionalidad de 'EXTERNAL MODEL' y llamadas a APIs desde T-SQL, no se requieren aquí.
RUN apt-get update && apt-get install -y python3 python3-pip unixodbc-dev && rm -rf /var/lib/apt/lists/* && apt-get clean
RUN pip install --no-cache-dir pyodbc requests pandas # Ejemplo de librerías para Python externo
Exponer los puertos necesarios.
1433 es el puerto interno estándar de SQL Server.
EXPOSE 1433

El puerto 5000 no es estrictamente necesario para la funcionalidad de 'EXTERNAL MODEL' en 2025,
pero se mantiene por compatibilidad si se usaran patrones de extensibilidad antiguos
o si se planeara exponer un endpoint personalizado desde el propio contenedor de SQL Server.
EXPOSE 5000

### 2.2. `docker-compose.yml`
Este archivo define y orquesta el servicio de SQL Server, gestiona su construcción, variables de entorno, volúmenes de datos persistentes y la exposición de puertos para acceso externo.
5 líneas en total (2 líneas de código) · 221 B
version: "3.9"

services: sqlserver: build:. # Indica que la imagen de SQL Server se construirá usando el Dockerfile en este directorio. container_name: SQL-Docker # Nombre descriptivo para el contenedor.

environment:
  ACCEPT_EULA: "Y" # Acepta el Acuerdo de Licencia de Usuario Final de SQL Server.
  SA_PASSWORD: "Yape2025!" # ¡Contraseña para el usuario 'sa'! Asegúrate de que sea segura.
  MSSQL_PID: "Developer" # Define la edición de SQL Server a instalar (Developer, Express, Standard, Enterprise).
  MSSQL_COLLATION: "SQL_Latin1_General_CP1_CI_AI" # Establece la colación de la instancia de SQL Server.
  TZ: "America/Monterrey" # Define la zona horaria del contenedor.
volumes:
  # Volúmenes para persistir datos de SQL Server, logs y secretos.
  # ¡IMPORTANTE!: Asegúrate de que las rutas locales (ej. C:\BaseDatos\...) existan en tu sistema
  # o cámbialas para que apunten a ubicaciones válidas en tu entorno.
  - C:\BaseDatos\Docker\SQL-Docker-2025\data:/var/opt/mssql/data
  - C:\BaseDatos\Docker\SQL-Docker-2025\log:/var/opt/mssql/log
  - C:\BaseDatos\Docker\SQL-Docker-2025\secrets:/var/opt/mssql/secrets
  # Monta el script 'init.sql'. Este script se ejecutará automáticamente
  # en la primera inicialización del contenedor de SQL Server, aplicando configuraciones iniciales.
  - C:\BaseDatos\Docker\SQL-Docker-2025\init.sql:/docker-entrypoint-initdb.d/init.sql
  
ports:
  # Mapea el puerto 1433 del contenedor (donde SQL Server escucha) al puerto 15000 de tu máquina host.
  # Esto permite que aplicaciones externas (como tu API Python o herramientas de administración)
  # se conecten a SQL Server a través de `localhost:15000`.
  - "15000:1433"
restart: unless-stopped # Política de reinicio: el contenedor siempre se reiniciará a menos que se detenga explícitamente.
networks:
  - app_net # Conecta el contenedor a una red Docker definida llamada 'app_net'.
  # Esto facilita la comunicación con otros servicios en la misma red por nombre de servicio.
healthcheck:
  # Define una verificación de estado para monitorear la disponibilidad de SQL Server.
  test: ["CMD-SHELL", "pidof sqlservr"] # Comando para verificar si el proceso de SQL Server está corriendo.
  interval: 10s # Frecuencia de las verificaciones.
  timeout: 5s # Tiempo máximo de espera para que una verificación se complete.
  retries: 10 # Número de intentos fallidos antes de declarar el contenedor como "unhealthy".
networks: app_net: name: app_net # Nombre personalizado para la red Docker. driver: bridge # Tipo de red predeterminado, permite la comunicación entre contenedores.

### 2.3. `init.sql`
Este script T-SQL se ejecuta la primera vez que el contenedor de SQL Server se inicializa. Contiene configuraciones críticas que habilitan las funcionalidades de extensibilidad, el Agente SQL Server y otras características importantes para tu proyecto.
5 líneas en total (2 líneas de código) · 277 B
-- Este script se ejecuta automáticamente en la primera inicialización del contenedor de SQL Server.

-- Habilitar opciones avanzadas: Permite configurar opciones de servidor más detalladas. EXEC sp_configure 'show advanced options', 1; RECONFIGURE; GO

-- Habilitar la ejecución de scripts externos: Es fundamental para: -- 1. Permitir la integración de Machine Learning y AI en el motor de SQL Server. -- 2. Utilizar las nuevas capacidades de 'EXTERNAL MODEL' de SQL Server 2025. EXEC sp_configure 'external scripts enabled', 1; RECONFIGURE WITH OVERRIDE; -- 'WITH OVERRIDE' es recomendado para forzar la configuración si hay dependencias. GO

-- Habilitar explícitamente los endpoints REST externos: CRUCIAL para SQL Server 2025 -- si planeas que la base de datos se conecte a APIs REST externas. EXEC sp_configure 'external rest endpoint enabled', 1; RECONFIGURE; GO

-- Habilitar el Agente SQL Server: Esencial para trabajos programados, -- automatización de tareas, mantenimiento, y el motor de eventos de SQL Server. EXEC sp_configure 'Agent XPs', 1; RECONFIGURE; GO

-- Habilitar Database Mail XPs: Permite a SQL Server enviar correos electrónicos -- para notificaciones, alertas, informes, etc. Requiere configuración adicional. EXEC sp_configure 'Database Mail XPs', 1; RECONFIGURE; GO

-- Habilitar Replication XPs: Necesario si planeas configurar y utilizar -- la replicación de datos de SQL Server. EXEC sp_configure 'Replication XPs', 1; RECONFIGURE; GO

-- Opciones de rendimiento y uso de recursos: Estos valores predeterminados son generales; -- ajústalos según los requisitos específicos de tu carga de trabajo y los recursos asignados al contenedor.

-- 'max degree of parallelism' (MAXDOP): Controla el número máximo de procesadores utilizados -- para la ejecución paralela de una única consulta. -- 0: Permite a SQL Server determinar el grado óptimo de paralelismo automáticamente. EXEC sp_configure 'max degree of parallelism', 0; RECONFIGURE; GO

-- 'cost threshold for parallelism': Umbral de costo (en segundos) a partir del cual el optimizador -- de consultas considerará una consulta para ejecución paralela. El valor por defecto es 5. EXEC sp_configure 'cost threshold for parallelism', 5; RECONFIGURE; GO

-- 'min memory per query (KB)': Memoria mínima (en kilobytes) que SQL Server garantiza para una consulta. EXEC sp_configure 'min memory per query (KB)', 1024; -- Equivalente a 1 MB. RECONFIGURE; GO

-- 'max server memory (MB)' y 'min server memory (MB)': -- Estas opciones controlan el uso de memoria de SQL Server. En entornos Docker, -- el límite general de memoria del contenedor gestiona esto. Sin embargo, si deseas -- establecer límites explícitos para la instancia de SQL Server dentro del contenedor, -- puedes descomentar y ajustar estas líneas. Asegúrate de que los valores sean coherentes -- con los recursos de RAM asignados a tu contenedor en el docker-compose.yml. -- Ejemplo para un contenedor con 20GB de RAM: -- EXEC sp_configure 'max server memory (MB)', 16384; -- 16 GB -- RECONFIGURE; -- GO -- EXEC sp_configure 'min server memory (MB)', 4096; -- 4 GB -- RECONFIGURE; -- GO

-- NOTA IMPORTANTE: 'xp_cmdshell' ha sido eliminado en SQL Server 2025 y no está disponible -- para configuración o uso. Por lo tanto, no se incluye ni se configura aquí.

-- NOTA: Si en versiones anteriores se utilizaba 'CREATE EXTERNAL LANGUAGE Python' -- para la ejecución de Python in-database (ML Services tradicionales), en SQL Server 2025 -- el enfoque para la IA ha evolucionado hacia 'EXTERNAL MODEL' y la invocación de servicios externos. -- Por lo tanto, este comando no se incluye ni es necesario para las capacidades de IA de 2025.

### 3. Pasos para Configurar y Desplegar
Sigue estos pasos para construir y ejecutar tu contenedor de SQL Server 2025:
1. **Crea los Archivos**: Asegúrate de tener los tres archivos (`Dockerfile`, `docker-compose.yml`, `init.sql`) en el mismo directorio base de tu proyecto (ej. `C:\BaseDatos\Docker\SQL-Docker-2025`).
2. **Verifica Rutas de Volúmenes**: Confirma que los directorios locales para los volúmenes (`data`, `log`, `secrets`) existan en tu sistema (por ejemplo, `C:\BaseDatos\Docker\SQL-Docker-2025\data`) o ajústalos en el `docker-compose.yml` para que apunten a ubicaciones válidas en tu entorno.
3. **Abre la Terminal**: Navega a tu directorio raíz del proyecto (donde se encuentran los archivos) en tu terminal (ej. PowerShell en Windows).
8 líneas en total (5 líneas de código) · 764 B
cd C:\BaseDatos\Docker\SQL-Docker-2025

4.  **Limpia el Caché de Docker (O
1 líneas en total (1 líneas de código) · 170 B
docker builder prune -a

    Confirma con `y` cuando te lo solicite.
5. **Construye y Levanta el Servicio**: Ejecuta Docker Compose para construir la imagen y levantar el contenedor en segundo plano:
2 líneas en total (2 líneas de código) · 174 B
docker-compose up --build -d

6.  **Verifica el Estado del Contenedor**: Confirma que el contenedor está corriendo y en estado `healthy` (suele tardar unos segundos en cambiar a `healthy`).
1 líneas en total (1 líneas de código) · 159 B
docker ps -a

    Deberías ver tu contenedor `SQL-Docker` con un `STATUS` similar a `Up X seconds (healthy)`.
### 4. Verificación y Conexión a SQL Server
Una vez que el contenedor esté en funcionamiento y muestre estado `healthy`:
1. **Conéctate a la Instancia**:
    * Utiliza tu herramienta de cliente preferida para SQL Server (SQL Server Management Studio (SSMS), Azure Data Studio, sqlcmd).
    * **Dirección del servidor**: `localhost,15000` (o `127.0.0.1,15000`)
    * **Tipo de autenticación**: `SQL Server Authentication`
    * **Login**: `sa`
    * **Contraseña**: `Yape2025!` (La que definiste en tu `docker-compose.yml`)
2. **Confirma las Configuraciones de `init.sql`**: Una vez conectado, ejecuta las siguientes consultas para verificar que las opciones de extensibilidad y otras configuraciones estén habilitadas:
13 líneas en total (10 líneas de código) · 826 B
EXEC sp_configure 'external scripts enabled'; GO EXEC sp_configure 'external rest endpoint enabled'; GO EXEC sp_configure 'Agent XPs'; GO EXEC sp_configure 'Database Mail XPs'; GO EXEC sp_configure 'Replication XPs'; GO EXEC sp_configure 'max degree of parallelism'; GO EXEC sp_configure 'cost threshold for parallelism'; GO EXEC sp_configure 'min memory per query (KB)'; GO

    Para cada una, los valores `run_value` y `config_value` deberían ser `1` (o el valor que estableciste para las opciones de rendimiento).
### 5. Implementación de Integración de IA y Llamadas a APIs Externas
Con tu SQL Server 2025 en Docker completamente configurado y listo, ahora puedes proceder a implementar la lógica de integración de IA y llamadas a APIs externas:
* **`EXTERNAL MODEL`**: Utiliza esta característica para registrar modelos de IA o servicios REST (APIs) externos directamente en SQL Server. Una vez registrados, puedes invocarlos desde T-SQL para procesar datos de tu base de datos o enriquecer tus consultas con inferencias de IA. Este es el camino principal para la integración de IA en SQL Server 2025.
* **Llamadas Directas a APIs desde T-SQL**: La habilitación de `external scripts enabled` y `external rest endpoint enabled` permite que SQL Server realice solicitudes HTTP/S a APIs externas directamente desde T-SQL, ya sea a través de `EXTERNAL MODEL` o mediante UDFs que encapsulen estas llamadas.
**Ejemplo Conceptual de Uso (la sintaxis precisa puede variar ligeramente según la versión final de SQL Server 2025 y el tipo de API):**
11 líneas en total (6 líneas de código) · 1.2 KB
-- Ejemplo (conceptual) de cómo se podría registrar y usar un EXTERNAL MODEL -- para interactuar con una API REST externa en SQL Server 2025. -- La implementación final dependerá de la estructura de tu API y la documentación específica de 2025.

-- 1. Crear una credencial a nivel de base de datos si la API requiere autenticación (ej. una clave API o token). -- Esto almacena de forma segura las credenciales de tu API. CREATE DATABASE SCOPED CREDENTIAL WITH IDENTITY = 'API_Service_User', -- Nombre de usuario interno para la credencial SECRET = 'mi_clave_api_muy_secreta_123'; -- ¡Reemplaza con tu clave API real o token! GO

-- 2. Crear el EXTERNAL MODEL o EXTERNAL SCRIPT para la API. -- Este es un EJEMPLO; la sintaxis exacta de SQL Server 2025 puede ser más específica -- y flexible, y podría requerir la definición de un EXTERNAL DATA SOURCE o EXTERNAL LANGUAGE -- que encapsule el conector a la API REST.

-- El patrón más directo implica definir cómo SQL Server interactuará con el endpoint REST. /* CREATE EXTERNAL MODEL. WITH ( ENDPOINT = 'https://api.ejemplo.com/v1/clasificar_texto', -- URL de tu API externa REQUEST_METHOD = 'POST', -- Método HTTP (GET, POST, PUT, DELETE) REQUEST_HEADERS = N'{"Content-Type": "application/json", "Accept": "application/json"}', -- Headers JSON REQUEST_BODY_SCHEMA = N'{"type": "object", "properties": {"text_input": {"type": "string"}}}', -- Esquema del JSON que se envía RESPONSE_SCHEMA = N'{"type": "object", "properties": {"category": {"type": "string"}, "score": {"type": "number"}}}', -- Esquema del JSON que se espera recibir CREDENTIAL = -- Opcional, si creaste la credencial ); GO

-- 3. Invocar el EXTERNAL MODEL desde T-SQL para enviar datos a la API y recibir resultados. -- Esto permite pasar datos de tus tablas de SQL Server a la API externa para procesamiento -- y recibir los resultados de vuelta directamente en una consulta T-SQL. SELECT T.ID_Registro, T.TextoOriginal, ClasificacionAPI.category, ClasificacionAPI.score FROM TuTablaDeTextos AS T CROSS APPLY PREDICT (MODEL =., DATA = (SELECT T.TextoOriginal AS text_input)); GO */

---
### 6. Lecciones Aprendidas (Desafíos y Soluciones durante la Configuración)
Durante el proceso de configuración de SQL Server 2025 en Docker, enfrentamos y superamos varios desafíos comunes, que ofrecen importantes lecciones para futuros despliegues:
* **Problemas de Permisos en Imagen Base de MSSQL (`mcr.microsoft.com/mssql/server`)**:
    * **Desafío**: Las imágenes base de MSSQL, aunque oficiales, pueden ser muy restrictivas en cuanto a permisos de usuario y acceso a directorios del sistema de archivos (`/var/lib/apt/lists`). Esto causaba errores al intentar ejecutar `apt-get install` o `mkdir` en ciertos contextos.
    * **Solución**: Se optó por una estrategia de construcción desde una imagen limpia de `ubuntu:22.04` para tener control total sobre la instalación de dependencias y la gestión de permisos, aunque finalmente se volvió a la imagen oficial una vez que se entendió el enfoque correcto para ML/AI en 2025.
* **Gestión de Repositorios `apt` en Dockerfiles**:
    * **Desafío**: Errores como `lsb_release: not found` o `E: Type '404:' is not known` al intentar añadir repositorios de Microsoft.
    * **Solución**: Asegurarse de instalar `lsb-release` previamente y utilizar el método más moderno y robusto de Microsoft (usando `curl` para la clave GPG y `echo` para el archivo `.list` en `/etc/apt/sources.list.d/`) para añadir el repositorio de SQL Server en Ubuntu 22.04.
* **Errores de Sintaxis en `Dockerfile`**:
    * **Desafío**: Docker tiene reglas estrictas para la sintaxis. Comentarios (`#`) o líneas en blanco inesperadas dentro de una instrucción `RUN` (especialmente si usa `\`) o en la misma línea que declaraciones `ENV` pueden causar fallos de `Syntax error`.
    * **Solución**: Mantener los comentarios en líneas separadas y asegurar que todas las líneas continuadas de un `RUN` terminen con `\` y no tengan interrupciones.
* **Configuración de `mssql-conf` en un Contenedor Docker**:
    * **Desafío**: La herramienta `mssql-conf` no siempre se comporta igual en un `Dockerfile RUN` que en una instalación interactiva. Errores como `unrecognized arguments: --edition` o `unrecognized arguments: --skip-systemd-start` indicaban que el `setup` se esperaba de otra forma. Además, `systemctl` no está disponible en la fase de construcción de Docker.
    * **Solución**: Se entendió que `mssql-conf setup` debe ejecutarse sin argumentos en la fase de construcción (confiando en las `ENV` variables para la configuración básica) y que la bandera `--skip-systemd-start` no es universalmente reconocida por todas las versiones de `mssql-conf`.
* **Evolución de los Machine Learning Services (ML Services) en SQL Server 2025**:
    * **Desafío**: El método tradicional para instalar Python/R in-database (`mssql-conf install python-3.9`) ya no es válido en SQL Server 2025.
    * **Solución**: Comprender que SQL Server 2025 ha evolucionado hacia un modelo de "AI nativa" con el tipo `VECTOR` y la invocación de `EXTERNAL MODEL` y APIs externas directamente desde T-SQL. Esto elimina la necesidad de instalar runtimes de Python/R de forma tradicional *dentro del motor de SQL Server* para las nuevas funcionalidades de IA.
* **`init.sql` como Herramienta Fundamental de Configuración**:
    * **Desafío**: Alinear las configuraciones post-instalación de SQL Server con el ciclo de vida del contenedor Docker.
    * **Solución**: Utilizar el script `init.sql` (montado en `/docker-entrypoint-initdb.d/`) para habilitar características clave como `external scripts enabled`, `external rest endpoint enabled`, `Agent XPs`, y otras configuraciones de forma automática en la primera inicialización del contenedor.
* **Disponibilidad de `xp_cmdshell` en SQL Server 2025**:
    * **Detección**: Se confirmó que `xp_cmdshell` ha sido eliminado en SQL Server 2025.
    * **Acción**: Eliminar cualquier intento de configurarlo del `init.sql`, ya que no tendrá efecto y podría generar errores.
---
