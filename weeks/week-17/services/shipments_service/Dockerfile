FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/generated

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY generated ./generated
COPY services/shipments_service/app ./app

EXPOSE 8130 8131

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8130"]
