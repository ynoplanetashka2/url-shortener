import hashlib
import string
import random
import logging
from urllib.parse import urlparse
from .config import logger

def generate_short_code(url: str, length: int = 6) -> str:
    """Генерация короткого кода для URL"""
    # Используем хеш URL как основу для генерации
    url_hash = hashlib.md5(url.encode()).hexdigest()
    
    # Берем первые N символов из хеша
    base_code = url_hash[:length]
    
    # Добавляем немного случайности для уникальности
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=2))
    
    return base_code + random_suffix

def validate_url(url: str) -> bool:
    """Валидация URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(url: str) -> str:
    """Нормализация URL"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url