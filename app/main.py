from fastapi import FastAPI

app = FastAPI(
    title="Diplomado BD API",
    description="API de demostración para pruebas de CI/CD con GitHub Actions y Docker",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenido a la API del Diplomado en BD - CI/CD con GitHub Actions",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "diplomado-bd-api"}
