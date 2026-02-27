"""
MIGRACION: categoria_override_id + Restaurar edificio + Configurar oficina
=========================================================================
1. Agrega columna categoria_override_id a caracteristicas_x_inmueble_mae
2. Reactivar categorias originales del edificio
3. Agregar asignaciones faltantes a oficina (tipo 1) para 4 grupos
4. Agregar asignaciones faltantes a edificio (tipo 12) para equipamiento/vista
5. Configurar overrides del edificio para 9 grupos originales
6. Mover montacarga (19) global a cat 4 para que oficina lo vea en Soporte

Run: set PYTHONIOENCODING=utf-8 && python scripts/migration_categoria_override.py
"""
import psycopg2

DB_URL = "postgresql://postgres:esbHQXHuToTttMYUpnRCkYAdHMpXapuM@maglev.proxy.rlwy.net:44913/railway"


def ejecutar():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    try:
        print("=" * 70)
        print("MIGRACION: categoria_override_id + Restaurar edificio")
        print("=" * 70)

        # ==========================================================
        # PASO 1: Agregar columna categoria_override_id
        # ==========================================================
        print("\n--- PASO 1: ALTER TABLE ---")
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'caracteristicas_x_inmueble_mae'
            AND column_name = 'categoria_override_id'
        """)
        if cur.fetchone():
            print("  Columna ya existe, saltando...")
        else:
            cur.execute("""
                ALTER TABLE caracteristicas_x_inmueble_mae
                ADD COLUMN categoria_override_id INTEGER
                REFERENCES categorias_mae(categoria_id)
            """)
            print("  Columna categoria_override_id agregada")

        # ==========================================================
        # PASO 2: Reactivar categorias del edificio
        # ==========================================================
        print("\n--- PASO 2: Reactivar categorias del edificio ---")
        cats_reactivar = {
            1:  ('Areas Comunes del Edificio', 3),
            2:  ('Ascensores', 4),
            6:  ('Vista de la Oficina', 7),
            19: ('Equipamiento de Oficina', 6),
            21: ('Informacion de Areas', 8),
            22: ('Valorizacion Edificio', 9),
        }
        for cat_id, (nombre, orden) in cats_reactivar.items():
            cur.execute("""
                UPDATE categorias_mae
                SET activo = true, orden = %s, updated_at = NOW()
                WHERE categoria_id = %s
            """, (orden, cat_id))
            print(f"  Reactivada cat {cat_id}: '{nombre}' (orden={orden})")

        # Actualizar orden de categorias activas existentes
        cur.execute("UPDATE categorias_mae SET orden = 1 WHERE categoria_id = 17")  # Generales/Estructura
        cur.execute("UPDATE categorias_mae SET orden = 2 WHERE categoria_id = 4")   # Soporte del Edificio
        cur.execute("UPDATE categorias_mae SET orden = 5 WHERE categoria_id = 18")  # De la Oficina
        cur.execute("UPDATE categorias_mae SET orden = 10 WHERE categoria_id = 5")  # Soporte Urbano
        print("  Ordenes de categorias actualizados")

        # ==========================================================
        # PASO 3: Mover Montacarga (19) de cat 17 a cat 4 (global)
        # Para que oficina lo vea en "Soporte del Edificio"
        # ==========================================================
        print("\n--- PASO 3: Mover montacarga global a cat 4 ---")
        cur.execute("""
            UPDATE caracteristicas_mae SET categoria_id = 4, updated_at = NOW()
            WHERE caracteristica_id = 19 AND categoria_id = 17
        """)
        print(f"  Montacarga (19): movido a cat 4 ({cur.rowcount} filas)")

        # ==========================================================
        # PASO 4: Agregar asignaciones faltantes a OFICINA (tipo 1)
        # Grupo "Generales del Edificio": 110, 120, 170, 119
        # Grupo "Soporte del Edificio": amenidades del edificio
        # ==========================================================
        print("\n--- PASO 4: Asignaciones para oficina (tipo 1) ---")

        # Generales del Edificio para oficina
        oficina_generales = [
            (1, 110, False, True, 1),   # Cantidad Pisos Edificio
            (1, 120, False, True, 2),   # Cantidad Oficinas por Piso
            (1, 170, False, True, 3),   # Ano de construccion
            (1, 119, False, True, 4),   # Ascensores (Cantidad Total)
        ]

        # Soporte del Edificio para oficina
        oficina_soporte = [
            (1, 38,  False, True, 10),  # Recepcion / Seguridad 24h7
            (1, 32,  False, True, 11),  # Generador / Grupo Electrogeno
            (1, 11,  False, True, 12),  # Salas de Reuniones
            (1, 171, False, True, 13),  # CCTV
            (1, 35,  False, True, 14),  # Chiller para AACC
            (1, 13,  False, True, 15),  # Comedor
            (1, 9,   False, True, 16),  # GYM
            (1, 10,  False, True, 17),  # Oficina Tramite Documentos
            (1, 18,  False, True, 18),  # Helipuerto
            (1, 7,   False, True, 19),  # Locales Comerciales
            (1, 19,  False, True, 20),  # Montacarga
            (1, 12,  False, True, 21),  # SUM
            (1, 6,   False, True, 22),  # Parqueos de visita
            (1, 4,   False, True, 23),  # Parqueos para Bicicletas
            (1, 5,   False, True, 24),  # Parqueos Vehiculos Electricos
            (1, 172, False, True, 25),  # Rociadores contra incendios
            (1, 173, False, True, 26),  # Escaleras contra incendios
        ]

        todas_oficina = oficina_generales + oficina_soporte
        insertados_oficina = 0
        for tipo_id, carac_id, req, visible, orden in todas_oficina:
            cur.execute("""
                SELECT id FROM caracteristicas_x_inmueble_mae
                WHERE tipo_inmueble_id = %s AND caracteristica_id = %s
            """, (tipo_id, carac_id))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO caracteristicas_x_inmueble_mae
                    (tipo_inmueble_id, caracteristica_id, requerido, visible_en_filtro, orden, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (tipo_id, carac_id, req, visible, orden))
                insertados_oficina += 1
                print(f"  + Oficina: carac {carac_id} (orden {orden})")
            else:
                print(f"  = Oficina: carac {carac_id} ya existe")

        print(f"  Total insertados oficina: {insertados_oficina}")

        # ==========================================================
        # PASO 5: Agregar asignaciones faltantes a EDIFICIO (tipo 12)
        # Equipamiento (122-130) y Vista (45-50) con override
        # ==========================================================
        print("\n--- PASO 5: Asignaciones para edificio (tipo 12) ---")

        edificio_faltantes = [
            # (tipo, carac, req, visible, orden, override_cat)
            # Equipamiento -> override a cat 19
            (12, 122, False, True, 70, 19),   # Falsos techos
            (12, 123, False, True, 71, 19),   # Luminarias
            (12, 124, False, True, 72, 19),   # AAC
            (12, 125, False, True, 73, 19),   # Sprinklers
            (12, 126, False, True, 74, 19),   # Fibra Optica
            (12, 127, False, True, 75, 19),   # Tabiques Mamparas
            (12, 128, False, True, 76, 19),   # Mobiliario
            (12, 129, False, True, 77, 19),   # Sillas
            (12, 130, False, True, 78, 19),   # Rollers
            # Vista -> override a cat 6
            (12, 49,  False, True, 80, 6),    # Vista frontal
            (12, 50,  False, True, 81, 6),    # Vista posterior
            (12, 48,  False, True, 82, 6),    # Vista interior
            (12, 47,  False, True, 83, 6),    # Vista frente al parque
            (12, 45,  False, True, 84, 6),    # Frente con doble altura
            (12, 46,  False, True, 85, 6),    # Doble frente (esquina)
        ]

        insertados_edificio = 0
        for tipo_id, carac_id, req, visible, orden, override_cat in edificio_faltantes:
            cur.execute("""
                SELECT id FROM caracteristicas_x_inmueble_mae
                WHERE tipo_inmueble_id = %s AND caracteristica_id = %s
            """, (tipo_id, carac_id))
            if cur.fetchone():
                cur.execute("""
                    UPDATE caracteristicas_x_inmueble_mae
                    SET categoria_override_id = %s
                    WHERE tipo_inmueble_id = %s AND caracteristica_id = %s
                """, (override_cat, tipo_id, carac_id))
                print(f"  ~ Edificio: carac {carac_id} override -> cat {override_cat}")
            else:
                cur.execute("""
                    INSERT INTO caracteristicas_x_inmueble_mae
                    (tipo_inmueble_id, caracteristica_id, requerido, visible_en_filtro, orden, categoria_override_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (tipo_id, carac_id, req, visible, orden, override_cat))
                insertados_edificio += 1
                print(f"  + Edificio: carac {carac_id} (override cat {override_cat})")

        print(f"  Total insertados edificio: {insertados_edificio}")

        # ==========================================================
        # PASO 6: Configurar overrides para edificio (tipo 12)
        # Caracteristicas que el edificio necesita en grupos diferentes
        # ==========================================================
        print("\n--- PASO 6: Overrides del edificio ---")

        overrides = {
            # Parking/Deposits: global cat 17 -> edificio cat 1 "Areas Comunes"
            1: [1, 2, 3, 14, 57],
            # Ascensores: global cat 17/4 -> edificio cat 2 "Ascensores"
            2: [20, 21],  # 19 ya movido a cat 4, override a cat 2
            # Amenidades: global cat 4 -> edificio cat 1 "Areas Comunes"
            # (En el edificio las amenidades van en Areas Comunes, no en Soporte)
            # NOTA: No override - edificio las muestra en Soporte del Edificio
            # que es donde estan globalmente. El edificio original las tenia en
            # Areas Comunes pero es mas logico dejarlas en Soporte.

            # Montacarga: global cat 4 -> edificio cat 2 "Ascensores"
            # 2: [19],  # Se agrega abajo
            # Areas: global cat 17 -> edificio cat 21 "Informacion de Areas"
            21: [140, 141, 142, 143, 144],
            # Precios: global cat 17 -> edificio cat 22 "Valorizacion Edificio"
            22: [161, 162, 163, 164, 165, 166, 167, 168],
        }

        # Montacarga override a cat 2 para edificio
        cur.execute("""
            UPDATE caracteristicas_x_inmueble_mae
            SET categoria_override_id = 2
            WHERE tipo_inmueble_id = 12 AND caracteristica_id = 19
        """)
        print(f"  Montacarga (19) -> cat 2 'Ascensores' para edificio")

        # Ascensores acceso (20, 21) override a cat 2
        cur.execute("""
            UPDATE caracteristicas_x_inmueble_mae
            SET categoria_override_id = 2
            WHERE tipo_inmueble_id = 12 AND caracteristica_id IN (20, 21)
        """)
        print(f"  Accesos ascensor (20,21) -> cat 2 'Ascensores' para edificio")

        for override_cat, carac_ids in overrides.items():
            if override_cat == 2:
                continue  # Ya procesado arriba
            for cid in carac_ids:
                cur.execute("""
                    UPDATE caracteristicas_x_inmueble_mae
                    SET categoria_override_id = %s
                    WHERE tipo_inmueble_id = 12 AND caracteristica_id = %s
                """, (override_cat, cid))
            print(f"  IDs {carac_ids} -> cat {override_cat} para edificio")

        # Parking/deposits override a Areas Comunes (cat 1)
        cur.execute("""
            UPDATE caracteristicas_x_inmueble_mae
            SET categoria_override_id = 1
            WHERE tipo_inmueble_id = 12 AND caracteristica_id IN (1, 2, 3, 14, 57)
        """)
        print(f"  Parking/depositos -> cat 1 'Areas Comunes' para edificio")

        # ==========================================================
        # PASO 7: Verificacion
        # ==========================================================
        print("\n--- PASO 7: Verificacion ---")

        # Oficina tipo 1 - NO debe tener overrides
        cur.execute("""
            SELECT COUNT(*) FROM caracteristicas_x_inmueble_mae
            WHERE tipo_inmueble_id = 1 AND categoria_override_id IS NOT NULL
        """)
        print(f"  Oficina tipo 1 overrides: {cur.fetchone()[0]} (debe ser 0)")

        # Edificio tipo 12 - debe tener overrides
        cur.execute("""
            SELECT COUNT(*) FROM caracteristicas_x_inmueble_mae
            WHERE tipo_inmueble_id = 12 AND categoria_override_id IS NOT NULL
        """)
        print(f"  Edificio tipo 12 overrides: {cur.fetchone()[0]}")

        # Simular /agrupadas para OFICINA (tipo 1)
        print("\n  OFICINA (tipo 1) - Simulacion /agrupadas:")
        cur.execute("""
            SELECT
                COALESCE(co.nombre, cd.nombre, 'General') as categoria,
                COALESCE(co.orden, cd.orden, 999) as cat_orden,
                COUNT(*) as cnt
            FROM caracteristicas_x_inmueble_mae cxi
            JOIN caracteristicas_mae cm ON cm.caracteristica_id = cxi.caracteristica_id
            LEFT JOIN categorias_mae cd ON cd.categoria_id = cm.categoria_id
            LEFT JOIN categorias_mae co ON co.categoria_id = cxi.categoria_override_id
            WHERE cxi.tipo_inmueble_id = 1
              AND cxi.visible_en_filtro = true
              AND cm.activo = true
            GROUP BY COALESCE(co.nombre, cd.nombre, 'General'),
                     COALESCE(co.orden, cd.orden, 999)
            ORDER BY cat_orden
        """)
        for row in cur.fetchall():
            print(f"    {row[0]}: {row[2]} caracteristicas")

        # Simular /agrupadas para EDIFICIO (tipo 12)
        print("\n  EDIFICIO (tipo 12) - Simulacion /agrupadas:")
        cur.execute("""
            SELECT
                COALESCE(co.nombre, cd.nombre, 'General') as categoria,
                COALESCE(co.orden, cd.orden, 999) as cat_orden,
                COUNT(*) as cnt
            FROM caracteristicas_x_inmueble_mae cxi
            JOIN caracteristicas_mae cm ON cm.caracteristica_id = cxi.caracteristica_id
            LEFT JOIN categorias_mae cd ON cd.categoria_id = cm.categoria_id
            LEFT JOIN categorias_mae co ON co.categoria_id = cxi.categoria_override_id
            WHERE cxi.tipo_inmueble_id = 12
              AND cxi.visible_en_filtro = true
              AND cm.activo = true
            GROUP BY COALESCE(co.nombre, cd.nombre, 'General'),
                     COALESCE(co.orden, cd.orden, 999)
            ORDER BY cat_orden
        """)
        for row in cur.fetchall():
            print(f"    {row[0]}: {row[2]} caracteristicas")

        # ==========================================================
        # CONFIRMAR
        # ==========================================================
        print("\n" + "=" * 70)
        respuesta = input("Aplicar cambios? (si/no): ").strip().lower()
        if respuesta == 'si':
            conn.commit()
            print("\nMIGRACION APLICADA EXITOSAMENTE")
        else:
            conn.rollback()
            print("\nMIGRACION CANCELADA")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR - ROLLBACK: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    ejecutar()
