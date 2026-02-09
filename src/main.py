from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import logging
from .database import Database
from .utils import generate_short_code, validate_url, normalize_url
from .config import logger

app = FastAPI(
    title="URL Shortener",
    description="Сервис для сокращения длинных ссылок",
    version="1.0.0"
)

db = Database()

class URLRequest(BaseModel):
    url: str

class URLResponse(BaseModel):
    original_url: str
    short_url: str
    short_code: str

@app.post("/shorten", response_model=URLResponse, status_code=201)
async def shorten_url(url_request: URLRequest):
    """Создание короткой ссылки"""
    original_url = url_request.url
    
    # Валидация URL
    if not validate_url(original_url):
        logger.warning(f"Попытка сократить невалидный URL: {original_url}")
        raise HTTPException(status_code=400, detail="Некорректный URL")
    
    # Нормализация URL
    normalized_url = normalize_url(original_url)
    
    # Генерация короткого кода
    short_code = generate_short_code(normalized_url)
    
    # Проверка на существование кода (хотя вероятность коллизии очень мала)
    existing_url = db.get_url_by_code(short_code)
    if existing_url and existing_url['original_url'] != normalized_url:
        # Генерируем новый код в случае коллизии
        short_code = generate_short_code(normalized_url + str(random.random()))
    
    # Сохранение в БД
    url_record = db.create_url(normalized_url, short_code)
    
    # Формирование короткого URL
    short_url = f"http://localhost:8000/{short_code}"
    
    logger.info(f"Создана короткая ссылка: {short_url} -> {normalized_url}")
    
    return URLResponse(
        original_url=normalized_url,
        short_url=short_url,
        short_code=short_code
    )

@app.get("/follow/{short_code}")
async def redirect_to_url(short_code: str):
    """Редирект по короткому коду"""
    # Получение URL из БД
    url_record = db.get_url_by_code(short_code)
    
    if not url_record:
        logger.warning(f"Попытка перехода по несуществующему коду: {short_code}")
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    
    # Увеличение счетчика переходов
    db.increment_access_count(short_code)
    
    logger.info(f"Редирект по коду {short_code} -> {url_record['original_url']}")
    
    # Редирект на оригинальный URL
    return RedirectResponse(url=url_record['original_url'])

@app.get("/stats")
async def get_statistics():
    """Получение статистики сервиса"""
    stats = db.get_stats()
    logger.info("Запрос статистики")
    return stats

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy", "service": "url-shortener"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)