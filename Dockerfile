FROM python:3.12-slim

WORKDIR /app

COPY ./pyproject.toml ./
RUN pip install .

COPY ./src ./src

CMD ["python3", "-m", "src.main"]
