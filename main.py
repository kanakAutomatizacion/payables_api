from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
from pathlib import Path
from pydantic import BaseModel

app = FastAPI()

# Ruta de la BD
DB_FILE = Path("data/reglas.db")
CUENTA_POR_DEFECTO = "51959501"


# -----------------------------
# 📌 MODELOS DE DATOS
# -----------------------------
class Regla(BaseModel):
    nit_vendedor: str
    cuenta_contable: str
    descripcion: str | None = None


# -----------------------------
# 📌 FUNCIONES AUXILIARES
# -----------------------------
def conectar_bd():
    """Abre la conexión a la base de datos."""
    return sqlite3.connect(DB_FILE)

def obtener_cuenta_por_nit(nit_vendedor: str) -> str:
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cuenta_contable FROM reglas_cuenta WHERE nit_vendedor = ?",
        (nit_vendedor,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else CUENTA_POR_DEFECTO


# -----------------------------
# 📌 ENDPOINT PRINCIPAL
# -----------------------------
@app.post("/completar-cuenta")
async def completar_cuenta(request: Request):
    data = await request.json()

    nit_vendedor = data.get("factura", {}).get("Nit_Vendedor", "")
    cuenta_asignada = obtener_cuenta_por_nit(nit_vendedor)

    for item in data.get("items", []):
        item["cuentacontable"] = cuenta_asignada

    return JSONResponse(content=data)


# -----------------------------
# 📌 ENDPOINTS ADMINISTRATIVOS
# -----------------------------

@app.get("/admin/reglas")
def listar_reglas():
    """Lista todas las reglas actuales."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nit_vendedor, cuenta_contable, descripcion FROM reglas_cuenta")
    reglas = [
        {"id": row[0], "nit_vendedor": row[1], "cuenta_contable": row[2], "descripcion": row[3]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return reglas


@app.post("/admin/reglas")
def agregar_regla(regla: Regla):
    """Agrega una nueva regla."""
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO reglas_cuenta (nit_vendedor, cuenta_contable, descripcion)
            VALUES (?, ?, ?)
        """, (regla.nit_vendedor, regla.cuenta_contable, regla.descripcion))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El NIT ya existe.")
    finally:
        conn.close()
    return {"message": "✅ Regla agregada con éxito"}


@app.put("/admin/reglas/{nit_vendedor}")
def actualizar_regla(nit_vendedor: str, regla: Regla):
    """Actualiza una regla existente por NIT."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reglas_cuenta
        SET cuenta_contable = ?, descripcion = ?
        WHERE nit_vendedor = ?
    """, (regla.cuenta_contable, regla.descripcion, nit_vendedor))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="NIT no encontrado.")
    conn.close()
    return {"message": "✅ Regla actualizada con éxito"}


@app.delete("/admin/reglas/{nit_vendedor}")
def eliminar_regla(nit_vendedor: str):
    """Elimina una regla por NIT."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reglas_cuenta WHERE nit_vendedor = ?", (nit_vendedor,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="NIT no encontrado.")
    conn.close()
    return {"message": "✅ Regla eliminada con éxito"}
