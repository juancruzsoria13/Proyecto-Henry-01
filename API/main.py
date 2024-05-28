from fastapi import FastAPI, Query
import pandas as pd
import uvicorn
import os

app = FastAPI()

@app.get("/")
def mensaje():
    return {"mensaje": "Bienvenido a la API de datos de steam"}


default_parquet_path = r"C:\Users\juanc.DESKTOP-LGMDQP1\OneDrive\Documentos\Proyecto Henry 01\Datos Limpios\output_games_clean.parquet"
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
