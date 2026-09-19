import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymongo
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI(
    title="Diplomado BD API - Calculator & Feature Flags",
    description="API REST transaccional, analítica y calculadora con Feature Flags (Taller 2)",
    version="2.1.0",
)


# --- CLASE CALCULATOR CON HISTORIAL Y OPERACIONES ---
class Calculator:
    def __init__(self):
        self.historial = []

    def suma(self, a: float, b: float) -> float:
        res = a + b
        self.historial.append(f"{a} + {b} = {res}")
        return res

    def resta(self, a: float, b: float) -> float:
        res = a - b
        self.historial.append(f"{a} - {b} = {res}")
        return res

    def multiplicacion(self, a: float, b: float) -> float:
        res = a * b
        self.historial.append(f"{a} * {b} = {res}")
        return res

    def division(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("No se puede dividir entre cero")
        res = a / b
        self.historial.append(f"{a} / {b} = {res}")
        return res


calc = Calculator()


class CalcRequest(BaseModel):
    a: float
    b: float


# Feature Flags Configuration (Rollout 100%)
FEATURE_FLAGS = {
    "resta_enabled": True,
    "multiplicacion_enabled": True,
    "division_enabled": True,
    "historial_enabled": True,
}


def get_db():
    if not MONGO_URI:
        raise HTTPException(status_code=500, detail="MONGO_URI no configurado")
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client, client["ventas_db"]


@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenido al Proyecto Diplomado BD - Calculadora & CI/CD",
        "version": "2.1.0",
        "feature_flags": FEATURE_FLAGS,
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


# --- ENDPOINTS CALCULATOR ---
@app.post("/api/calculator/suma")
def api_suma(req: CalcRequest):
    return {"operacion": "suma", "a": req.a, "b": req.b, "resultado": calc.suma(req.a, req.b)}


@app.post("/api/calculator/resta")
def api_resta(req: CalcRequest):
    if not FEATURE_FLAGS.get("resta_enabled", False):
        raise HTTPException(status_code=403, detail="Feature resta_enabled desactivada por Feature Flag")
    return {"operacion": "resta", "a": req.a, "b": req.b, "resultado": calc.resta(req.a, req.b)}


@app.post("/api/calculator/multiplicacion")
def api_multiplicacion(req: CalcRequest):
    if not FEATURE_FLAGS.get("multiplicacion_enabled", False):
        raise HTTPException(status_code=403, detail="Feature multiplicacion_enabled desactivada")
    return {"operacion": "multiplicacion", "a": req.a, "b": req.b, "resultado": calc.multiplicacion(req.a, req.b)}


@app.post("/api/calculator/division")
def api_division(req: CalcRequest):
    if not FEATURE_FLAGS.get("division_enabled", False):
        raise HTTPException(status_code=403, detail="Feature division_enabled desactivada")
    try:
        res = calc.division(req.a, req.b)
        return {"operacion": "division", "a": req.a, "b": req.b, "resultado": res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/calculator/historial")
def api_historial():
    if not FEATURE_FLAGS.get("historial_enabled", False):
        raise HTTPException(status_code=403, detail="Feature historial_enabled desactivada")
    return {"status": "success", "historial": calc.historial}