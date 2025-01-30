"""
This script clones the raw data from the database to the preprocessed data for fast testing
Execute after insert_dataset.py on a clean volume
Usage:
    python clone_raw_to_prerpocessed.py <dataset_path>

Arguments:
    dataset_path: Path to the dataset file (pickle format).
"""

import pandas as pd
import Storage.warehouse as warehouse
from sqlalchemy import create_engine
import json
import argparse
import os

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insert dataset into database")
    parser.add_argument("dataset", type=str, help="Dataset path")
    args = parser.parse_args()

    print(f"Loading dataset from {args.dataset}")
    df = pd.read_pickle(args.dataset)
    MACHINE_NAME_TO_ID = {
        "Large Capacity Cutting Machine 1": 1,
        "Riveting Machine" : 2,
        "Medium Capacity Cutting Machine 1": 3,
        "Laser Cutter": 4,
        "Large Capacity Cutting Machine 2": 5,
        "Medium Capacity Cutting Machine 2": 6,
        "Testing Machine 1": 7,
        "Testing Machine 2": 8,
        "Low Capacity Cutting Machine 1": 9,
        "Medium Capacity Cutting Machine 3": 10,
        "Assembly Machine 1": 11,
        "Laser Welding Machine 1": 12,
        "Assembly Machine 2": 13,
        "Assembly Machine 3": 14,
        "Laser Welding Machine 2": 15,
        "Testing Machine 3": 16
    }
    df['machineid'] = df['name'].apply(lambda x: MACHINE_NAME_TO_ID[x])
    df.drop(columns=['asset_id'], inplace=True)
    df.drop(columns=['name'], inplace=True)
    # rename columns
    df.rename(columns={'time': 'timestamp'}, inplace=True)
    df['timestamp'] = df['timestamp'].apply(lambda x: x.replace('T', ' ').replace('Z', ''))
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df['imputation'] = False
    df['anomaly'] = False
    df['next_days_predictions'] = None
    df['confidence_interval_lower'] = None
    df['confidence_interval_upper'] = None
    df['trend drift'] = 0.0
    df_sum = df.drop(columns=['avg', 'min', 'max'])
    df_sum.rename(columns={'sum': 'value'}, inplace=True)
    df_sum['aggregation_type'] = 'sum'
    df_max = df.drop(columns=['avg', 'min', 'sum'])
    df_max.rename(columns={'max': 'value'}, inplace=True)
    df_max['aggregation_type'] = 'max'
    df_min = df.drop(columns=['avg', 'max', 'sum'])
    df_min.rename(columns={'min': 'value'}, inplace=True)
    df_min['aggregation_type'] = 'min'
    df_avg = df.drop(columns=['min', 'max', 'sum'])
    df_avg.rename(columns={'avg': 'value'}, inplace=True)
    df_avg['aggregation_type'] = 'avg'
    # merge all dataframes
    df = pd.concat([df_sum, df_max, df_min, df_avg])

    print("Connecting to the PostgreSQL database")
    engine = create_engine(
        f"postgresql+psycopg2://postgres:password@{DB_HOST}:5432/postgres"
    )

    table_name = "historical_store"
    print(f"Inserting data into the {table_name} table")
    df.to_sql(
        table_name, engine, if_exists="replace", index=False
    )
    print("Data insertion complete")
