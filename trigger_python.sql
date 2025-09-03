-- 1. (Opcional) Crear BD
IF DB_ID('PruebaPython') IS NULL
BEGIN
    CREATE DATABASE PruebaPython;
END
GO

USE PruebaPython;
GO

-- 2. Tabla de ejemplo
IF OBJECT_ID('dbo.Usuarios', 'U') IS NOT NULL
    DROP TABLE dbo.Usuarios;
GO

CREATE TABLE dbo.Usuarios (
    Id     INT IDENTITY(1,1) PRIMARY KEY,
    Nombre NVARCHAR(100) NOT NULL,
    Edad   INT           NOT NULL,
    Email  NVARCHAR(150) NOT NULL UNIQUE
);
GO

-- 3. Trigger de UPSERT basado en Email
IF OBJECT_ID('dbo.tr_Usuarios_Upsert', 'TR') IS NOT NULL
    DROP TRIGGER dbo.tr_Usuarios_Upsert;
GO

CREATE TRIGGER dbo.tr_Usuarios_Upsert
ON dbo.Usuarios
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Si Email ya existe => UPDATE
    UPDATE U
    SET U.Nombre = I.Nombre,
        U.Edad   = I.Edad
    FROM dbo.Usuarios U
    INNER JOIN inserted I ON U.Email = I.Email;

    -- Si Email NO existe => INSERT
    INSERT INTO dbo.Usuarios (Nombre, Edad, Email)
    SELECT I.Nombre, I.Edad, I.Email
    FROM inserted I
    WHERE NOT EXISTS (
        SELECT 1 FROM dbo.Usuarios U WHERE U.Email = I.Email
    );
END
GO

-- Lista el trigger en la BD
SELECT 
    t.name        AS TriggerName,
    t.object_id   AS TriggerId,
    s.name        AS SchemaName,
    o.name        AS TableName,
    t.create_date AS CreatedOn,
    t.modify_date AS LastModified,
    m.definition  AS TriggerDefinition
FROM sys.triggers t
INNER JOIN sys.objects o ON t.parent_id = o.object_id
INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
INNER JOIN sys.sql_modules m ON t.object_id = m.object_id
ORDER BY s.name, o.name, t.name;

-- C:\Users\USUARIO\source_python\sql_trigger_python
:r C:\Users\USUARIO\source_python\sql_trigger\trigger_python.sql