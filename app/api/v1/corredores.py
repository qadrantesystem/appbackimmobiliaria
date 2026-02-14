from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.dependencies import require_admin
from app.models import Usuario
from app.schemas.corredor import CorredorAprobar, CorredorRechazar
from app.schemas.common import ResponseModel

router = APIRouter()

PERFIL_CORREDOR = 3


def serializar_corredor(usuario: Usuario) -> dict:
    """Convierte un usuario corredor a diccionario para response"""
    return {
        "usuario_id": usuario.usuario_id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "telefono": usuario.telefono,
        "dni": usuario.dni,
        "foto_perfil": usuario.foto_perfil,
        "autorizado": usuario.autorizado,
        "comision_porcentaje": float(usuario.comision_porcentaje) if usuario.comision_porcentaje else None,
        "fecha_vigencia_corredor": usuario.fecha_vigencia_corredor.isoformat() if usuario.fecha_vigencia_corredor else None,
        "aprobado_por": usuario.aprobado_por,
        "aprobado_at": usuario.aprobado_at.isoformat() if usuario.aprobado_at else None,
        "motivo_rechazo": usuario.motivo_rechazo,
        "fecha_registro": usuario.fecha_registro.isoformat() if usuario.fecha_registro else None,
    }


@router.get("/stats", response_model=ResponseModel[dict])
async def obtener_stats_corredores(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Estadísticas de corredores: pendientes, aprobados, rechazados"""
    base = db.query(Usuario).filter(Usuario.perfil_id == PERFIL_CORREDOR)

    pendientes = base.filter(Usuario.autorizado == False, Usuario.motivo_rechazo == None).count()
    aprobados = base.filter(Usuario.autorizado == True).count()
    rechazados = base.filter(Usuario.motivo_rechazo != None, Usuario.autorizado == False).count()

    return ResponseModel(
        success=True,
        message="Estadísticas de corredores",
        data={
            "pendientes": pendientes,
            "aprobados": aprobados,
            "rechazados": rechazados,
            "total": pendientes + aprobados + rechazados
        }
    )


@router.get("/pendientes", response_model=ResponseModel[list])
async def listar_corredores_pendientes(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lista corredores con perfil_id=3 pendientes de aprobación"""
    corredores = (
        db.query(Usuario)
        .filter(
            Usuario.perfil_id == PERFIL_CORREDOR,
            Usuario.autorizado == False,
            Usuario.motivo_rechazo == None
        )
        .order_by(Usuario.fecha_registro.asc())
        .all()
    )

    return ResponseModel(
        success=True,
        message=f"{len(corredores)} corredores pendientes",
        data=[serializar_corredor(c) for c in corredores]
    )


@router.get("/aprobados", response_model=ResponseModel[list])
async def listar_corredores_aprobados(
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lista corredores ya aprobados"""
    corredores = (
        db.query(Usuario)
        .filter(
            Usuario.perfil_id == PERFIL_CORREDOR,
            Usuario.autorizado == True
        )
        .order_by(Usuario.aprobado_at.desc())
        .all()
    )

    return ResponseModel(
        success=True,
        message=f"{len(corredores)} corredores aprobados",
        data=[serializar_corredor(c) for c in corredores]
    )


@router.patch("/{usuario_id}/aprobar", response_model=ResponseModel[dict])
async def aprobar_corredor(
    usuario_id: int,
    datos: CorredorAprobar,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Aprueba un corredor: autorizado=True + comisión + vigencia"""
    corredor = db.query(Usuario).filter(
        Usuario.usuario_id == usuario_id,
        Usuario.perfil_id == PERFIL_CORREDOR
    ).first()

    if not corredor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corredor no encontrado"
        )

    if corredor.autorizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este corredor ya está aprobado"
        )

    corredor.autorizado = True
    corredor.comision_porcentaje = datos.comision_porcentaje
    corredor.fecha_vigencia_corredor = datos.fecha_vigencia
    corredor.aprobado_por = admin.usuario_id
    corredor.aprobado_at = datetime.utcnow()
    corredor.motivo_rechazo = None

    db.commit()
    db.refresh(corredor)

    return ResponseModel(
        success=True,
        message=f"Corredor {corredor.nombre} {corredor.apellido} aprobado exitosamente",
        data=serializar_corredor(corredor)
    )


@router.patch("/{usuario_id}/rechazar", response_model=ResponseModel[dict])
async def rechazar_corredor(
    usuario_id: int,
    datos: CorredorRechazar,
    admin: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Rechaza un corredor con motivo"""
    corredor = db.query(Usuario).filter(
        Usuario.usuario_id == usuario_id,
        Usuario.perfil_id == PERFIL_CORREDOR
    ).first()

    if not corredor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corredor no encontrado"
        )

    corredor.autorizado = False
    corredor.motivo_rechazo = datos.motivo_rechazo
    corredor.comision_porcentaje = None
    corredor.fecha_vigencia_corredor = None
    corredor.aprobado_por = None
    corredor.aprobado_at = None

    db.commit()
    db.refresh(corredor)

    return ResponseModel(
        success=True,
        message=f"Corredor {corredor.nombre} {corredor.apellido} rechazado",
        data=serializar_corredor(corredor)
    )
