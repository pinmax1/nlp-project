FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

# not crit, but it is better to keep it sync with port in .env file
EXPOSE 8000

CMD ["python3", "backend/main.py", "-e", "backend/configs/.env.testing"]
