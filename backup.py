import shutil
from datetime import datetime
import os

# ruta base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

origen = os.path.join(BASE_DIR, "db.sqlite3")

# crear carpeta backup si no existe
carpeta_backup = os.path.join(BASE_DIR, "backup")
os.makedirs(carpeta_backup, exist_ok=True)

# nombre archivo
nombre = f"db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"

destino = os.path.join(carpeta_backup, nombre)

shutil.copy(origen, destino)

print("✅ Backup realizado:", destino)
