import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    DOCUMENTS_FOLDER = os.getenv('DOCUMENTS_FOLDER', 'instance/documentos')
    COMPROBANTES_FOLDER = os.getenv('COMPROBANTES_FOLDER', 'instance/comprobantes')
    SILABOS_FOLDER = os.getenv('SILABOS_FOLDER', 'instance/silabos')
    PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', 'http://127.0.0.1:5000')
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024  # 6 MB (margen de comprobantes)