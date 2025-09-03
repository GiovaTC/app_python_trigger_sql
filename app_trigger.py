import pyodbc

# ========= Configura tu conexión =========
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=GTAPIERO-POLI;"
    "DATABASE=PruebaPython;"
    "UID=sa;"
    "PWD=tapiero;"
    "TrustServerCertificate=Yes;"
) 

def upsert_usuario(nombre: str, edad: int, email: str):
    """
    Realiza un INSERT (el trigger decide si INSERT o UPDATE) .
    Devuelve la fila final desde la tabla .
    """
    with pyodbc.connect(CONN_STR, autocommit=True) as conn:
        with conn.cursor() as cur:
            # intentar el INSERT ( trigger hara el upsert real )
            cur.execute(
                "INSERT INTO dbo.Usuarios (Nombre, Edad, Email) VALUES (?, ?, ?);",
                (nombre, edad, email)
            )

            # leer el estado final del registro
            cur.execute("SELECT * FROM dbo.Usuarios WHERE Email = ?;", (email,))
            row = cur.fetchone()
            if not row:
                raise RuntimeError("no se encontro el registro despues del upsert .")

            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row))

if __name__ == "__main__":
    # ---- INSERT INICIAL ----
    fila1 = upsert_usuario("Carlos Pérez", 28, "carlos.perez@example.com.co")
    print(f"[UPSERT] -> {fila1}")

    # ---- UPDATE (mismo email) -----
    fila2 = upsert_usuario("Carlos A. Pérez", 29, "carlos.perez@example.com.co")
    print(f"[UPSERT] -> {fila2}")