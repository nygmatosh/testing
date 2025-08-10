FROM python:3.11-slim-bullseye

WORKDIR /usr/src/app/web/web/

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "start_ws.py"]