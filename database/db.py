import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db():

    try:

        # If DATABASE_URL exists (Render or .env)
        database_url = os.getenv("DATABASE_URL")

        if database_url:

            return psycopg2.connect(database_url)

        # Fallback for local PostgreSQL
        return psycopg2.connect(
            dbname="CollabHub1",
            user="postgres",
            password="0506",
            host="localhost",
            port="5432",
        )

    except Exception as e:

        print("Database Connection Error:", e)

        return None