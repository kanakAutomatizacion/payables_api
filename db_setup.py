import sqlite3
from pathlib import Path

# Carpeta donde guardaremos la BD
db_path = Path("data")
db_path.mkdir(exist_ok=True)

DB_FILE = db_path / "reglas.db"

# Conectar a la base de datos (se crea si no existe)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Crear tabla
cursor.execute("""
CREATE TABLE IF NOT EXISTS reglas_cuenta (
    nit_vendedor TEXT PRIMARY KEY,
    cuenta_contable TEXT NOT NULL
)
""")

# Datos iniciales
reglas_iniciales = [
    ("891408584", "51956001"),
    ("800153993", "51353502"),
    ("830055643", "51359501"),
    ("890904996", "51353001"),
    ("800020706", "51055101"),
    ("800120681", "51055101"),
    ("805004875", "51055101"),
    ("800242106", "51451001"),
    ("860037013", "51301001")
]

cursor.executemany("""
INSERT OR REPLACE INTO reglas_cuenta (nit_vendedor, cuenta_contable)
VALUES (?, ?)
""", reglas_iniciales)

conn.commit()
conn.close()

print("✅ Base de datos creada en:", DB_FILE)
