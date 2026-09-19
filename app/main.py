import os
from fastapi import FastAPI, HTTPException
import pymongo
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI(
    title="Diplomado BD API - Proyecto MongoDB Atlas CI/CD",
    description="API REST transaccional y analítica integrada con MongoDB Atlas y GitHub Actions",
    version="2.0.0",
)


def get_db():
    if not MONGO_URI:
        raise HTTPException(status_code=500, detail="MONGO_URI no configurado")
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client, client["ventas_db"]


@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenido al Proyecto de Arquitectura de Datos MongoDB Atlas - Diplomado BD",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    try:
        client, db = get_db()
        client.admin.command('ping')
        client.close()
        return {"status": "healthy", "database": "connected", "service": "diplomado-bd-api"}
    except Exception as e:
        return {"status": "degraded", "database": str(e), "service": "diplomado-bd-api"}


@app.get("/api/stats")
def get_database_stats():
    try:
        client, db = get_db()
        stats = {
            "clientes": db.clientes.count_documents({}),
            "productos": db.productos.count_documents({}),
            "ventas_oltp": db.ventas.count_documents({}),
            "ventas_olap": db.ventas_analiticas.count_documents({}),
        }
        client.close()
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
