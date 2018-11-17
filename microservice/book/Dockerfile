FROM python:3.7.1-alpine3.8
MAINTAINER Yenchen
WORKDIR /app
ADD . /app
RUN apk add --no-cache gcc musl-dev
RUN pip install -r requirements.txt
CMD nameko run --config config.yaml book