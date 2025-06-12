## sql.py
import os
import json
import psycopg2
from dotenv import load_dotenv
from config.logger_config import logger

load_dotenv()

def store_transformed(data):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT")
        )
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (user_id, personal, location, professional, bank, net)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["user_id"],
            json.dumps(data["personal"]),
            json.dumps(data["location"]),
            json.dumps(data["professional"]),
            json.dumps(data["bank"]),
            json.dumps(data["net"])
        ))

        conn.commit()
        logger.info(f"✅ Datos almacenados en PostgreSQL para user_id: {data['user_id']}")
    except Exception as e:
        logger.error(f"❌ Error insertando en PostgreSQL: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()