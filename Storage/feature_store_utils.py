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


def get_filtered_online_features(store, feature_view_name, attributes, conditions):
    """
    Retrieve filtered online features from the feature store.

    Args:
        store (FeatureStore): The Feast feature store.
        feature_view_name (str): The name of the feature view.
        attributes (list): List of attributes to retrieve.
        conditions (dict): Conditions for filtering the features.

    Returns:
        DataFrame: The retrieved features.
    """
    if not all(key in conditions for key in ['machineid', 'kpi', 'aggregation_type']):
        raise ValueError("Le condizioni devono includere 'machineid', 'kpi' e 'aggregation_type'.")

    # Genera combinazioni cartesiane di tutte le condizioni specificate
    entity_rows = [
        {"machineid": machineid, "kpi": kpi, "aggregation_type": aggregation_type}
        for machineid, kpi, aggregation_type in product(conditions['machineid'], conditions['kpi'], conditions['aggregation_type'])
    ]

    # Funzione per ottenere i dati online dalla store
    def get_online_features_from_view(store, feature_view_name, attributes, entity_rows):
        attributes_with_prefix = [f"{feature_view_name}:{attribute}" for attribute in attributes]
        returned_features = store.get_online_features(
            features=attributes_with_prefix,
            entity_rows=entity_rows
        ).to_dict()

        df = pd.DataFrame(returned_features)
        df.columns = [col.replace(f"{feature_view_name}:", "") for col in df.columns]

        return df

    # 1. Prova a ottenere i dati dalla fresh feature view
    fresh_df = get_online_features_from_view(store, f"{feature_view_name}_fresh", attributes, entity_rows)

    # 2. Controlla se ci sono valori None o NaN negli attributi
    if fresh_df[attributes].isnull().any().any():
        tz = pytz.timezone('Europe/Rome')
        store.materialize(start_date=datetime.now(tz) - timedelta(hours=2), end_date=datetime.now(tz))
        historical_df = get_online_features_from_view(store, feature_view_name, attributes, entity_rows)
        return historical_df

    return fresh_df




import pandas as pd
from feast import FeatureStore


from feast import FeatureStore
import pandas as pd

def read_data_from_redis(store, feature_view_name, entity_df):
    """
    Leggi i dati da Redis per la feature view e le entità specificate.

    Args:
        store (FeatureStore): Il Feature Store di Feast.
        feature_view_name (str): Il nome della feature view.
        entity_df (DataFrame): Il DataFrame con le entità da interrogare.

    Returns:
        DataFrame: I dati letti da Redis per la feature view richiesta.
    """
    # Esegui la lettura delle feature online per la feature view
    online_features = store.get_online_features(
        features=[
            f"{feature_view_name}:value",              # Feature "value" per historical_store
            f"{feature_view_name}:imputation",         # Feature "imputation"
            f"{feature_view_name}:anomaly",            # Feature "anomaly"
            f"{feature_view_name}:trend_drift",        # Feature "trend_drift"
            f"{feature_view_name}:next_days_predictions",   # Feature "next_days_predictions"
            f"{feature_view_name}:confidence_interval_lower",  # Feature "confidence_interval_lower"
            f"{feature_view_name}:confidence_interval_upper"   # Feature "confidence_interval_upper"
        ],
        entity_df=entity_df
    ).to_df()

    return online_features




def insert_data_to_redis(df, store, feature_view_name):
    """
    Insert data into Redis for online feature serving.

    Args:
        df (DataFrame): The data to insert.
        store (FeatureStore): The Feast feature store.
        feature_view_name (str): The name of the feature view.

    Returns:
        None
    """
    store.push(f"{feature_view_name}_push_source", df, to=PushMode.ONLINE)









def insert_new_data(df, table_name: str, engine: Engine, store):
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
    insert_data_to_sql(df, table_name, engine)
    insert_data_to_redis(df, store, table_name)