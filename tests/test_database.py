import pytest
import sqlite3
import tempfile
import os
import src.database as database_module

@pytest.fixture
def temp_db():
    """Создание временной базы данных для тестов"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Временно подменяем путь к БД
    original_db_path = None
    if hasattr(database_module, 'DB_PATH'):
        original_db_path = database_module.DB_PATH
    
    yield db_path
    
    # Восстанавливаем оригинальный путь
    if original_db_path:
        database_module.DB_PATH = original_db_path
    
    # Удаляем временный файл
    os.unlink(db_path)

def test_init_db(temp_db):
    """Тест инициализации базы данных"""
    database_module.DB_PATH = temp_db
    database_module.Database()
    
    # Проверяем создание таблицы
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urls'")
    assert cursor.fetchone() is not None
    conn.close()

def test_create_and_get_url(temp_db):
    """Тест создания и получения URL"""
    database_module.DB_PATH = temp_db
    db = database_module.Database()
    
    # Создаем URL
    url_data = db.create_url("https://example.com", "test123")
    assert url_data['original_url'] == "https://example.com"
    assert url_data['short_code'] == "test123"
    
    # Получаем URL
    retrieved = db.get_url_by_code("test123")
    assert retrieved is not None
    assert retrieved['original_url'] == "https://example.com"
    
    # Проверяем несуществующий код
    not_found = db.get_url_by_code("nonexistent")
    assert not_found is None