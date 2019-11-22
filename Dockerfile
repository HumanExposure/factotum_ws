FROM python:3.7-alpine

ARG FACTOTUM_BRANCH=dev

RUN apk add --no-cache \
        g++ \
        git \
        mariadb-dev

COPY requirements.txt /requirements.txt
RUN sed -i "/factotum.git/d" /requirements.txt \
 && pip --no-cache-dir install -r /requirements.txt \
 && rm /requirements.txt

WORKDIR /factotum
ADD https://github.com/HumanExposure/factotum/archive/${FACTOTUM_BRANCH}.tar.gz src.tar.gz
RUN tar -xf src.tar.gz --strip-components=1 \
 && pip --no-cache-dir install . \
 && rm -rf /factotum

COPY . /app/.
WORKDIR /app
RUN rm -f .env \
 && rm -rf collected_static \
 && python manage.py collectstatic

CMD gunicorn config.wsgi -c config/gunicorn.py --log-config config/logging.conf

EXPOSE 8001
VOLUME /app/collected_static
