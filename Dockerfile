FROM python:3-alpine

RUN apk add --no-cache \
        g++ \
        git \
        libxml2-dev \
        libxslt-dev \
        linux-headers \
        mariadb-dev \
        python3-dev

COPY requirements.txt /requirements.txt
RUN pip3 --no-cache-dir install -r /requirements.txt \
 && rm /requirements.txt

COPY . /app/.
WORKDIR /app
RUN rm -rf static \
 && python3 manage.py collectstatic

CMD gunicorn config.wsgi -c config/gunicorn.conf --log-config config/logging.conf

EXPOSE 8001
VOLUME /app/static

