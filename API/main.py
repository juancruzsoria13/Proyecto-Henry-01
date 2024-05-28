from fastapi import FastAPI
import pandas as pd


app= FastAPI()

@app.get("/")

def mensaje():
    return ("Bienvenido a la API de datos de steam")
#Consulta 1
@app.get("/developer/")




def desarrollador(developer:str):
    df = pd.read_parquet(r'C:\Users\juanc.DESKTOP-LGMDQP1\OneDrive\Documentos\Proyecto Henry 01\Datos Limpios\output_games_clean.parquet')
    filtro_developer= df[df["developer"] == developer]
    cantidad_items=filtro_developer["id"].count()
    free_por_año= filtro_developer.groupby("release_date").agg({
        "id": "count",
        'price': lambda x: ((x == 0.00).mean() * 100)
        
    }).reset_index()
    free_por_año.rename(columns={"id":"cantidad_items"},inplace=True)
    free_por_año.rename(columns={"price":"contenido_free"},inplace=True)
    free_por_año.rename(columns={"release_date":"año"},inplace=True)
    free_por_año[["año","cantidad_items","contenido_free"]]
    free_por_año["contenido_free"]=free_por_año["contenido_free"].astype(str) + "%"
    
    return free_por_año


developer=input("Ingrese el desarrollador")
desarrollador(developer)