import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

def preprocessing_data():
    df = pd.read_csv("games_dataset.csv", delimiter=";")

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

def train_model():
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

def predict_score(price=None, release_month=None, tags=None, genres=None, platforms=None):
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

pred = predict_score(20, 2, ["RPG", "Indie"], ["Adventure"])
print(f"Score estimado: {pred:.2f}/100")
