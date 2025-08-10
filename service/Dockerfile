FROM python:3.13.5-alpine3.21

RUN apk add --no-cache \
    sqlite \
    sqlite-dev \
    build-base \
    linux-headers

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads && \
    touch /app/notes.db && \
    chmod 777 /app/uploads /app/notes.db && \
    chmod 777 /tmp

EXPOSE 5000

CMD ["python3", "web.py"]
