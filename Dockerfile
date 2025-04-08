FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN pip install .

COPY . .

EXPOSE 8000
EXPOSE 3000

CMD ["sh", "-c", "streamlit run src/app.py & uvicorn src.api:app --host 0.0.0.0 --port 8000"]