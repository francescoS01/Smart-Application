# How to start the storage system with docker

> **Note:** Make sure Docker is installed on your system. You can download and install Docker from [here](https://www.docker.com/get-started).

You can directly start the database infrastructure by running in the `Storage` directory:

```sh
docker-compose up --build -d
```

Alternatively, build the Docker image `Warehouse.Dockerfile`:

```sh
docker build -t my-postgres-db -f Warehouse.Dockerfile .
```

And the Docker image for `kafka-to-warehouse.Dockerfile`, use the following command:

```sh
docker build -t kafka-to-warehouse -f kafka-to-warehouse.Dockerfile .
```

> **Note:** The above Docker commands must be executed in the `Storage` directory.

To start the storage system using `docker-compose`, follow these steps:

1. Run the following command to start the services defined in the `docker-compose.yml` file:
    ```sh
    docker-compose up -d
    ```

2. To stop the services, use the following command:
    ```sh
    docker compose down
    ```

> **Note:** The above Docker commands must be executed in the `Storage` directory.

To create a virtual environment with Python and install the required libraries from `requirements.txt`, follow these steps:

1. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

2. Activate the virtual environment:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```sh
        source venv/bin/activate
        ```

3. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```

4. To deactivate the virtual environment, use the following command:
    ```sh
    deactivate
    ```

> **Note:** The above Python-related commands should be executed outside the `Storage` directory.

To simulate a machine sending data, you can execute the `producer_v2.py` script:

```sh
python -m Storage.scripts.prodcons.producer_v2
```

> **Note:** Use `--help` to understand what `producer_v2` does.

> **Note:** Use the command outside the `Storage` directory

> **Note:** In the `scripts/prodcons` directory there are other scripts for alerts, but they are not used by the system (alerts get inserted directly by the API layer). Other scripts are deprecated.

Inside the `scripts/postgres`directory there are utility or startup scripts for the PostgreSQL database. `Populate.sql` and `Depopulate.sql` are used for tests. `insert_dataset.py` is used to insert the dataset data into the data warehouse. `1-create-tables` is automatically when starting the database for the first time.

# Database Schema and Feature Store

The database schema for the PostgreSQL database is defined in the `1-create-tables.sql` file. This file is executed automatically when starting the database for the first time. You can find this file in the `Storage/scripts/postgres` directory.

The features for the feature store are defined in the `example_repo.py` file. This file contains all the feature definitions used by the system. You can find this file in the `Storage/postgres_store` directory.

# How to run tests

The tests for this project were created using `pytest` and are located in the `Storage/tests` directory. To run the tests, follow these steps:

1. Ensure that the virtual environment is activated (refer to the steps above).

2. Run the tests using the following command:
    ```sh
    pytest <path-to-tests>
    ```

The tests are all present in the `Storage/tests` directory.

# Tutorials

For a comprehensive guide on using the warehouse, refer to the `Tutorial.ipynb` notebook. This notebook provides step-by-step instructions and examples on how to interact with the data warehouse. You can find this file in the `Storage` directory.

For a detailed tutorial on the feature store, refer to the `FeatureStoreNotebook.ipynb` notebook. This notebook covers how to define and use features within the feature store. You can find this file in the `Storage` directory.

