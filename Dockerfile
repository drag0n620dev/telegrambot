# 1. Basis-Image
FROM python:3.11-slim

# 2. Arbeitsverzeichnis erstellen
WORKDIR /app

# 3. Abhängigkeiten kopieren und installieren
ENV TIMEZONE=Europe/Berlin

RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TIMEZONE /etc/localtime && \
    echo $TIMEZONE > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4. Bot-Code kopieren
COPY bot.py ./

# 5. Environment-Variable für Token (optional)
ENV BOT_TOKEN=dein_telegram_token
ENV CHAT_ID=123456789
ENV BUNDESLAND=RP

# 6. Startkommando
CMD ["python", "bot.py"]
