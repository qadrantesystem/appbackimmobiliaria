from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password = "123456"
hash_generado = pwd_context.hash(password)

print(f"Password: {password}")
print(f"Hash: {hash_generado}")
print(f"Longitud: {len(hash_generado)}")
