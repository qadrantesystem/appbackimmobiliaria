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
    
    # 📸 ImageKit (para imágenes de propiedades y perfiles)
    IMAGEKIT_PRIVATE_KEY: str = config("IMAGEKIT_PRIVATE_KEY", default="private_1xysV6NsG2Lm3I+iU63EhJHfJ2g=")
    IMAGEKIT_PUBLIC_KEY: str = config("IMAGEKIT_PUBLIC_KEY", default="public_y/LX/tLO5qSkPjgOTlEx8JnFq9Q=")
    IMAGEKIT_URL_ENDPOINT: str = config("IMAGEKIT_URL_ENDPOINT", default="https://ik.imagekit.io/3y7rfi7jj")
    
    # 📧 SendGrid Email Service
    SENDGRID_API_KEY: str = config("SENDGRID_API_KEY", default="")
    SENDGRID_FROM_EMAIL: str = config("SENDGRID_FROM_EMAIL", default="noreply@inmobiliaria.com")
    SENDGRID_FROM_NAME: str = config("SENDGRID_FROM_NAME", default="Sistema Inmobiliario")
    
    # 📧 SMTP Email Service (Servidor Propio)
    SMTP_HOST: str = config("SMTP_HOST", default="mail.qadrante2.com")
    SMTP_PORT: int = config("SMTP_PORT", default=587, cast=int)
    SMTP_USER: str = config("SMTP_USER", default="")
    SMTP_PASSWORD: str = config("SMTP_PASSWORD", default="")
    SMTP_FROM_EMAIL: str = config("SMTP_FROM_EMAIL", default="sistemas@qadrante2.com")
    SMTP_FROM_NAME: str = config("SMTP_FROM_NAME", default="Sistema Inmobiliario")
    USE_SMTP: bool = config("USE_SMTP", default=True, cast=bool)
    
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
