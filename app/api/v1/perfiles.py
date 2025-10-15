from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models import Usuario
from app.schemas.common import ResponseModel
from app.services.imagekit_service import imagekit_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me", response_model=ResponseModel[dict])
async def get_my_profile(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    👤 Obtener mi perfil completo
    """
    # Obtener perfil del usuario
    perfil = db.query(Usuario).filter(Usuario.usuario_id == current_user.usuario_id).first()
    
    return ResponseModel(
        success=True,
        message="Perfil obtenido exitosamente",
        data={
            "usuario_id": perfil.usuario_id,
            "email": perfil.email,
            "nombre": perfil.nombre,
            "apellido": perfil.apellido,
            "telefono": perfil.telefono,
            "dni": perfil.dni,
            "foto_perfil": perfil.foto_perfil,
            "perfil_id": perfil.perfil_id,
            "estado": perfil.estado,
            "plan_id": perfil.plan_id,
            "fecha_registro": perfil.fecha_registro,
            "fecha_ultima_sesion": perfil.fecha_ultima_sesion
        }
    )

@router.post("/avatar", response_model=ResponseModel[dict])
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    📸 Subir foto de perfil del usuario usando ImageKit
    
    - **file**: Imagen del perfil (JPG, PNG, WEBP)
    """
    try:
        logger.info(f"📸 [AVATAR] Subiendo foto de perfil para usuario {current_user.usuario_id}")
        logger.info(f"📸 [AVATAR] Content-Type: {file.content_type}")
        logger.info(f"📸 [AVATAR] Filename: {file.filename}")
        
        # Validar tipo de archivo
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido. Solo se permiten: {', '.join(allowed_types)}"
            )
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Subir a ImageKit
        file_name = f"avatar_user_{current_user.usuario_id}_{file.filename}"
        folder = "inmobiliaria/avatars"
        
        upload_result = imagekit_service.upload_image(
            file_content=file_content,
            file_name=file_name,
            folder=folder
        )
        
        if upload_result and upload_result.get('url'):
            # Actualizar foto de perfil en BD
            current_user.foto_perfil = upload_result['url']
            db.commit()
            db.refresh(current_user)
            
            logger.info(f"✅ [AVATAR] Foto de perfil actualizada exitosamente")
            logger.info(f"   📸 URL: {upload_result['url']}")
            
            return ResponseModel(
                success=True,
                message="Foto de perfil actualizada exitosamente",
                data={
                    "foto_perfil": upload_result['url'],
                    "file_id": upload_result.get('file_id'),
                    "thumbnail": upload_result.get('thumbnail_url')
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al subir la imagen a ImageKit"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [AVATAR] Error subiendo foto de perfil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir foto de perfil: {str(e)}"
        )

@router.delete("/avatar", response_model=ResponseModel[dict])
async def remove_avatar(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    🗑️ Eliminar foto de perfil del usuario
    """
    try:
        # Remover foto de perfil
        current_user.foto_perfil = None
        db.commit()
        
        logger.info(f"✅ [AVATAR] Foto de perfil eliminada para usuario {current_user.usuario_id}")
        
        return ResponseModel(
            success=True,
            message="Foto de perfil eliminada exitosamente",
            data={}
        )
        
    except Exception as e:
        logger.error(f"❌ [AVATAR] Error eliminando foto de perfil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar foto de perfil: {str(e)}"
        )

@router.put("/me", response_model=ResponseModel[dict])
async def update_my_profile(
    nombre: str = None,
    apellido: str = None,
    telefono: str = None,
    dni: str = None,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    ✏️ Actualizar mi perfil
    
    - **nombre**: Nombre del usuario
    - **apellido**: Apellido del usuario
    - **telefono**: Teléfono del usuario
    - **dni**: DNI del usuario
    """
    try:
        # Actualizar campos si se proporcionan
        if nombre:
            current_user.nombre = nombre
        if apellido:
            current_user.apellido = apellido
        if telefono:
            current_user.telefono = telefono
        if dni:
            current_user.dni = dni
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"✅ [PERFIL] Perfil actualizado para usuario {current_user.usuario_id}")
        
        return ResponseModel(
            success=True,
            message="Perfil actualizado exitosamente",
            data={
                "usuario_id": current_user.usuario_id,
                "email": current_user.email,
                "nombre": current_user.nombre,
                "apellido": current_user.apellido,
                "telefono": current_user.telefono,
                "dni": current_user.dni,
                "foto_perfil": current_user.foto_perfil
            }
        )
        
    except Exception as e:
        logger.error(f"❌ [PERFIL] Error actualizando perfil: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}"
        )
