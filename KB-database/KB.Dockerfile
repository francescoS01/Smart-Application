FROM timescale/timescaledb:latest-pg16
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres
COPY Knowledge-base-dump-Dec-7.sql /docker-entrypoint-initdb.d/1-restore-dump.sql
COPY formula-update.sql /docker-entrypoint-initdb.d/2-formula-update.sql
COPY update-categories.sql /docker-entrypoint-initdb.d/3-update-categories.sql