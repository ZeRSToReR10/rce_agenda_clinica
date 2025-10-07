import pandas as pd
from sqlalchemy import create_engine

# Configuración de conexión a PostgreSQL
usuario = "rce_admin"
contraseña = "LaMc2019"
host = "localhost"
base_datos = "rce_database_new"

# Crear motor de conexión con SQLAlchemy
engine = create_engine(f"postgresql+psycopg2://{usuario}:{contraseña}@{host}/{base_datos}")

# Ruta del archivo Excel
archivo_excel = "diagnosticos.xlsx"  # cámbialo por tu ruta real

# Leer los datos
df = pd.read_excel(archivo_excel)

# Renombrar la columna si es necesario
df.columns = ["nombre"]  # asegúrate de que coincida con tu columna en la tabla

# Eliminar filas vacías o duplicadas
df = df.dropna().drop_duplicates()

# Insertar los datos en la tabla
df.to_sql("diagnosticos", engine, if_exists="append", index=False)

print(f"✅ {len(df)} diagnósticos cargados correctamente en la base de datos.")
