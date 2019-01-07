FROM python:3.7.1-alpine3.8
MAINTAINER Yenchen
WORKDIR /app
ADD . /app
RUN apk add --no-cache libressl-dev gcc musl-dev libffi-dev
RUN pip install -r requirements.txt
RUN apk del libressl-dev musl-dev libffi-dev gcc
CMD nameko run --config config.yaml file