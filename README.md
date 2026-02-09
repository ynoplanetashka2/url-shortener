# Быстрый старт

- Запустить проект - `docker compose up -d main`, сервер поднимается на 8000 порту.
- Запустить тесты - `docker compose up tests`

## Запуск без докера

Нужно установить зависимости `pip install -e .`.
Запустить сервер `python3 -m src.main`

Тесты - `pytest test -v`
