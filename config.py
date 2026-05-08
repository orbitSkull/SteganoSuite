import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'steganosuite-dev-secret-key-change-in-production'
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    ALLOWED_EXTENSIONS = {
        'image': {'png', 'bmp', 'jpg', 'jpeg', 'webp'},
        'audio': {'wav', 'mp3', 'flac', 'aac', 'ogg', 'm4a'},
        'text': {'txt'}
    }
    
    # Output formats
    OUTPUT_FORMATS = {
        'image': 'png',
        'audio': 'wav'
    }
    
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
