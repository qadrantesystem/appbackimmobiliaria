#!/usr/bin/env python3
"""
Script para generar hash de password con bcrypt
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generar hash para password "123456"
password = "123456"
hashed = pwd_context.hash(password)

print(f"Password: {password}")
print(f"Hash: {hashed}")
print(f"\nVerificación: {pwd_context.verify(password, hashed)}")
