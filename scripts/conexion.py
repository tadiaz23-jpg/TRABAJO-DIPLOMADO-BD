import os
import sys
import pymongo
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure, ConfigurationError, OperationFailure

# Force UTF-8 stdout if needed
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")


def conectar_mongodb():
    try:
        print("[INFO] Intentando conectar a MongoDB Atlas...")
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("[SUCCESS] Conexión exitosa a MongoDB Atlas!")
        
        db = client["ventas_db"]
        return client, db
        
    except ConnectionFailure as e:
        print(f"[ERROR] No se pudo contactar al servidor: {e}")
    except ConfigurationError as e:
        print(f"[ERROR] Error de configuración: {e}")
    except OperationFailure as e:
        print(f"[ERROR] Error de autenticación: {e}")
    
    return None, None


if __name__ == "__main__":
    client, db = conectar_mongodb()
    if client:
        client.close()
        print("[INFO] Conexión cerrada.")
