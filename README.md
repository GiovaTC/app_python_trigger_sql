# app_python_trigger_sql
# 🚀 Ejemplo: Upsert con Trigger + Python (SQL Server)

Ejemplo equivalente pero usando un **trigger en SQL Server** en lugar de un **Stored Procedure**.  
La idea es que el trigger se encargue de la lógica de **upsert** cuando se hace un `INSERT`.

<img width="1272" height="1079" alt="image" src="https://github.com/user-attachments/assets/86d866ca-29b0-491e-a776-bebd12a53175" />

---

## 📌 Concepto
👉 En SQL Server, un trigger se ejecuta después de una operación (`AFTER INSERT`, `AFTER UPDATE`, etc.).  
Como los triggers no pueden decidir si hacen un `INSERT` o un `UPDATE` antes de ejecutarse, la manera más práctica es:

- Siempre haces un `INSERT` desde Python.  
- Si ya existe el **Email**, el trigger convierte ese `INSERT` en un `UPDATE`.

---

## 📂 Proyecto: Upsert con Trigger + Python

### 1️⃣ SQL Server: esquema + trigger  

Guarda como **`schema_trigger.sql`** y ejecútalo en tu instancia:

```sql
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

📖 Explicación:
INSTEAD OF INSERT intercepta el INSERT.

Si el Email ya existe → convierte en UPDATE.

Si no existe → hace el INSERT.

2️⃣ Python: app sin Stored Procedure
Guarda como app_trigger.py:

python

import pyodbc

# ========= Configura tu conexión =========
CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost,1433;"          # Cambia host/puerto si aplica
    "DATABASE=PruebaPython;"
    "Trusted_Connection=Yes;"         # O usa UID=sa;PWD=TuPassword;
    "TrustServerCertificate=Yes;"
)

def upsert_usuario(nombre: str, edad: int, email: str):
    """
    Realiza un INSERT (el trigger decide si INSERT o UPDATE).
    Devuelve la fila final desde la tabla.
    """
    with pyodbc.connect(CONN_STR, autocommit=True) as conn:
        with conn.cursor() as cur:
            # Intentar el INSERT (trigger hará el upsert real)
            cur.execute(
                "INSERT INTO dbo.Usuarios (Nombre, Edad, Email) VALUES (?, ?, ?);",
                (nombre, edad, email)
            )

            # Leer el estado final del registro
            cur.execute("SELECT * FROM dbo.Usuarios WHERE Email = ?;", (email,))
            row = cur.fetchone()
            if not row:
                raise RuntimeError("No se encontró el registro después del upsert.")

            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row))

if __name__ == "__main__":
    # ---- INSERT inicial ----
    fila1 = upsert_usuario("Carlos Pérez", 28, "carlos.perez@example.com")
    print(f"[UPSERT] -> {fila1}")

    # ---- UPDATE (mismo Email) ----
    fila2 = upsert_usuario("Carlos A. Pérez", 29, "carlos.perez@example.com")
    print(f"[UPSERT] -> {fila2}")

3️⃣ Ejecución
Ejecuta el script de SQL:

sql

:r schema_trigger.sql
Corre la app Python:

bash

python app_trigger.py
Resultado esperado en consola:

csharp

[UPSERT] -> {'Id': 1, 'Nombre': 'Carlos Pérez', 'Edad': 28, 'Email': 'carlos.perez@example.com'}
[UPSERT] -> {'Id': 1, 'Nombre': 'Carlos A. Pérez', 'Edad': 29, 'Email': 'carlos.perez@example.com'}
Verificación en SQL Server:

sql
    
SELECT * FROM dbo.Usuarios;
