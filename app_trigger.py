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

def upsert_usuario(nombre: str, edad: int, email: str, id_existente: int | None = None):
    """
    Ejecuta dbo.usp_Usuarios_Upsert .
    - Si id_existente es None => INSERT
    - Si id_existente tiene valor => UPDATE
    Devuelve: (id_resultante, accion, fila_dict)
    """
    with pyodbc.connect(CONN_STR, autocommit=True) as conn:
        with conn.cursor() as cur:
            tsql = """
                DECLARE @outId INT = ?; -- recibimos el Id inicial
                EXEC dbo.usp_Usuarios_Upsert
                    @Id=@outId OUTPUT,
                    @Nombre=?,
                    @Edad=?,
                    @Email=?;
                -- La SP devuelve la fila afectada y el Id final
                SELECT FinalId = @outId;
            """
