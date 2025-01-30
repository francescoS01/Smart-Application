import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",              
        user=os.getenv("root"),   #your system database username
        password=os.getenv("####"), # your system database password
        database=os.getenv("tokens_db")
    )

def save_token(user_id, token_hash, expiration):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tokens (user_id, token_hash, expiration)
                VALUES (%s, %s, %s)
                """,
                (user_id, token_hash, expiration),
            )
        conn.commit()
    finally:
        conn.close()
