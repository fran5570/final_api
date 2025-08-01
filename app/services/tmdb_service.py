import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")

def fetch_movie_by_id(tmdb_id: int):
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY, "language": "es-ES"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def fetch_popular_movies():
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {"api_key": TMDB_API_KEY, "language": "es-ES", "page": 1}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("results", [])

def search_movies(query: str):
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {"api_key": TMDB_API_KEY, "language": "es-ES", "query": query, "page": 1}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("results", [])
