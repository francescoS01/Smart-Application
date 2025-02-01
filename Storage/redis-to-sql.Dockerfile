# Usa un'immagine base Python
FROM python:3.10-slim

# Imposta la working directory
WORKDIR /app

# Copia i requisiti nel container
COPY requirements_redis_to_sql.txt /app/

# Aggiorna pip e installa le dipendenze
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements_redis_to_sql.txt

# Copia il codice del progetto nel container
COPY . /app/

# Comando per avviare la funzione che esegue il trigger
CMD ["python3", "redis_to_sql.py"]
