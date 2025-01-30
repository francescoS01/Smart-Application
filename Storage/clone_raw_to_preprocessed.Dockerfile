FROM python:3.11.10-slim
WORKDIR /app
RUN mkdir Storage 
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-server-dev-all
COPY requirements_storage.txt .
RUN pip install -r requirements_storage.txt
COPY . ./Storage
ENV POSTGRES_HOST=db
CMD ["python", "-u", "-m", "Storage.clone_raw_to_preprocessed", "Storage/smart_app_data.pkl"]
