FROM python:3-alpine

RUN apk add --no-cache \
        g++ \
        git \
        mariadb-dev

COPY requirements.txt /requirements.txt
RUN pip3 --no-cache-dir install -r /requirements.txt \
 && rm /requirements.txt

COPY . /app/.
WORKDIR /app
RUN rm -f .env \
 && rm -rf collected_static \
 && python manage.py collectstatic

CMD gunicorn config.wsgi -c config/gunicorn.py --log-config config/logging.conf

EXPOSE 8001
VOLUME /app/collected_static
