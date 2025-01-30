FROM python:3.11.10-slim
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN mkdir Data_Processing 
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-server-dev-all
COPY ./Data-Processing/Data_Processing/requirements.txt .
RUN pip install -r requirements.txt
COPY ./Data-Processing/Data_Processing ./Data_Processing
COPY ./Storage/feature_store_utils.py ./Data_Processing/feature_store_utils.py
COPY ./Data-Processing/Data_Processing/feature_store.yaml ./Feature_store/feature_store.yaml
COPY ./Storage/postgres_store/feature_repo/example_repo.py ./Feature_store/example_repo.py

RUN pip freeze > requirements.txt

ENV API_HOSTNAME="api-layer"
ENV API_PORT=443
ENV REDIS_HOSTNAME="redis"
ENV REDIS_PORT=6379
ENV DB_HOSTNAME="db"
ENV PDOC_ALLOW_EXEC=1
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV TF_ENABLE_ONEDNN_OPTS=0
ENV PDOC_DISPLAY_ENV_VARS=1

ENTRYPOINT ["sh"]

CMD ["-c", "\
pdoc Data_Processing -o ./docs && \
python3 -u -m Data_Processing"]