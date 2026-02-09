import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_shorten_url_valid():
    """Тест создания короткой ссылки с валидным URL"""
    response = client.post(
        "/shorten",
        json={"url": "https://example.com"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "short_url" in data
    assert "short_code" in data
    assert data["original_url"] == "https://example.com"

def test_shorten_url_invalid():
    """Тест создания короткой ссылки с невалидным URL"""
    response = client.post(
        "/shorten",
        json={"url": "not-a-valid-url"}
    )
    
    assert response.status_code == 400

def test_redirect_existing():
    """Тест редиректа по существующему коду"""
    # Сначала создаем короткую ссылку
    create_response = client.post(
        "/shorten",
        json={"url": "https://example.com"}
    )
    short_code = create_response.json()["short_code"]
    
    # Затем пробуем перейти по ней
    redirect_response = client.get(f"/follow/{short_code}", follow_redirects=False)
    
    assert redirect_response.status_code == 307  # Temporary Redirect
    assert "example.com" in redirect_response.headers["location"]

def test_redirect_nonexistent():
    """Тест редиректа по несуществующему коду"""
    response = client.get("/nonexistentcode")
    
    assert response.status_code == 404

def test_health_check():
    """Тест проверки здоровья приложения"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_stats():
    """Тест получения статистики"""
    response = client.get("/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_urls" in data
    assert "total_clicks" in data
    assert "top_urls" in data