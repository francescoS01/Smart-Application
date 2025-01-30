#!/bin/bash
docker build -t insert-db -f "./Storage/insert_db.Dockerfile" './Storage/'
docker run --network db-network insert-db