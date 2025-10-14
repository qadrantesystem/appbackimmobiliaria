from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, TIMESTAMP, ForeignKey, CheckConstraint, ARRAY, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Propiedad(Base):
    """Modelo de Propiedad (Cabecera)"""
    __tablename__ = "registro_x_inmueble_cab"
    
    registro_cab_id = Column(Integer, primary_key=True, index=True)
    
    # Usuario que registra
    usuario_id = Column(Integer, ForeignKey("usuarios.usuario_id"), nullable=False)
    
    # Propietario real (SIEMPRE obligatorio)
    propietario_real_nombre = Column(String(200), nullable=False)
    propietario_real_dni = Column(String(20), nullable=False)
    propietario_real_telefono = Column(String(20), nullable=False)
    propietario_real_email = Column(String(100))
    
    # Corredor asignado (si aplica)
    corredor_asignado_id = Column(Integer, ForeignKey("usuarios.usuario_id"))
    comision_corredor = Column(DECIMAL(5, 2))
    
    # Datos del inmueble
    tipo_inmueble_id = Column(Integer, ForeignKey("tipo_inmueble_mae.tipo_inmueble_id"), nullable=False)
    distrito_id = Column(Integer, ForeignKey("distritos_mae.distrito_id"), nullable=False)
    nombre_inmueble = Column(String(200), nullable=False)
    direccion = Column(String(300), nullable=False)
    latitud = Column(DECIMAL(10, 8))
    longitud = Column(DECIMAL(11, 8))
    
    # Características básicas
    area = Column(DECIMAL(10, 2), nullable=False)
    habitaciones = Column(Integer)
    banos = Column(Integer)
    parqueos = Column(Integer)
    antiguedad = Column(Integer)
    
    # Precios
    transaccion = Column(String(20))
    precio_venta = Column(DECIMAL(12, 2))
    precio_alquiler = Column(DECIMAL(10, 2))
    moneda = Column(String(3), default="PEN")
    
    # Descripción
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    
    # Imágenes
    imagen_principal = Column(String(500))
    imagenes = Column(ARRAY(String))
    
    # Documentos
    documentos_url = Column(ARRAY(String))
    documentos_verificados = Column(Boolean, default=False)
    verificado_por = Column(Integer, ForeignKey("usuarios.usuario_id"))
    verificado_at = Column(TIMESTAMP)
    
    # Estado CRM
    estado_crm = Column(String(50), default="lead")
    
    # Estado de publicación
    estado = Column(String(20), default="borrador")
    motivo_rechazo = Column(Text)
    
    # Métricas
    vistas = Column(Integer, default=0)
    contactos = Column(Integer, default=0)
    compartidos = Column(Integer, default=0)
    
    # Auditoría
    created_by = Column(Integer, ForeignKey("usuarios.usuario_id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_by = Column(Integer, ForeignKey("usuarios.usuario_id"))
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("transaccion IN ('venta', 'alquiler', 'ambos')", name="check_transaccion"),
        CheckConstraint("estado_crm IN ('lead', 'contacto', 'propuesta', 'negociacion', 'pre_cierre', 'cerrado_ganado', 'cerrado_perdido')", name="check_estado_crm"),
        CheckConstraint("estado IN ('borrador', 'publicado', 'pausado', 'cerrado', 'rechazado')", name="check_estado"),
    )
    
    # Relationships
    usuario = relationship("Usuario", foreign_keys=[usuario_id], backref="propiedades")
    corredor = relationship("Usuario", foreign_keys=[corredor_asignado_id], backref="propiedades_asignadas")
    tipo_inmueble = relationship("TipoInmueble", backref="propiedades")
    distrito = relationship("Distrito", backref="propiedades")
    
    def __repr__(self):
        return f"<Propiedad {self.titulo}>"
