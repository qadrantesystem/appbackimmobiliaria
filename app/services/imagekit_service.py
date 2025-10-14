from imagekitio import ImageKit
from app.core.config import settings
import base64
import uuid

# Inicializar ImageKit
imagekit = ImageKit(
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
)

class ImageKitService:
    """Servicio para gestión de imágenes con ImageKit"""
    
    @staticmethod
    def upload_image(file_content: bytes, file_name: str, folder: str = "propiedades") -> dict:
        """
        Subir imagen a ImageKit
        
        Args:
            file_content: Contenido del archivo en bytes
            file_name: Nombre del archivo
            folder: Carpeta en ImageKit (default: propiedades)
            
        Returns:
            dict con url, file_id, etc.
        """
        try:
            # Generar nombre único
            unique_name = f"{uuid.uuid4()}_{file_name}"
            
            # Subir imagen
            upload_result = imagekit.upload(
                file=file_content,
                file_name=unique_name,
                options={
                    "folder": f"/{folder}/",
                    "is_private_file": False,
                    "use_unique_file_name": True
                }
            )
            
            return {
                "success": True,
                "url": upload_result.url,
                "file_id": upload_result.file_id,
                "name": upload_result.name,
                "thumbnail_url": upload_result.thumbnail_url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def upload_base64_image(base64_string: str, file_name: str, folder: str = "propiedades") -> dict:
        """
        Subir imagen desde base64
        
        Args:
            base64_string: String en base64 de la imagen
            file_name: Nombre del archivo
            folder: Carpeta en ImageKit
            
        Returns:
            dict con url, file_id, etc.
        """
        try:
            # Decodificar base64
            file_content = base64.b64decode(base64_string)
            return ImageKitService.upload_image(file_content, file_name, folder)
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def delete_image(file_id: str) -> bool:
        """
        Eliminar imagen de ImageKit
        
        Args:
            file_id: ID del archivo en ImageKit
            
        Returns:
            bool indicando éxito
        """
        try:
            imagekit.delete_file(file_id)
            return True
        except Exception as e:
            print(f"Error eliminando imagen: {e}")
            return False
    
    @staticmethod
    def get_image_url(file_path: str, transformations: dict = None) -> str:
        """
        Obtener URL de imagen con transformaciones
        
        Args:
            file_path: Ruta del archivo en ImageKit
            transformations: Dict con transformaciones (width, height, etc.)
            
        Returns:
            URL de la imagen
        """
        try:
            if transformations:
                url = imagekit.url({
                    "path": file_path,
                    "transformation": [transformations]
                })
            else:
                url = f"{settings.IMAGEKIT_URL_ENDPOINT}/{file_path}"
            
            return url
        except Exception as e:
            print(f"Error generando URL: {e}")
            return ""
