from decouple import config
from typing import List

class Settings:
    """Configuración global de la aplicación"""
    
    # 🔐 JWT Configuration
    SECRET_KEY: str = config("SECRET_KEY", default="inmobiliaria-super-secret-key-development")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)
    
    # 🗄️ Database
    DATABASE_URL: str = config(
        "DATABASE_URL", 
        default="postgresql://postgres:esbHQXHuToTttMYUpnRCkYAdHMpXapuM@maglev.proxy.rlwy.net:44913/railway"
    )
    
    # 📸 ImageKit (para imágenes de propiedades)
    IMAGEKIT_PRIVATE_KEY: str = config("IMAGEKIT_PRIVATE_KEY", default="private_juJdHhsZIjOMwacjNq6/94YqfYo=")
    IMAGEKIT_PUBLIC_KEY: str = config("IMAGEKIT_PUBLIC_KEY", default="public_m7rawfzMCD/O2+1pNfMA8aHqCkk=")
    IMAGEKIT_URL_ENDPOINT: str = config("IMAGEKIT_URL_ENDPOINT", default="https://ik.imagekit.io/3y7rfi7jj")
    
    # 📧 SendGrid Email Service
    SENDGRID_API_KEY: str = config("SENDGRID_API_KEY", default="")
    SENDGRID_FROM_EMAIL: str = config("SENDGRID_FROM_EMAIL", default="noreply@inmobiliaria.com")
    SENDGRID_FROM_NAME: str = config("SENDGRID_FROM_NAME", default="Sistema Inmobiliario")
    
    # 📱 Twilio SMS
    TWILIO_ACCOUNT_SID: str = config("TWILIO_ACCOUNT_SID", default="")
    TWILIO_AUTH_TOKEN: str = config("TWILIO_AUTH_TOKEN", default="")
    TWILIO_PHONE_NUMBER: str = config("TWILIO_PHONE_NUMBER", default="")
    
    # 🌐 CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 🔄 Environment
    ENVIRONMENT: str = config("ENVIRONMENT", default="development")
    
    # 📄 Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

settings = Settings()
