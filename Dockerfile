FROM python:3.12-slim

# Install curl safely
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app/ .

# Switch user
USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]