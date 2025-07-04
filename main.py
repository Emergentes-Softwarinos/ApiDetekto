from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from ultralytics import YOLO
import shutil
import os
import uuid
import mysql.connector
from typing import Optional

# Conexión a la base de datos
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="12345678",
    database="detecciones_db",
    port=3306,
)
cursor = conn.cursor()

app = FastAPI(
    title="API de Detección de Objetos",
    description="Sube una imagen para detectar objetos con YOLO y descarga la imagen procesada.",
    version="1.0.0",
)

# Cargar modelo
modelo = YOLO("Herramientas_model/entrenamiento_herramientas/weights/best.pt")

# Crear directorio de salida si no existe
os.makedirs("imagenes_salida", exist_ok=True)


@app.post("/detectar/", response_class=FileResponse)
async def detectar_objeto(imagen: UploadFile = File(...)):
    id_img = str(uuid.uuid4())
    ruta_entrada = f"temp_{id_img}.jpg"
    ruta_salida = f"imagenes_salida/predict_{id_img}.jpg"

    with open(ruta_entrada, "wb") as f:
        shutil.copyfileobj(imagen.file, f)

    resultados = modelo.predict(
        source=ruta_entrada,
        save=True,
        project="imagenes_salida",
        name=f"predict_{id_img}",
        exist_ok=True,
    )

    # Obtener clase detectada (solo la primera si hay varias)
    clase_detectada: Optional[str] = None
    if resultados and resultados[0].boxes and resultados[0].boxes.cls.numel() > 0:
        clase_detectada = float(resultados[0].boxes.cls[0])
    else:
        clase_detectada = "sin detección"

    # Buscar la imagen procesada
    carpeta_prediccion = f"imagenes_salida/predict_{id_img}"
    archivos_generados = os.listdir(carpeta_prediccion)
    if archivos_generados:
        imagen_procesada = os.path.join(carpeta_prediccion, archivos_generados[0])
    else:
        return {"error": "No se generó ninguna imagen"}

    # Guardar en base de datos
    cursor.execute(
        "INSERT INTO detecciones (nombre_archivo, clase_detectada, ruta_imagen) VALUES (%s, %s, %s)",
        (imagen.filename, str(clase_detectada), imagen_procesada),
    )
    conn.commit()

    return FileResponse(
        path=imagen_procesada,
        filename=f"resultado_{imagen.filename}",
        media_type="image/jpeg",
    )


@app.get("/ultima-imagen", response_class=FileResponse)
def obtener_ultima_imagen():
    cursor.execute("SELECT ruta_imagen FROM detecciones ORDER BY id DESC LIMIT 1")
    resultado = cursor.fetchone()

    if not resultado:
        return {"error": "No hay imágenes registradas"}

    ruta_imagen = resultado[0]

    if not os.path.exists(ruta_imagen):
        return {"error": "La imagen no se encuentra en el sistema"}

    return FileResponse(
        path=ruta_imagen, media_type="image/jpeg", filename="ultima_deteccion.jpg"
    )
