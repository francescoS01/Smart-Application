# Usa l'immagine di base
FROM python:3.11-slim

# Imposta la directory di lavoro
WORKDIR /app

# Aggiungi PYTHONPATH per assicurarti che /app sia riconosciuto come root
ENV PYTHONPATH=/app

# Copia i requisiti e installali
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia il codice dell'applicazione
COPY ./app /app

# Imposta il comando di avvio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
