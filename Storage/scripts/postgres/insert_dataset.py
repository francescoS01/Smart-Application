"""
This script inserts a dataset into a PostgreSQL database. It performs the following steps:
1. Loads the dataset from a specified path.
2. Extracts and processes machine names and types.
3. Inserts machine data into the warehouse.
4. Obtains machine IDs and prepares the data for insertion.
5. Connects to the PostgreSQL database and inserts the data into a specified table.

Usage:
    python insert_dataset.py <dataset_path>

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
    df["time"] = pd.to_datetime(df["time"])

    machine_names = df["name"].unique()
    print(f"Found machine names: {machine_names}")

    machine_types = [
        " ".join(name.split()[:-1]) if name.split()[-1].isdigit() else name
        for name in machine_names
    ]
    lines = [
        name.split()[-1] if name.split()[-1].isdigit() else "0"
        for name in machine_names
    ]

    print("Inserting machine data into the warehouse")
    for machine_id, machine_name, machine_type, line in zip(
        range(len(machine_names)), machine_names, machine_types, lines
    ):
        # warehouse.put_machine_data(
        #     machine_name, machine_type=machine_type, machine_line=line
        # )
        warehouse.put_machine_with_default_id(machine_name, machine_type, line)

    print("Obtaining machine IDs")
    df["id"] = df["name"].apply(lambda x: warehouse.get_machine_data_by_name(x)[0][0])

    # print machine name and id
    for machine_id, machine_name in zip(df["id"].unique(), df["name"].unique()):
        print(f"Machine name: {machine_name}, Machine ID: {machine_id}")

    print("Preparing data for insertion into the database")
    ready_df = (
        df.groupby(["id", "time"])[["kpi", "min", "max", "avg", "sum"]]
        .apply(
            lambda x: x.set_index("kpi")[["min", "max", "avg", "sum"]].to_dict(
                orient="index"
            )
        )
        .reset_index()
        .rename(columns={0: "kpi"})
    )

    ready_df.rename(
        columns={"time": "timestamp", "id": "machineid", "kpi": "measurements"},
        inplace=True,
    )
    ready_df = ready_df[["timestamp", "machineid", "measurements"]]

    def jsonify_without_nan(x):
        json_str = json.dumps(x)
        return json_str.replace("NaN", "null")

    ready_df["measurements"] = ready_df["measurements"].apply(jsonify_without_nan)

    print("Connecting to the PostgreSQL database")
    engine = create_engine(
        f"postgresql+psycopg2://postgres:password@{DB_HOST}:5432/postgres"
    )

    table_name = "sensors_data"
    print(f"Inserting data into the {table_name} table")
    ready_df.to_sql(
        table_name, engine, if_exists="replace", index=False, schema="warehouse"
    )
    print("Data insertion complete")
