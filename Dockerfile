FROM python:3.12-slim

WORKDIR /app

COPY ./pyproject.toml ./
RUN pip install .

COPY ./src ./src
RUN pip install -e .[dev]

COPY ./tests ./tests

CMD ["python3", "-m", "src.main"]
