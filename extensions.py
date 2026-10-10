import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_mailman import Mail
from itsdangerous import URLSafeTimedSerializer

load_dotenv()

db = SQLAlchemy()
mail = Mail()

secret_key = os.getenv('SECRET_KEY')
encryption_key = os.getenv('ENCRYPTION_KEY')

cipher = Fernet(encryption_key.encode()) if encryption_key else None
serializer = URLSafeTimedSerializer(secret_key)