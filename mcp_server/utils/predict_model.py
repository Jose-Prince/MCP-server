import os
from pathlib import Path
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

from utils.game import create_gameList

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "games_dataset.csv"

df = None
mlb_tags = None
mlb_genres = None
mlb_platforms = None
model = None

def setup_model():
    global df, mlb_tags, mlb_genres, mlb_platforms, model

    if not CSV_PATH.exists():
        print("[INFO] games_dataset.csv not found. Creating dataset...")
        create_gameList()

    df = pd.read_csv(CSV_PATH, delimiter=";")

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["release_month"] = df["release_date"].dt.month.fillna(0).astype(int)

    df["tags"] = df["tags"].fillna("").apply(lambda x: x.split(";") if x else [])
    df["genres"] = df["genres"].fillna("").apply(lambda x: x.split(";") if x else [])
    df["platforms"] = df["platforms"].fillna("").apply(lambda x: x.split(";") if x else [])

    mlb_tags = MultiLabelBinarizer()
    mlb_genres = MultiLabelBinarizer()
    mlb_platforms = MultiLabelBinarizer()

    tags_encoded = mlb_tags.fit_transform(df["tags"])
    genres_encoded = mlb_genres.fit_transform(df["genres"])
    platforms_encoded = mlb_platforms.fit_transform(df["platforms"])

    X = np.hstack([
        df[["price", "release_month"]].values,
        tags_encoded,
        genres_encoded,
        platforms_encoded,
        df[["ccu", "recommendations", "average_forever", "average_2weeks", "median_forever", "median_2weeks"]].fillna(0).values
    ])

    y = df["score"].fillna(df["score"].mean())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)


def predict_score(price=None, release_month=None, tags=None, genres=None, platforms=None):
    global df, mlb_tags, mlb_genres, mlb_platforms, model

    if model is None:
        raise RuntimeError("El modelo no está entrenado. Llama a setup_model() primero.")

    if price is None:
        price = df["price"].median()
    if release_month is None:
        release_month = 0
    if tags is None:
        tags = []
    if genres is None:
        genres = []
    if platforms is None:
        platforms = []

    tags_vector = mlb_tags.transform([tags])
    genres_vector = mlb_genres.transform([genres])
    platforms_vector = mlb_platforms.transform([platforms])

    extras = [0, 0, 0, 0, 0, 0]

    X_new = np.hstack([[price, release_month], tags_vector[0], genres_vector[0], platforms_vector[0], extras])
    return model.predict([X_new])[0]

