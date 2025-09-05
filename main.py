import steamspypi
import requests
import csv
import time
import dotenv
import os
from dotenv import load_dotenv

from game import Game

load_dotenv()

API_KEY_RAWG = os.getenv("RAWG_KEY")
games_list = []

def get_rawg_platforms(name):
    url = f"https://api.rawg.io/api/games?search={name}&key={API_KEY_RAWG}"
    try:
        r = requests.get(url, timeout=10).json()
        if "results" in r and len(r["results"]) > 0:
            platforms = [p["platform"]["name"] for p in r["results"][0].get("platforms", [])]
            return platforms
    except Exception as e:
        print(f"Error RAWG {name}: {e}")
    return []

def get_rawg_data(game_name):
    """
    Busca un juego en RAWG por nombre y devuelve el primer resultado completo
    con información relevante, incluyendo rating y plataformas.
    """
    url = f"https://api.rawg.io/api/games"
    params = {
        "key": API_KEY_RAWG,
        "search": game_name,
        "page_size": 1  # solo necesitamos el primer resultado
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "results" in data and len(data["results"]) > 0:
            return data["results"][0]  # retorna el primer juego encontrado
        else:
            return None
    except requests.RequestException as e:
        print(f"[RAWG ERROR] {game_name}: {e}")
        return None

def get_steam_store(appid):
    """Obtiene datos desde la Steam Store"""
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    try:
        r = requests.get(url, timeout=10).json()
        if r[str(appid)]["success"]:
            return r[str(appid)]["data"]
    except Exception as e:
        print(f"Error SteamStore {appid}: {e}")
    return None

def get_steamspy(appid):
    """Obtiene datos desde SteamSpy"""
    url = f"https://steamspy.com/api.php?request=appdetails&appid={appid}"
    try:
        return requests.get(url, timeout=10).json()
    except Exception as e:
        print(f"Error SteamSpy {appid}: {e}")
    return None

# 🔹 Obtener lista de juegos desde SteamSpy
params = {'request': 'all', 'page': '0'}
games = steamspypi.download(params)

# 🔹 Iterar sobre algunos juegos (ejemplo: primeros 50)
for idx, appid in enumerate(games.keys()):
    if idx >= 5:
        break

    steamspy_data = get_steamspy(appid)
    store_data = get_steam_store(appid)

    if not steamspy_data or not store_data:
        continue

    # Saltar si no es un juego
    if store_data.get("type") != "game":
        continue

    name = store_data.get("name", "")
    price = store_data.get("price_overview", {}).get("final", 0) / 100
    genre = steamspy_data.get("genre", "")
    platforms = get_rawg_platforms(name)

    # Datos de SteamSpy
    avg_forever = steamspy_data.get("average_forever", 0)
    avg_2weeks = steamspy_data.get("average_2weeks", 0)
    med_forever = steamspy_data.get("median_forever", 0)
    med_2weeks = steamspy_data.get("median_2weeks", 0)
    ccu = steamspy_data.get("ccu", 0)
    tags = list(steamspy_data.get("tags", {}).keys())

    # Datos de Steam Store
    genres = [g["description"] for g in store_data.get("genres", [])]
    release_date = store_data.get("release_date", {}).get("date", "")

    score = None
    if "metacritic" in store_data and store_data["metacritic"]:
        score = store_data["metacritic"].get("score", None)
    else:
        rawg_data = get_rawg_data(name)
        if rawg_data:
            rawg_rating = rawg_data.get("rating", None)
            if rawg_rating is not None:
                score = int(rawg_rating * 20)

    recommendations = store_data.get("recommendations", {}).get("total", 0)

    # Crear instancia Game
    game_obj = Game(name, price, genre, platforms, avg_forever, avg_2weeks,
                    med_forever, med_2weeks, ccu, genres, tags, score,
                    release_date, recommendations)

    games_list.append(game_obj)

    print(f"[{idx}] {name} agregado ✔")
    time.sleep(1)  # evitar rate limit

with open("games_dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow([
        "name", "price", "genre", "platforms", "average_forever",
        "average_2weeks", "median_forever", "median_2weeks", "ccu",
        "genres", "tags", "score", "release_date", "recommendations"
    ])
    for g in games_list:
        writer.writerow([
            g.name,
            g.price,
            g.genre,
            ";".join(g.platforms) if isinstance(g.platforms, list) else g.platforms,
            g.average_forever,
            g.average_2weeks,
            g.median_forever,
            g.median_2weeks,
            g.ccu,
            ";".join(g.genres) if isinstance(g.genres, list) else g.genres,
            ";".join(g.tags) if isinstance(g.tags, list) else g.tags,
            g.score,
            g.release_date,
            g.recommendations
        ])
