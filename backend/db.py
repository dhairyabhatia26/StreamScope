import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv(dotenv_path=".env")

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        autocommit=True,
    )
