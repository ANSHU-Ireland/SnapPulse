FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/collector/app.py .
COPY services/collector/feast_repo ./feast_repo

CMD ["python3", "app.py"]
