"""
Migración: Agregar campos de aprobación de corredor a tabla usuarios
Columnas: comision_porcentaje, fecha_vigencia_corredor, aprobado_por, aprobado_at, motivo_rechazo
Usa psycopg2 directo (compatible con Python 3.13)
"""
import psycopg2

DB_URL = "postgresql://postgres:esbHQXHuToTttMYUpnRCkYAdHMpXapuM@maglev.proxy.rlwy.net:44913/railway"


def ejecutar_migracion():
    """Agrega campos de aprobación de corredor a la tabla usuarios"""

    columnas = [
        {
            "nombre": "comision_porcentaje",
            "sql": "ALTER TABLE usuarios ADD COLUMN comision_porcentaje DECIMAL(5,2)",
            "comentario": "Porcentaje de comisión que Qadrante recibe al cierre de oportunidad"
        },
        {
            "nombre": "fecha_vigencia_corredor",
            "sql": "ALTER TABLE usuarios ADD COLUMN fecha_vigencia_corredor TIMESTAMP",
            "comentario": "Fecha hasta la cual el corredor está autorizado para operar"
        },
        {
            "nombre": "aprobado_por",
            "sql": "ALTER TABLE usuarios ADD COLUMN aprobado_por INTEGER REFERENCES usuarios(usuario_id)",
            "comentario": "ID del admin que aprobó al corredor"
        },
        {
            "nombre": "aprobado_at",
            "sql": "ALTER TABLE usuarios ADD COLUMN aprobado_at TIMESTAMP",
            "comentario": "Fecha y hora en que fue aprobado el corredor"
        },
        {
            "nombre": "motivo_rechazo",
            "sql": "ALTER TABLE usuarios ADD COLUMN motivo_rechazo TEXT",
            "comentario": "Motivo de rechazo si el corredor no fue aprobado"
        }
    ]

    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        for col in columnas:
            # Verificar si la columna ya existe
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'usuarios' AND column_name = %s",
                (col["nombre"],)
            )

            if cur.fetchone():
                print(f"   columna '{col['nombre']}' ya existe, saltando...")
                continue

            cur.execute(col["sql"])
            cur.execute(f"COMMENT ON COLUMN usuarios.{col['nombre']} IS %s", (col["comentario"],))
            print(f"   columna '{col['nombre']}' agregada")

        conn.commit()
        print("\n   Commit exitoso.")

        # Verificar resultado
        cur.execute(
            "SELECT column_name, data_type "
            "FROM information_schema.columns "
            "WHERE table_name = 'usuarios' "
            "AND column_name IN ('comision_porcentaje', 'fecha_vigencia_corredor', "
            "'aprobado_por', 'aprobado_at', 'motivo_rechazo', 'autorizado') "
            "ORDER BY ordinal_position"
        )

        print("\nColumnas de aprobación en tabla usuarios:")
        for row in cur.fetchall():
            print(f"   {row[0]}: {row[1]}")

    except Exception as e:
        conn.rollback()
        print(f"\n   Error, rollback ejecutado: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("Ejecutando migración: campos de aprobación de corredor...\n")
    ejecutar_migracion()
    print("\nMigración completada.")
