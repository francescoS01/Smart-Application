# Usa Python come immagine base
FROM python:3.9-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia solo il file dei requisiti per sfruttare la cache Docker
COPY Milestone3/Requirements.txt .

# Installa le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    libomp-dev \
    libfreetype6-dev \
    libxft-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installa le dipendenze Python utilizzando il file requirements.txt
RUN pip install --no-cache-dir -r Requirements.txt

# Copia il resto dei file del progetto nella directory di lavoro
COPY . .

# Aggiungi un healthcheck per verificare la comunicazione con il container di Ollama
HEALTHCHECK --interval=30s CMD curl -f http://localhost:11434/v1 || exit 1

# Specifica il comando di avvio
CMD ["python", "Milestone3/generation.py"]
