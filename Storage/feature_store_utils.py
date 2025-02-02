"""
This module provides utility functions for interacting with a SQL database and a Feast feature store.
It includes functions for creating SQLAlchemy engines, starting the feature store, inserting and retrieving data from SQL,
deleting data from SQL, retrieving filtered online features from the feature store, and inserting data into Redis for online feature serving.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from feast import FeatureStore
import subprocess
from sqlalchemy.engine import Engine
import pytz
from feast.data_source import PushMode
from itertools import product
import pandas as pd
from feast import FeatureStore
import redis
import pickle
from datetime import datetime
import redis
import pickle
import pytz
import pickle
from datetime import datetime



def new_engine(hostname='localhost'):
    """
    Create a new SQLAlchemy engine for PostgreSQL.
    Args:
        hostname (str): The hostname of the PostgreSQL server.
    Returns:
        Engine: SQLAlchemy engine object.
    """
    username = 'postgres'
    password = 'password'
    host = hostname
    port = '5432'
    database = 'postgres'
    engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")
    return engine


def start_store(repo_dir: str = None, print__subprocess_output: bool = False):
    """
    Start the Feast feature store and apply the feature definitions.
    Args:
        repo_dir (str): The directory of the Feast repository.
    Returns:
        FeatureStore: The initialized Feast feature store.
    """
    store = FeatureStore(repo_path=repo_dir)
    # connect stdout to current process stdout
    stdout_par = subprocess.PIPE if print__subprocess_output else None
    stderr_par = subprocess.PIPE if print__subprocess_output else None
    result = subprocess.run(["feast", "--chdir", repo_dir, "apply"], stdout=stdout_par, stderr=stderr_par)
    if print__subprocess_output:
        print(result.stdout.decode())
        print(result.stderr.decode())
    return store



# ------------------- SQL Functions -------------------

def insert_data_to_sql(df, table_name: str, engine: Engine):
    """
    Insert data into a SQL table.
    Args:
        df (DataFrame): The data to insert.
        table_name (str): The name of the table.
        engine (Engine): The SQLAlchemy engine object.
    Returns:
        None
    """
    try:
        df.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"Dati inseriti con successo nella tabella '{table_name}'.")
    except Exception as e:
        print(f"Errore durante l'inserimento dei dati: {e}")


def get_data_from_sql(table_name: str, engine, attributes: list = None, conditions: dict = None, start_time: datetime = None, end_time: datetime = None):
    """
    Retrieve data from a SQL table with optional filtering.
    Args:
        table_name (str): The name of the table.
        engine (Engine): The SQLAlchemy engine object.
        attributes (list): List of attributes to select.
        conditions (dict): Conditions for filtering the data.
        start_time (datetime): Start time for filtering.
        end_time (datetime): End time for filtering.
    Returns:
        DataFrame: The retrieved data.
    """
    try:
        where_clauses = []
        if conditions is not None:
            for key, value in conditions.items():
                if isinstance(value, (list, tuple)):
                    values = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in value])
                    where_clauses.append(f"{key} IN ({values})")
                elif isinstance(value, str):
                    where_clauses.append(f"{key} = '{value}'")
                else:
                    where_clauses.append(f"{key} = {value}")
        
        if start_time is not None:
            where_clauses.append(f"timestamp >= '{start_time}'")
        if end_time is not None:
            where_clauses.append(f"timestamp <= '{end_time}'")

        where_clause = " AND ".join(where_clauses)

        if attributes is None:
            query = f"SELECT * FROM {table_name}"
        else:
            query = f"SELECT {', '.join(attributes)} FROM {table_name}"

        if where_clause:
            query += f" WHERE {where_clause}"

        with engine.connect() as connection:
            result = connection.execute(text(query))
            data = result.fetchall()
            df = pd.DataFrame(data, columns=result.keys())
            return df
    except Exception as e:
        print(f"Errore durante il recupero dei dati: {e}")
        return None


def delete_data_from_sql(table_name: str, engine: Engine, conditions: dict = None, start_time: datetime = None, end_time: datetime = None):
    """
    Delete data from a SQL table with optional filtering.
    Args:
        table_name (str): The name of the table.
        engine (Engine): The SQLAlchemy engine object.
        conditions (dict): Conditions for filtering the data to delete.
        start_time (datetime): Start time for filtering.
        end_time (datetime): End time for filtering.
    Returns:
        None
    """
    try:
        where_clauses = []
        if conditions is not None:
            for key, value in conditions.items():
                if isinstance(value, str):
                    where_clauses.append(f"{key} = '{value}'")
                else:
                    where_clauses.append(f"{key} = {value}")
        if start_time is not None:
            where_clauses.append(f"timestamp >= '{start_time}'")
        if end_time is not None:
            where_clauses.append(f"timestamp <= '{end_time}'")
        
        where_clause = " AND ".join(where_clauses)
        query = f"DELETE FROM {table_name}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        print(query)
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                connection.execute(text(query))
                trans.commit()
            except Exception as e:
                trans.rollback()
                raise e
            print(f"Dati eliminati con successo dalla tabella '{table_name}'.")
    except Exception as e:
        print(f"Errore durante l'eliminazione dei dati: {e}")



# ------------------- Online Store Functions -------------------

def insert_data_to_redis(df):
    redis_client = get_redis_client()
    for _, row in df.iterrows():
        key = build_key(row['machineid'], row['kpi'], row['aggregation_type'])
        data = {
            "timestamp": row['timestamp'],
            "value": row['value'],
            "imputation": row['imputation'],
            "anomaly": row['anomaly'],
            "trend_drift": row['trend_drift'],
            "next_days_predictions": row['next_days_predictions'],
            "confidence_interval_lower": row['confidence_interval_lower'],
            "confidence_interval_upper": row['confidence_interval_upper']
        }
        # Serializza e aggiunge il dato alla lista in Redis
        redis_client.rpush(key, pickle.dumps(data))  

    print("Dati inseriti con successo in Redis.")


def get_data_from_redis_with_conditions(conditions):
    redis_client = get_redis_client()
    matching_data = []

    # Estrai tutte le chiavi esistenti in Redis
    all_keys = redis_client.keys('*')

    for key in all_keys:
        # Decodifica la chiave e suddividila nei suoi componenti
        key_str = key.decode('utf-8')
        key_parts = key_str.split(':')

        if len(key_parts) != 3:
            continue  # Ignora chiavi non conformi

        machineid, kpi, aggregation_type = key_parts

        # Verifica se la chiave soddisfa le condizioni
        if ('machineid' in conditions and conditions['machineid'] and machineid not in conditions['machineid']):
            continue
        if ('kpi' in conditions and conditions['kpi'] and kpi not in conditions['kpi']):
            continue
        if ('aggregation_type' in conditions and conditions['aggregation_type'] and aggregation_type not in conditions['aggregation_type']):
            continue

        # Recupera tutti gli elementi della lista associata alla chiave
        raw_data_list = redis_client.lrange(key, 0, -1)

        # Deserializza e aggiungi i dati alla lista dei risultati
        for raw_data in raw_data_list:
            data = pickle.loads(raw_data)
            matching_data.append(data)

    return matching_data


def delete_data_from_redis(conditions):
    redis_client = get_redis_client()
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



# ------------------- Insert New Data in Both -------------------

def insert_new_data(df, table_name, engine):
    """
    Insert new data into both SQL and Redis.
    Args:
        df (DataFrame): The data to insert.
        table_name (str): The name of the SQL table.
        engine (Engine): The SQLAlchemy engine object.
        store (FeatureStore): The Feast feature store.
    Returns:
        None
    """
    #insert_data_to_sql(df, table_name, engine)
    #insert_data_to_redis(df, store, table_name)
    insert_data_to_sql(df, table_name, engine)
    insert_data_to_redis(df, table_name)



# ------------------- utils functions -------------------

def get_redis_client(host='localhost', port=6379, db=0):
    """
    Creates and returns a Redis client instance.
    Args:
        host (str): The hostname of the Redis server. Defaults to 'localhost'.
        port (int): The port number on which the Redis server is listening. Defaults to 6379.
        db (int): The database number to connect to. Defaults to 0.
    Returns:
        redis.StrictRedis: A Redis client instance connected to the specified server and database.
    """
    return redis.StrictRedis(host=host, port=port, db=db, decode_responses=False)

def build_key(machineid: str, kpi: str, aggregation_type: str) -> str:
    return f"{machineid}:{kpi}:{aggregation_type}"















"""

# --------------------- DA ELMINARE PROVE -----------------------
def get_data_from_redis_by_timestamp2(threshold_time: datetime, redis_client):
    # Crea un DataFrame con i dati da inserire
    new_data = {
        "timestamp": [
            datetime.now()
        ],
        "machineid": ['987'],
        "kpi": ['x_acceleration'],
        "aggregation_type": ['min'],
        "value": [1.0],
        "imputation": [True],
        "anomaly": [True],
        "trend_drift": [1],
        "next_days_predictions": [
            [75.5, 75.6, 75.7, 75.8]
        ],
        "confidence_interval_lower": [
            [75.4, 75.5, 75.6, 75.7]
        ],
        "confidence_interval_upper": [
            [75.6, 75.7, 75.8, 75.9]
        ]
    }

    df = pd.DataFrame(new_data)

    # Inserisci i dati in Redis
    insert_data_to_redis3(df, redis_client)

    return "ciaooooo"



def insert_data_to_redis3(df, redis_client):
    
    for _, row in df.iterrows():
        key = build_key(row['machineid'], row['kpi'], row['aggregation_type'])
        
        data = {
            "timestamp": row['timestamp'],
            "value": row['value'],
            "imputation": row['imputation'],
            "anomaly": row['anomaly'],
            "trend_drift": row['trend_drift'],
            "next_days_predictions": row['next_days_predictions'],
            "confidence_interval_lower": row['confidence_interval_lower'],
            "confidence_interval_upper": row['confidence_interval_upper']
        }
        
        # Serializza e aggiunge il dato alla lista in Redis
        redis_client.rpush(key, pickle.dumps(data))  

    print("Dati inseriti con successo in Redis.")


    # Funzione per inserire i dati in Redis
def insert_data_to_redis2(df, feature_view_name):
    redis_client = get_redis_client()
    for _, row in df.iterrows():
        machineid = row['machineid']
        kpi = row['kpi']
        aggregation_type = row['aggregation_type']
        
        key = build_key(machineid, kpi, aggregation_type) # Costruisce la chiave
        
        data = {
            "timestamp": row['timestamp'],
            "value": row['value'],
            "imputation": row['imputation'],
            "anomaly": row['anomaly'],
            "trend_drift": row['trend_drift'],
            "next_days_predictions": row['next_days_predictions'],
            "confidence_interval_lower": row['confidence_interval_lower'],
            "confidence_interval_upper": row['confidence_interval_upper']
        }
        
        # Serializza e inserisci i dati in Redis
        redis_client.set(key, pickle.dumps(data))  # Serializza con pickle e salva in Redis

        # Funzione per estrarre i dati in base a condizioni dinamiche
def get_data_from_redis_with_conditions3(conditions):
    redis_client = get_redis_client()
    matching_data = []
    # Estrai tutte le chiavi esistenti in Redis
    all_keys = redis_client.keys('*')

    # Loop su tutte le chiavi per verificare quelle che soddisfano le condizioni
    for key in all_keys:
        # Estrai i componenti della chiave (machineid, kpi, aggregation_type)
        key_parts = key.decode('utf-8').split(':')
        
        if len(key_parts) == 3:
            machineid, kpi, aggregation_type = key_parts
        else:
            continue  # Se la chiave non ha il formato corretto, salta

        # Verifica se la chiave soddisfa le condizioni
        if (conditions['machineid'] and machineid not in conditions['machineid']):
            continue
        if (conditions['kpi'] and kpi not in conditions['kpi']):
            continue
        if (conditions['aggregation_type'] and aggregation_type not in conditions['aggregation_type']):
            continue

        # Recupera i dati dalla chiave
        raw_data = redis_client.get(key)

        # Se ci sono dati per quella chiave, deserializza e aggiungi ai risultati
        if raw_data:
            data = pickle.loads(raw_data)
            matching_data.append(data)

    # Restituisce i dati che corrispondono alle condizioni
    return matching_data

"""