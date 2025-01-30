#!/bin/bash
docker-compose -f "./API Layer/docker-compose.yml" up -d
docker-compose -f "./Storage/docker-compose.yml" up -d
docker-compose -f "./Data-Processing/docker-compose.yml" up -d
docker-compose -f "./KB-database/docker-compose.yml" up -d
docker-compose -f "./Kpi Engine/docker-compose.yml" up -d
docker-compose -f "./RAG/docker-compose.yml" up -d
docker-compose -f "./Security, Privacy and Explainability/Milestone 3/docker-compose.yml" up -d