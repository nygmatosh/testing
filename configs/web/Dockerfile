FROM python:3.11-slim-bullseye

WORKDIR /usr/src/app/web/

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]