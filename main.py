import os
import psycopg2
from dotenv import load_dotenv, dotenv_values
import requests
import json

# load the .env
load_dotenv()

# WikiArt API urls
url_popular_art = 'https://www.wikiart.org/en/App/Painting/MostViewedPaintings?randomSeed=123&json=2'
url_artwork_data = 'http://www.wikiart.org/en/App/Painting/ImageJson/'
headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"} 

def popular_artworks(url_popular_art):
    res = requests.get(
        url_popular_art,
        headers = headers
        )
    res.raise_for_status()
    return res.json()


def artwork_details(contentId):
    res = requests.get(
        url_artwork_data + str(contentId),
        headers = headers
        )
    res.raise_for_status()
    return res.json()



# create an object for the database connection 
db_params = {
    "dbname": os.getenv("DBNAME"),
    "user": "default",
    "password": os.getenv("PASSWORD"),
    "host": os.getenv("HOST"),
    "port": os.getenv("PORT")
}

def insert_artwork(db_params, artwork_data, correct_artist_name):
    try:
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        query = """ INSERT INTO artwork (
                content_id, title, artist_content_id, artist_name,
                completition_year, year_as_string, width, height,
                image, artist_url, url, genre, style, material,
                technique, location, period, serie, gallery_name,
                auction, year_of_trade, last_price, dictionaries,
                description, tags, diameter, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, NOW(), NOW()
            )
            ON CONFLICT (content_id) DO UPDATE SET
                title = EXCLUDED.title,
                artist_content_id = EXCLUDED.artist_content_id,
                artist_name = EXCLUDED.artist_name,
                completition_year = EXCLUDED.completition_year,
                year_as_string = EXCLUDED.year_as_string,
                width = EXCLUDED.width,
                height = EXCLUDED.height,
                image = EXCLUDED.image,
                artist_url = EXCLUDED.artist_url,
                url = EXCLUDED.url,
                genre = EXCLUDED.genre,
                style = EXCLUDED.style,
                material = EXCLUDED.material,
                technique = EXCLUDED.technique,
                location = EXCLUDED.location,
                period = EXCLUDED.period,
                serie = EXCLUDED.serie,
                gallery_name = EXCLUDED.gallery_name,
                auction = EXCLUDED.auction,
                year_of_trade = EXCLUDED.year_of_trade,
                last_price = EXCLUDED.last_price,
                dictionaries = EXCLUDED.dictionaries,
                description = EXCLUDED.description,
                tags = EXCLUDED.tags,
                diameter = EXCLUDED.diameter,
                updated_at = NOW()
                """
        
        values = (
        artwork_data.get('contentId'),
            artwork_data.get('title'),
            artwork_data.get('artistContentId'),
            correct_artist_name,
            artwork_data.get('completitionYear'),
            artwork_data.get('yearAsString'),
            artwork_data.get('width'),
            artwork_data.get('height'),
            artwork_data.get('image'),
            artwork_data.get('artistUrl'),
            artwork_data.get('url'),
            artwork_data.get('genre'),
            artwork_data.get('style'),
            artwork_data.get('material'),
            artwork_data.get('technique'),
            artwork_data.get('location'),
            artwork_data.get('period'),
            artwork_data.get('serie'),
            artwork_data.get('galleryName'),
            artwork_data.get('auction'),
            artwork_data.get('yearOfTrade'),
            artwork_data.get('lastPrice'),
            json.dumps(artwork_data.get('dictionaries', [])),  # Convert list to JSON
            artwork_data.get('description'),
            artwork_data.get('tags'),
            artwork_data.get('diameter'),
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
        artworks = popular_artworks(url_popular_art)

        print("\nData insertion start")
        for artwork in artworks:
             # Get the correct artist name from the popular artworks list
            correct_artist = artwork.get('artistName')
            
            # Fetch detailed information
            artwork_detailed = artwork_details(artwork.get('contentId'))
            
            # Add a fallback to the correct artist name
            artwork_detailed['artistName'] = correct_artist  # Override with correct name
            
            # Pass both the detailed data and correct artist name
            insert_artwork(db_params, artwork_detailed, correct_artist)

            for key, value in artwork.items():
                print(f"{key}: {value}")

       

    except Exception as e:
        print(f"Main execution error: {e}")
