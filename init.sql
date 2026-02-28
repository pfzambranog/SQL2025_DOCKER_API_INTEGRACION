    -- Habilitar la ejecución de scripts externos para la funcionalidad de EXTERNAL MODEL
    -- Esto es crucial para permitir que SQL Server llame a APIs externas.

-- Habilitar opciones avanzadas para configurar otras características

EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
GO

-- Habilitar la ejecución de scripts externos (fundamental para AI/ML, EXTERNAL MODELs)
EXEC sp_configure 'external scripts enabled', 1;
RECONFIGURE WITH OVERRIDE;
GO

-- Habilitar explícitamente los endpoints REST externos (CRUCIAL para llamadas a API externas en 2025)
EXEC sp_configure 'external rest endpoint enabled', 1;
RECONFIGURE;
GO

-- Habilitar el Agente SQL Server (para trabajos programados, etc.)
EXEC sp_configure 'Agent XPs', 1;
RECONFIGURE;
GO

-- Habilitar Database Mail (si lo necesitas para notificaciones por correo)
EXEC sp_configure 'Database Mail XPs', 1;
RECONFIGURE;
GO

-- Habilitar Replication XPs (si necesitas replicación de datos)
EXEC sp_configure 'Replication XPs', 1;
RECONFIGURE;
GO

-- Opciones de rendimiento y uso de recursos (ajustar según el hardware del contenedor)
-- 0 = SQL Server determina el grado de paralelismo
EXEC sp_configure 'max degree of parallelism', 0;
RECONFIGURE;
GO

-- Umbral de costo para considerar la ejecución paralela (valor por defecto es 5)
EXEC sp_configure 'cost threshold for parallelism', 5;
RECONFIGURE;
GO

-- Memoria mínima por consulta (ej: 1MB)
EXEC sp_configure 'min memory per query (KB)', 1024;
RECONFIGURE;
GO

-- Memoria máxima del servidor en MB (ej: 80% de la RAM del contenedor)
-- Tendrías que ajustar este valor a la RAM asignada a tu contenedor en docker-compose
-- EXEC sp_configure 'max server memory (MB)', 16384; -- Ejemplo para un contenedor con 20GB de RAM
-- RECONFIGURE;
-- GO

-- Memoria mínima del servidor en MB (ej: 20% de la RAM del contenedor)
-- EXEC sp_configure 'min server memory (MB)', 4096; -- Ejemplo para un contenedor con 20GB de RAM
-- RECONFIGURE;
-- GO

GO

-- NOTA: Si el CREATE EXTERNAL LANGUAGE Python dio error, manténlo comentado o eliminado.
--       La lógica de ML en 2025 es más sobre EXTERNAL MODELS que sobre runtimes internos de Python/R.
