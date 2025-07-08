FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads && \
    touch /app/notes.db && \
    chmod 777 /app/uploads /app/notes.db

RUN chmod 777 /tmp

RUN python -c "from app import init_db; init_db()"

EXPOSE 5000

CMD ["python", "web.py"]