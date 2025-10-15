#!/usr/bin/env python3
"""
Script para actualizar passwords de usuarios con hash correcto
"""

import sys
import os
import bcrypt
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.usuario import Usuario

def update_passwords():
    """Actualizar passwords con hash correcto para 123456"""
    db = SessionLocal()
    
    try:
        print("🔐 Actualizando passwords...")
        
        # Generar hash correcto para "123456" usando bcrypt directamente
        password = "123456".encode('utf-8')
        salt = bcrypt.gensalt()
        correct_hash = bcrypt.hashpw(password, salt).decode('utf-8')
        print(f"✅ Hash generado: {correct_hash}")
        print(f"📏 Longitud del hash: {len(correct_hash)} caracteres")
        
        # Lista de usuarios a actualizar
        usuarios_emails = [
            "admin@inmobiliaria.com",
            "demandante@email.com",
            "ofertante@email.com",
            "corredor@inmobiliaria.com",
            "ana.martinez@email.com"
        ]
        
        # Actualizar cada usuario
        for email in usuarios_emails:
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
            if usuario:
                usuario.password_hash = correct_hash
                print(f"✅ Password actualizado para: {email}")
            else:
                print(f"⚠️ Usuario no encontrado: {email}")
        
        # Commit cambios
        db.commit()
        print("\n💾 Cambios guardados en base de datos")
        
        print("\n🎯 PASSWORDS ACTUALIZADOS:")
        for email in usuarios_emails:
            print(f"📧 Email: {email}")
        print("🔑 Password: 123456")
        print("\n✅ Ahora puedes hacer login con estos usuarios!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔐 Actualizando passwords de usuarios...")
    update_passwords()
    print("🚀 Script completado!")
