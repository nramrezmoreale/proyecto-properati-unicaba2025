import pandas as pd
import sqlite3
from sqlite3 import Error
import os

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
#Nombre de la Base de Datos
DB_NAME = 'db_properti.db'

#Archivos que contienen la información a cargar
CSV_FILES = {
    'properati_clean': 'properati_clean.csv',
    'metricas': 'metricas_entrenamiento.csv',
    'resultados_lineal': 'resultados_lineal.csv',
    'resultados_rforest': 'resultados_rforest.csv'
}

# Definición del mapeo de modelos para la tabla 'modelo' y las de resultados/métricas
MODEL_MAP = {
    'Regresion_Lineal': 1,
    'Random_Forest': 2
}

# =============================================================================
# 1. FUNCIÓN DE CONEXIÓN A BASE DE DATOS
# =============================================================================
def get_db_connection():
    """Crea y devuelve la conexión a la base de datos SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        # Habilitamos el soporte de claves foráneas
        conn.execute("PRAGMA foreign_keys = ON;") 
        # Aseguramos que el texto se maneje correctamente como cadenas de Python (útil para csv)
        conn.text_factory = str
        return conn
    except Error as e:
        print(f"Error al conectar a SQLite: {e}")
        return None

# =============================================================================
# 2. FUNCIÓN DE CREACIÓN DE TABLAS
# =============================================================================
def create_tables(conn):
    """Crea las cuatro tablas requeridas en la base de datos."""
    cursor = conn.cursor()

    # 1. Tabla MODELO: Almacena los tipos de modelos (clave primaria)
    print("Creando tabla 'modelo'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelo (
            id_modelo INTEGER PRIMARY KEY,
            modelo TEXT NOT NULL UNIQUE
        );
    """)

    # 2. Tabla PROPERTI_CLEAN: Datos originales de la propiedad (clave primaria)
    print("Creando tabla 'properti_clean'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS properti_clean (
            id_registro INTEGER PRIMARY KEY,
            surface_total REAL,
            rooms INTEGER,
            bathrooms INTEGER,
            price REAL,
            price_per_m2 REAL
        );
    """)

    # 3. Tabla RESULTADOS: Predicciones de ambos modelos (clave foránea a properti_clean y modelo)
    print("Creando tabla 'resultados'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id_modelo INTEGER,
            id_registro INTEGER,
            precio_real REAL,
            prediccion REAL,
            PRIMARY KEY (id_modelo, id_registro),
            FOREIGN KEY (id_modelo) REFERENCES modelo (id_modelo),
            FOREIGN KEY (id_registro) REFERENCES properti_clean (id_registro)
        );
    """)
    
    # 4. Tabla MÉTRICAS: Rendimiento de los modelos (clave foránea a modelo)
    print("Creando tabla 'metricas'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metricas (
            id_modelo INTEGER,
            fecha_ejecucion TEXT,
            rmse REAL,
            mae REAL,
            r2 REAL,
            PRIMARY KEY (id_modelo, fecha_ejecucion),
            FOREIGN KEY (id_modelo) REFERENCES modelo (id_modelo)
        );
    """)
    
    conn.commit()
    print("✅ Tablas creadas con éxito.")

# =============================================================================
# 3. FUNCIÓN DE CARGA DE DATOS
# =============================================================================
def load_data(conn):
    """Carga datos desde los CSV a las tablas correspondientes."""
    
    # -------------------------------------------------------------------------
    # 3.1 Carga Inicial de la tabla 'modelo'
    # -------------------------------------------------------------------------
    print("\nCargando datos en tabla 'modelo'...")
    modelo_data = pd.DataFrame(MODEL_MAP.items(), columns=['modelo', 'id_modelo'])
    modelo_data = modelo_data[['id_modelo', 'modelo']]
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM modelo;")
    conn.commit()

    modelo_data.to_sql('modelo', conn, if_exists='append', index=False)
    print("✅ Tabla 'modelo' cargada.")

    # -------------------------------------------------------------------------
    # 3.2 Carga de la tabla 'properti_clean' (Datos originales)
    # -------------------------------------------------------------------------
    print("\nCargando datos en tabla 'properti_clean'...")
    df_clean = pd.read_csv(CSV_FILES['properati_clean'])
    
    # Añadir id_registro (índice original del DataFrame)
    df_clean['id_registro'] = df_clean.index 

    # Redondeo de columnas
    df_clean['price'] = df_clean['price'].round(2)
    df_clean['price_per_m2'] = df_clean['price_per_m2'].round(2)
    
    # Conversión de tipos enteros (rooms, bathrooms)
    df_clean['rooms'] = df_clean['rooms'].astype(int)
    df_clean['bathrooms'] = df_clean['bathrooms'].astype(int)
    
    # Seleccionamos solo las columnas de la tabla (y reordenar para claridad)
    columns_to_keep = ['id_registro', 'surface_total', 'rooms', 'bathrooms', 'price', 'price_per_m2']
    df_clean = df_clean[columns_to_keep]
    
    # Carga: Usamos 'replace' para sobrescribir los datos originales en cada ejecución
    df_clean.to_sql('properti_clean', conn, if_exists='replace', index=False)
    print(f"✅ Tabla 'properti_clean' cargada ({len(df_clean)} filas).")
    
    # -------------------------------------------------------------------------
    # 3.3 Carga de la tabla 'resultados' (Combinada)
    # -------------------------------------------------------------------------
    print("\nCargando datos en tabla 'resultados'...")
    
    all_results = []
    
    # Procesamos Resultados Lineales
    df_lineal = pd.read_csv(CSV_FILES['resultados_lineal'])
    df_lineal['id_modelo'] = MODEL_MAP['Regresion_Lineal']
    df_lineal = df_lineal.rename(columns={'id_registro': 'id_registro', 'prediccion_lineal': 'prediccion'})
    df_lineal['precio_real'] = df_lineal['precio_real'].round(2)
    df_lineal['prediccion'] = df_lineal['prediccion'].round(2)
    all_results.append(df_lineal[['id_modelo', 'id_registro', 'precio_real', 'prediccion']])
    
    # Procesamos Resultados Random Forest
    df_rforest = pd.read_csv(CSV_FILES['resultados_rforest'])
    df_rforest['id_modelo'] = MODEL_MAP['Random_Forest']
    df_rforest = df_rforest.rename(columns={'id_registro': 'id_registro', 'prediccion_rforest': 'prediccion'})
    df_rforest['precio_real'] = df_rforest['precio_real'].round(2)
    df_rforest['prediccion'] = df_rforest['prediccion'].round(2)
    all_results.append(df_rforest[['id_modelo', 'id_registro', 'precio_real', 'prediccion']])
    
    # Combinamos y cargamos
    df_resultados = pd.concat(all_results, ignore_index=True)
    df_resultados.to_sql('resultados', conn, if_exists='replace', index=False)
    print(f"✅ Tabla 'resultados' cargada ({len(df_resultados)} filas).")

    # -------------------------------------------------------------------------
    # 3.4 Carga de la tabla 'metricas'
    # -------------------------------------------------------------------------
    print("\nCargando datos en tabla 'metricas'...")
    df_metricas = pd.read_csv(CSV_FILES['metricas'])
    
    #Limpiar la columna 'modelo' de espacios en blanco
    df_metricas['modelo'] = df_metricas['modelo'].str.strip()

    # Mapeo de id_modelo
    #df_metricas['id_modelo'] = df_metricas['modelo'].map(MODEL_MAP)

    # Mapeo directo
    df_metricas['id_modelo'] = df_metricas['modelo'].replace({
        'Regresion_Lineal': 1,
        'Random_Forest': 2
    })

    # FORZAMOS EL ID A TIPO ENTERO (INTEGER)
    df_metricas['id_modelo'] = df_metricas['id_modelo'].astype(int)

    # VERIFICACIÓN DE SEGURIDAD
    if df_metricas['id_modelo'].isnull().any():
        print("\n❌ ERROR CRÍTICO DE CONSISTENCIA DE DATOS:")
        #print("Uno o más nombres de modelos en el CSV de métricas no coinciden con el mapeo (1=Lineal, 2=RF).")
        print("Hay nombres de modelos en el CSV de métricas que no son 'Regresion_Lineal' o 'Random_Forest'.")
        print(f"Nombres sin mapear: {df_metricas[df_metricas['id_modelo'].isnull()]['modelo'].unique()}")
        raise Exception("Error de Mapeo de ID de Modelo.")
    
    # Formato de fecha (dd-mm-aaaa)
    df_metricas['fecha_ejecucion'] = pd.to_datetime(df_metricas['fecha_ejecucion']).dt.strftime('%d-%m-%Y')
    
    # Redondeo de métricas
    df_metricas['RMSE'] = df_metricas['RMSE'].round(2)
    df_metricas['MAE'] = df_metricas['MAE'].round(2)
    df_metricas['R2'] = df_metricas['R2'].round(4) # R2 suele redondearse a más dígitos
    
    # Seleccionamos y renombramos columnas
    df_metricas = df_metricas.rename(columns={'RMSE': 'rmse', 'MAE': 'mae', 'R2': 'r2'})
    
    columns_to_keep = ['id_modelo', 'fecha_ejecucion', 'rmse', 'mae', 'r2']
    df_metricas = df_metricas[columns_to_keep]

    # Carga: Usamos 'append' para mantener el historial de ejecuciones.
    df_metricas.to_sql('metricas', conn, if_exists='append', index=False)
    print(f"✅ Tabla 'metricas' cargada ({len(df_metricas)} filas).")

    conn.commit()

# =============================================================================
# 4. FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    """Función principal para orquestar la creación y carga de la DB."""
    print(f"Iniciando proceso de carga en la base de datos '{DB_NAME}'.")

    # ELIMINAR LA DB ANTES DE EMPEZAR
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"🗑️ Base de datos '{DB_NAME}' existente eliminada para asegurar limpieza.")
    
    # 1. Verificar existencia de archivos CSV
    missing_files = [f for f in CSV_FILES.values() if not os.path.exists(f)]
    if missing_files:
        print(f"\n❌ ERROR: Faltan los siguientes archivos CSV para la carga: {missing_files}")
        print("Asegúrate de ejecutar primero el notebook 'entrenamientos.ipynb'.")
        return

    conn = None
    try:
        conn = get_db_connection()
        
        create_tables(conn)
        load_data(conn)
        
        print("\n🎉 Proceso de carga de datos finalizado con éxito.")
        
    except sqlite3.Error as e:
        print(f"\n❌ Error de SQLite: {e}")
    except pd.errors.EmptyDataError:
        print("\n❌ Error de datos: Uno de los archivos CSV está vacío.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()