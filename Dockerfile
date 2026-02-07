FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

EXPOSE 5555

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5555", "--workers", "4", "--timeout", "120", "run:app"]
