import sqlite3
import logging
from datetime import datetime, timedelta
from contextlib import contextmanager
from .config import DB_PATH, logger

class Database:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_url TEXT NOT NULL,
                    short_code TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_short_code ON urls(short_code)')
            conn.commit()
            logger.info("База данных инициализирована")
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            logger.error(f"Ошибка БД: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_url(self, original_url: str, short_code: str) -> dict:
        """Создание новой короткой ссылки"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO urls (original_url, short_code)
                VALUES (?, ?)
            ''', (original_url, short_code))
            conn.commit()
            
            cursor.execute('SELECT * FROM urls WHERE id = ?', (cursor.lastrowid,))
            result = cursor.fetchone()
            logger.info(f"Создана новая ссылка: {short_code} -> {original_url}")
            return dict(result)
    
    def get_url_by_code(self, short_code: str) -> dict:
        """Получение URL по короткому коду"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM urls WHERE short_code = ?', (short_code,))
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
    
    def increment_access_count(self, short_code: str):
        """Увеличение счетчика переходов"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE urls 
                SET access_count = access_count + 1 
                WHERE short_code = ?
            ''', (short_code,))
            conn.commit()
            logger.info(f"Увеличен счетчик для кода: {short_code}")
    
    def get_stats(self) -> dict:
        """Получение статистики"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as total_urls FROM urls')
            total_urls = cursor.fetchone()['total_urls']
            
            cursor.execute('SELECT SUM(access_count) as total_clicks FROM urls')
            total_clicks = cursor.fetchone()['total_clicks'] or 0
            
            cursor.execute('''
                SELECT short_code, original_url, access_count 
                FROM urls 
                ORDER BY access_count DESC 
                LIMIT 5
            ''')
            top_urls = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_urls': total_urls,
                'total_clicks': total_clicks,
                'top_urls': top_urls
            }