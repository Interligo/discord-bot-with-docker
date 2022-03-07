FROM python:3.8
LABEL maintainer="Interligo@yandex.ru"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /discord-bot

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./bot ./bot

# CMD [ "python", "bot/bot_main.py" ]
CMD python bot/bot_main.py
