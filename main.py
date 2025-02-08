import os
import psycopg2
from dotenv import load_dotenv, dotenv_values
import requests

# load the .env
load_dotenv()

# API connection
url_popular_art = 'https://www.wikiart.org/en/App/Painting/MostViewedPaintings?randomSeed=123&json=2'

def api_connection(url_popular_art):
    res = requests.get(
        url_popular_art,
        headers={ "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
    res.raise_for_status()
    return res.json()[0]


# create an object for the database connection 
db_params = {
    "dbname": os.getenv("DBNAME"),
    "user": "default",
    "password": os.getenv("PASSWORD"),
    "host": os.getenv("HOST"),
    "port": os.getenv("PORT")
}

def insert_artwork(db_params, artwork_data):
    try:
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        query = """INSERT INTO artwork (
            content_id, title, artist_content_id, 
            artist_name, completition_year,
            year_as_string, width, image, height
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (content_id) DO UPDATE SET
                title = EXCLUDED.title,
                artist_content_id = EXCLUDED.artist_content_id,
                artist_name = EXCLUDED.artist_name,
                completition_year = EXCLUDED.completition_year,
                year_as_string = EXCLUDED.year_as_string,
                width = EXCLUDED.width,
                image = EXCLUDED.image,
                height = EXCLUDED.height
                        """
        
        values = (
            artwork_data.get('contentId'),
            artwork_data.get('title'),
            artwork_data.get('artistContentId'),
            artwork_data.get('artistName'),
            artwork_data.get('completitionYear'),
            artwork_data.get('yearAsString'),
            artwork_data.get('width'),
            artwork_data.get('image'),
            artwork_data.get('height')
        )

        cursor.execute(query, values)
        conn.commit()
        print("Data inserted successfully!")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except requests.RequestException as e:
        print(f"API request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        artwork = api_connection(url_popular_art)

        print("\nRecieved artwork data:")
        for key, value in artwork.items():
            print(f"{key}: {value}")

        insert_artwork(db_params, artwork)

    except Exception as e:
        print(f"Main execution error: {e}")
