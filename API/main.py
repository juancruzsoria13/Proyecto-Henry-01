from fastapi import FastAPI
import pandas as pd
import uvicorn
from sklearn.neighbors import NearestNeighbors
import os
import numpy as np

app = FastAPI()


default_parquet_path = os.path.join("Datos Limpios", "output_games_clean.parquet")
parquet_path = os.getenv("parquet_path", default_parquet_path)
df_games = pd.read_parquet(parquet_path)

@app.get("/")
def read_root():
    return {"Bienvenidos al modelo de recomendacion de steam"}

# Consulta 1
@app.get("/developer/")
def desarrollador(developer: str):
    filtro_developer = df_games[df_games["developer"] == developer]
    cantidad_items = filtro_developer["id"].count()
    
    free_por_año = filtro_developer.groupby("release_date").agg({
        "id": "count",
        'price': lambda x: ((x == 0.00).mean() * 100)
    }).reset_index()
    
    free_por_año.rename(columns={"id": "cantidad_items", "price": "contenido_free", "release_date": "año"}, inplace=True)
    free_por_año["contenido_free"] = free_por_año["contenido_free"].astype(str) + "%"
    
    return free_por_año[["año", "cantidad_items", "contenido_free"]].to_dict(orient="records")






# Modelo de recomendación
df_games_numeric = df_games.select_dtypes(include=[np.number]).fillna(0)
nn_model = NearestNeighbors(metric='cosine', algorithm='brute')
nn_model.fit(df_games_numeric)

# Función para obtener las recomendaciones de juegos similares a uno dado
@app.get("/juego/")
def recomendacion_juego(product_name: str):
    try:
        idx = df_games.index[df_games['app_name'] == product_name].tolist()[0]
        distances, indices = nn_model.kneighbors([df_games_numeric.iloc[idx]], n_neighbors=6)
        similar_product_names = [df_games.iloc[i]['app_name'] for i in indices.flatten()[1:]]
        return similar_product_names
    except IndexError:
        raise ValueError("El nombre de juego proporcionado no se encuentra en el DataFrame")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

