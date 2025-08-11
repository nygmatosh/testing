FROM python:3.11-slim-bullseye

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=web.web.settings

CMD ["python", "-m", "web.web.start_ws.py"]