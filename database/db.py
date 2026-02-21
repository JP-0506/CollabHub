import psycopg2


def get_db():

    return psycopg2.connect(
        dbname="CollabHub1",  # your database name
        user="postgres",  # your username
        password="0506",  # your password
        host="localhost",
        port="5432",
    )
