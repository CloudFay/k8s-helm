FROM python:3.12-slim

# Install curl
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home appuser
WORKDIR /home/appuser

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

USER appuser
EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]