docker cp formula-update.sql kb-database-kb-1:./
docker exec -it kb-database-kb-1 psql -U postgres -h localhost -p 5432 -f formula-update.sql
\q
exit

