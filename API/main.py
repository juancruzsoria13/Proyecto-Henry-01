from fastapi import FastAPI, Query
import pandas as pd
import uvicorn
import os
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import numpy as np

app = FastAPI()

@app.get("/")
def mensaje():
    return {"mensaje": "Bienvenido a la API de datos de steam"}


default_parquet_path = os.path.join("Datos Limpios", "output_games_clean.parquet")
parquet_path = os.getenv("parquet_path", default_parquet_path)

# Consulta 1
@app.get("/developer/")
def desarrollador(developer: str):
    df = pd.read_parquet(parquet_path)
    filtro_developer = df[df["developer"] == developer]
    cantidad_items = filtro_developer["id"].count()
    
    free_por_año = filtro_developer.groupby("release_date").agg({
        "id": "count",
        'price': lambda x: ((x == 0.00).mean() * 100)
    }).reset_index()
    
    free_por_año.rename(columns={"id": "cantidad_items", "price": "contenido_free", "release_date": "año"}, inplace=True)
    free_por_año["contenido_free"] = free_por_año["contenido_free"].astype(str) + "%"
    
    return free_por_año[["año", "cantidad_items", "contenido_free"]].to_dict(orient="records")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)






#Modelo de recomendacion

df_games= pd.read_parquet(parquet_path)
# Manejo de valores faltantes: rellenar con cero o eliminar las filas con valores faltantes
df_games_numeric = df_games.select_dtypes(include=[np.number]).fillna(0)  # Rellenar con cero

# Inicializar el modelo NearestNeighbors
nn_model = NearestNeighbors(metric='cosine', algorithm='brute')  # Utilizando la distancia coseno

# Entrenar el modelo
nn_model.fit(df_games_numeric)

# Función para obtener las recomendaciones de juegos similares a uno dado
@app.get("/juego/")
def recomendacion_juego(product_name):
    try:
        # Obtener el índice del producto en el DataFrame
        idx = df_games.index[df_games['app_name'] == product_name].tolist()[0]
        # Calcular las distancias y los índices de los vecinos más cercanos
        distances, indices = nn_model.kneighbors([df_games_numeric.iloc[idx]], n_neighbors=6)  # Excluimos el propio juego y tomamos los 5 más similares
        # Obtener los nombres de los juegos más similares
        similar_product_names = [df_games.iloc[i]['app_name'] for i in indices.flatten()[1:]]  # Excluimos el propio juego
        return similar_product_names
    except IndexError:
        raise ValueError("El nombre de juego proporcionado no se encuentra en el DataFrame")


