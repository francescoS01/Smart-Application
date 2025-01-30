FROM python:3.8-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Installing libraries
RUN apk update && apk add libpq

# Installing build dependencies
RUN apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev libffi-dev openssl-dev
RUN apk add librdkafka-dev --repository=https://dl-cdn.alpinelinux.org/alpine/edge/community
RUN apk add make

COPY ["./API Layer/requirements.txt", "./API Layer/test-requirements.txt", "./API Layer/pytest.ini", "/usr/src/app/"]

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir -r test-requirements.txt

# Delete build dependencies
RUN apk del .build-deps

RUN mkdir -p /usr/src/app/swagger_server
COPY ["./API Layer/swagger_server", "/usr/src/app/swagger_server/"]
COPY ./Storage/warehouse.py ./Storage/kafka.py /usr/src/app/swagger_server/ext/

# Long term dependencies
RUN apk add openssl
RUN apk add --no-cache bash

RUN pip freeze > requirements.txt

EXPOSE 443

# On start, generate the SSL certificate

ENTRYPOINT ["sh"]

CMD ["-c", "openssl req -x509 -newkey rsa:4096 -keyout ./swagger_server/key.pem -out ./swagger_server/cert.pem -sha256 -nodes -subj '/CN=localhost' -days 365 && \
    pdoc swagger_server -o ./docs && \
    python3 -m swagger_server"]