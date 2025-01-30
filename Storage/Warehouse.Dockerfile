FROM timescale/timescaledb:latest-pg16
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres
COPY scripts/postgres/1-create-tables.sql /docker-entrypoint-initdb.d/