import time
import schedule
import redis
import pickle
import psycopg2
from datetime import datetime, timedelta
from feature_store_utils import *
import logging
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text


def get_data_from_redis_by_timestamp(threshold_time: datetime, redis_client, engine):
    matching_data = []  # Dati da salvare in SQL
    all_keys = redis_client.keys('*')  # Ottieni tutte le chiavi di Redis

    print(f"Threshold time: {threshold_time}")  # Debug

    for key in all_keys:
        key_str = key.decode('utf-8')
        print(f"Analizzando chiave: {key_str}")
        raw_data_list = redis_client.lrange(key, 0, -1)

        key_parts = key_str.split(":")
        machineid = key_parts[0]  
        kpi = key_parts[1]  
        aggregation_type = key_parts[2]  

        to_remove = []  # Lista per i dati vecchi da eliminare

        for raw_data in raw_data_list:
            # Deserializza i dati
            data = pickle.loads(raw_data)

            # Aggiungi i campi relativi alla chiave nei dati
            data['machineid'] = machineid
            data['kpi'] = kpi
            data['aggregation_type'] = aggregation_type

            print(f"Dato trovato: {data['timestamp']}")  # Debug: stampa il timestamp

            # controllo se il timestamp è minore di threshold_time (cioè vecchio)
            if data['timestamp'].replace(tzinfo=None) < threshold_time.replace(tzinfo=None):
                matching_data.append(data)  # Dati da salvare in SQL
                to_remove.append(raw_data)  # Dati da eliminare da Redis

        # Se ci sono dati vecchi, li salviamo in SQL
        if to_remove:
            df = pd.DataFrame(matching_data)
            insert_data_to_sql(df, "historical_store", engine)  # Inserisce in SQL
            print(f"{len(matching_data)} dati inseriti in SQL")

        # Ora eliminiamo SOLO i dati vecchi da Redis
        for raw_data in to_remove:
            redis_client.lrem(key, 1, raw_data)  
            print(f"Eliminato da Redis: {raw_data}")

    return matching_data  # Ritorna i dati appena inseriti in SQL



def redis_to_sql():
    # Crea client Redis e connessione al database PostgreSQL
    engine = n_engine()

    # Imposta il filtro temporale per i dati (ad esempio, più recenti di 1 minuto)
    local_tz = pytz.timezone('Europe/Rome') # Fuso orario locale
    threshold_time = datetime.now(local_tz) - timedelta(minutes=1)
    redis_client = redis.StrictRedis(host='storage-redis-1', port=6379, db=0)

    # Recupera i dati da che sono stati inseriti prima di threshold_time
    data_from_redis = get_data_from_redis_by_timestamp(threshold_time, redis_client, engine)

    # se ci sono dati in redis 
    if data_from_redis:
        # Converti i dati in un DataFrame
        df = pd.DataFrame(data_from_redis)
        print(df)

        # Inserisci i dati nel database PostgreSQL
        insert_data_to_sql(df, "historical_store", engine)

        print(f"Elaborazione completata: {len(df)} dati inseriti nel database")
    else:
        print("Nessun dato da trasferire da Redis a PostgreSQL.")




def delete_data_from_redis(conditions, redis_client):
    # Verifica che il dizionario contenga tutte le chiavi necessarie
    required_keys = ['machineid', 'kpi', 'aggregation_type', 'timestamp']
    
    for key in required_keys:
        if key not in conditions:
            print(f"Errore: il dizionario manca della chiave {key}.")
            return
    
    # Estrai i valori dal dizionario
    machineid = conditions['machineid'][0]  # Assumiamo che ci sia solo un valore
    kpi = conditions['kpi'][0]  # Assumiamo che ci sia solo un valore
    aggregation_type = conditions['aggregation_type'][0]  # Assumiamo che ci sia solo un valore
    timestamp_to_delete = conditions['timestamp'][0]  # Assumiamo che ci sia solo un valore
    
    # Costruisce la chiave utilizzando i parametri
    key = build_key(machineid, kpi, aggregation_type)
    
    # Recupera tutti i dati dalla lista
    raw_data_list = redis_client.lrange(key, 0, -1)
    
    # Scorri la lista per trovare e rimuovere il dato con il timestamp specificato
    for raw_data in raw_data_list:
        data = pickle.loads(raw_data)
        
        # Confronta il timestamp e verifica se è quello da eliminare
        if data['timestamp'] == timestamp_to_delete:
            # Rimuove il dato dalla lista
            redis_client.lrem(key, 0, raw_data)
            print(f"Dato con timestamp {timestamp_to_delete} rimosso dalla chiave {key}")
            return
    
    print(f"Nessun dato trovato con timestamp {timestamp_to_delete} nella chiave {key}.")


def n_engine(hostname='storage-db-1'):  # Usa il nome del servizio/container PostgreSQL
    """
    Create a new SQLAlchemy engine for PostgreSQL.
    Args:
        hostname (str): The hostname of the PostgreSQL server.
    Returns:
        Engine: SQLAlchemy engine object.
    """
    username = 'postgres'
    password = 'password'
    port = '5432'
    database = 'postgres'
    engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{database}")
    return engine


# Funzione per eseguire il trasferimento ogni 30 secondi
schedule.every(30).seconds.do(redis_to_sql)

# Loop principale
while True:
    schedule.run_pending()
    time.sleep(1)



""" ------------- DA ELIMINARE -------------

def get_data_from_redis_by_timestamp1(threshold_time: datetime, redis_client, engine):
    matching_data = []
    all_keys = redis_client.keys('*')  # Ottieni tutte le chiavi di Redis

    for key in all_keys:
        key_str = key.decode('utf-8') 
        print(key_str)
        raw_data_list = redis_client.lrange(key, 0, -1)

        key_parts = key_str.split(":")
        machineid = key_parts[0]  # Ottieni il primo elemento come machineid
        kpi = key_parts[1]  # Ottieni il secondo elemento come kpi
        aggregation_type = key_parts[2]  # Ottieni il terzo elemento come aggregation_type

       
        for raw_data in raw_data_list:
            # Deserializza i dati
            data = pickle.loads(raw_data)

            # Aggiungi i campi relativi alla chiave nei dati
            data['machineid'] = machineid  # Aggiungi machineid (dal formato della chiave)
            data['kpi'] = kpi  # Aggiungi kpi (dal formato della chiave)
            data['aggregation_type'] = aggregation_type  # Aggiungi aggregation_type (dal formato della chiave)]

            # Verifica se il timestamp è maggiore di threshold_time
            if data['timestamp'] > threshold_time:
                matching_data.append(data)
                # Eliminazione diretta da Redis
                redis_client.lrem(key, 0, raw_data)  
                print(f"Eliminato da Redis: {data}")  

    print(matching_data)
    return matching_data



    
# Rimuovi i dati trasferiti da Redis
    for _, row in df.iterrows():
        # Crea un dizionario con le condizioni per la rimozione
        conditions = {
        'machineid': [row['machineid']],
            'kpi': [row['kpi']],
            'aggregation_type': [row['aggregation_type']],
            'timestamp': [row['timestamp']]
        }

        # Chiamata alla funzione per eliminare i dati da Redis
        delete_data_from_redis(conditions, redis_client)
        
"""