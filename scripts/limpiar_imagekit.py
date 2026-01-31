"""
Script para limpiar todos los archivos de ImageKit
Ejecutar una sola vez para resetear el storage
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from imagekitio import ImageKit
from imagekitio.models.ListAndSearchFileRequestOptions import ListAndSearchFileRequestOptions

# Credenciales de ImageKit
PRIVATE_KEY = "private_1xysV6NsG2Lm3I+iU63EhJHfJ2g="
PUBLIC_KEY = "public_y/LX/tLO5qSkPjgOTlEx8JnFq9Q="
URL_ENDPOINT = "https://ik.imagekit.io/3y7rfi7jj"

def main():
    print("[CLEAN] Iniciando limpieza de ImageKit...")

    # Inicializar cliente
    imagekit = ImageKit(
        private_key=PRIVATE_KEY,
        public_key=PUBLIC_KEY,
        url_endpoint=URL_ENDPOINT
    )

    print("[OK] ImageKit conectado")

    # Listar todos los archivos
    print("\n[LIST] Listando archivos...")

    try:
        result = imagekit.list_files(
            options=ListAndSearchFileRequestOptions(
                limit=1000  # Maximo permitido
            )
        )

        if result and result.list:
            files = result.list
            print(f"[FOUND] Encontrados: {len(files)} archivos")

            if len(files) == 0:
                print("[EMPTY] ImageKit ya esta vacio")
                return

            # Mostrar archivos encontrados
            print("\n[FILES] Archivos a eliminar:")
            for f in files:
                print(f"   - {f.file_path} ({f.file_id})")

            # Eliminar cada archivo
            print("\n[DELETE] Eliminando archivos...")
            deleted = 0
            errors = 0

            for f in files:
                try:
                    imagekit.delete_file(file_id=f.file_id)
                    print(f"   [OK] Eliminado: {f.file_path}")
                    deleted += 1
                except Exception as e:
                    print(f"   [ERROR] Error eliminando {f.file_path}: {e}")
                    errors += 1

            print(f"\n[SUMMARY] Resumen:")
            print(f"   Eliminados: {deleted}")
            print(f"   Errores: {errors}")

        else:
            print("[EMPTY] No se encontraron archivos en ImageKit")

    except Exception as e:
        print(f"[ERROR] Error listando archivos: {e}")

if __name__ == "__main__":
    main()
