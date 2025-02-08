import os
import psycopg2
from dotenv import load_dotenv, dotenv_values
import requests
import json

# load the .env
load_dotenv()

# API connection
url = 'https://www.wikiart.org/en/App/Painting/MostViewedPaintings?randomSeed=123&json=2'

def api_connection(url):
    res = requests.get(
        url,
        headers={ "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )

    if res.status_code == 200:
        output = res.json()
        print(output[0])
    else:
        print("Error!", res.status_code)

api_connection(url)



# create an object for the database connection 
db_params = {
    "dbname": os.getenv("DBNAME"),
    "user": "default",
    "password": os.getenv("PASSWORD"),
    "host": os.getenv("HOST"),
    "port": os.getenv("PORT")
}

def db_connection(db_params):
    try:
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        cursor.execute("SELECT * from artwork WHERE title = 'Moses';")
        
        for record in cursor:
            print(record)


    except (psycopg2.Error) as error:
        print(f"error connecting to postgresql database: {error}")

    finally:
        print("database connection closed.")

#db_connection(db_params)
