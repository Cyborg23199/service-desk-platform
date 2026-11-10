import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://servicedesk_user:ServiceDesk_Secure_Pass2026!@localhost:5432/servicedesk'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'dev-key-lab'