
# Strartup and data insertion

To build and run all containers of the system, execute the script `build_and_run.sh` from the root directory of the project. This script will build the docker images and run the containers in detached mode. The script can be executed with the following command:

```bash
./build_and_run.sh
```
If not on a Unix system, the script commands can still be executed manually.

After the containers are running, to insert the initial data into the database, execute the script `add_data_to_db.sh` from the root directory of the project. This script will insert the initial data into the database. The script can be executed with the following command:

```bash
./add_data_to_db.sh
```

# Documentations

The various topic folders contain more specific documentations and readme files.