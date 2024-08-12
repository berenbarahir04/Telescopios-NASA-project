class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Añade otras configuraciones comunes

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Cositalinda04$@localhost:3303/newsletter'
    MAILERSEND_API_KEY = 'mlsn.0485c84168816bfc45065c1e2dea455a66e7050589d2d30f33921bb9784f3ad8'  # Reemplaza con tu API key de MailerSend
    # Añade otras configuraciones específicas para desarrollo
