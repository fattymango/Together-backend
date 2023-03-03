FROM python:3.10-alpine

WORKDIR /code

COPY requirements.txt /code

RUN pip3 install -r requirements.txt --no-cache-dir
RUN pip3 install channels-redis
RUN apk add --no-cache libstdc++
COPY . /code
VOLUME /app/demoo/${MEDIA_URL}
EXPOSE 8000
CMD python manage.py runserver $ENV_DJANGO_HOST:$ENV_DJANGO_PORT