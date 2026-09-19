import os
import sys
import pymongo
from dotenv import load_dotenv
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")


def crear_estructura_ventas():
    client = pymongo.MongoClient(MONGO_URI)
    db = client["ventas_db"]
    
    print("[INFO] Creando estructura de base de datos de ventas...\n")
    
    # 1. Crear colecciones OLTP (Transaccionales) si no existen
    print("[INFO] Creando colecciones transaccionales (OLTP)...")
    colecciones_existentes = db.list_collection_names()
    colecciones_oltp = ["clientes", "productos", "ventas"]
    for col in colecciones_oltp:
        if col not in colecciones_existentes:
            db.create_collection(col)
            print(f"  [+] Colección '{col}' creada")
        else:
            print(f"  [=] Colección '{col}' ya existe")
    
    # 2. Crear índices para optimizar consultas
    print("\n[INFO] Creando índices...")
    db.clientes.create_index([("email", 1)], unique=True)
    db.productos.create_index([("sku", 1)], unique=True)
    db.ventas.create_index([("fecha_venta", -1)])
    db.ventas.create_index([("cliente_id", 1)])
    print("  [+] Índices creados exitosamente")
    
    # 3. Insertar datos de prueba
    print("\n[INFO] Insertando datos de prueba de ejemplo...")
    
    if db.clientes.count_documents({"codigo_cliente": "CLI001"}) == 0:
        cliente_ejemplo = {
            "codigo_cliente": "CLI001",
            "nombre": "Juan Pérez",
            "email": "juan.perez@email.com",
            "telefono": "3001234567",
            "direccion": {
                "calle": "Calle 123 #45-67",
                "ciudad": "Bogotá",
                "pais": "Colombia"
            },
            "fecha_registro": datetime.now(),
            "activo": True
        }
        db.clientes.insert_one(cliente_ejemplo)
        print("  [+] Cliente de ejemplo insertado")
    
    if db.productos.count_documents({"sku": "PROD001"}) == 0:
        producto_ejemplo = {
            "sku": "PROD001",
            "nombre": "Laptop Dell XPS 15",
            "categoria": "Electrónica",
            "precio_unitario": 4500000,
            "stock": 25,
            "proveedor": "Dell Colombia S.A.S",
            "fecha_creacion": datetime.now()
        }
        db.productos.insert_one(producto_ejemplo)
        print("  [+] Producto de ejemplo insertado")
    
    if db.ventas.count_documents({"numero_factura": "FAC-2026-0001"}) == 0:
        cliente = db.clientes.find_one({"codigo_cliente": "CLI001"})
        producto = db.productos.find_one({"sku": "PROD001"})
        if cliente and producto:
            venta_ejemplo = {
                "numero_factura": "FAC-2026-0001",
                "cliente_id": cliente["_id"],
                "fecha_venta": datetime.now(),
                "items": [
                    {
                        "producto_id": producto["_id"],
                        "cantidad": 1,
                        "precio_unitario": 4500000,
                        "subtotal": 4500000
                    }
                ],
                "total": 4500000,
                "metodo_pago": "Tarjeta de Crédito",
                "estado": "Completada"
            }
            db.ventas.insert_one(venta_ejemplo)
            print("  [+] Venta de ejemplo insertada")
    
    # 4. Crear colección OLAP (Analítica)
    print("\n[INFO] Creando colección analítica (OLAP)...")
    if "ventas_analiticas" not in db.list_collection_names():
        db.create_collection("ventas_analiticas")
        print("  [+] Colección 'ventas_analiticas' creada")
    else:
        print("  [=] Colección 'ventas_analiticas' ya existe")
    
    print("\n[SUCCESS] Estructura de ventas creada exitosamente en Atlas!")
    client.close()


if __name__ == "__main__":
    crear_estructura_ventas()
