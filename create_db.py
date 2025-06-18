import pandas as pd
import sqlite3
import os # Importar os para verificar la existencia del archivo

def importar_excel_a_db(ruta_excel, nombre_db='bufandas.db', nombre_tabla='bufandas'):
    try:
        # Leer el archivo Excel
        df = pd.read_excel(ruta_excel)
        df['ZENBAKIA'] = df['ZENBAKIA'].astype(int)

        # Conectar a la base de datos (se creará si no existe)
        conn = sqlite3.connect(nombre_db)
        cursor = conn.cursor()

        # --- Lógica para definir los tipos de columna ---
        column_definitions = []
        for col in df.columns:
            print(df.info())
            if col.upper() == 'ZENBAKIA': # Usamos .upper() para hacer la comparación insensible a mayúsculas/minúsculas
                column_definitions.append(f'"{col}" INTEGER PRIMARY KEY') # ZENBAKIA ahora es la clave primaria
            else:
                column_definitions.append(f'"{col}" TEXT')
        
        # Unir las definiciones de columna para la sentencia CREATE TABLE
        columns_sql = ', '.join(column_definitions)
        print(columns_sql)

        # Crear la tabla dinámicamente si no existe
        # Se elimina la columna 'id' autoincremental ya que ZENBAKIA será la clave primaria.
        # Nota: 'if_exists='replace'' en df.to_sql ya maneja la recreación de la tabla,
        # pero es crucial que no haya una DB antigua con la estructura incorrecta persistiendo.
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {nombre_tabla} ({columns_sql})"
        print(create_table_sql)
        cursor.execute(create_table_sql)
        conn.commit()

        # Insertar los datos del DataFrame en la tabla
        # 'replace' borrará la tabla y la recreará con la estructura del DataFrame,
        # lo cual es útil si la estructura de columnas cambia.
        # Si la tabla ya existe con la estructura correcta y solo quieres añadir, usa 'append'.
        df.to_sql(nombre_tabla, conn, if_exists='replace', index=False) 

        print(f"Datos de '{ruta_excel}' importados exitosamente a la tabla '{nombre_tabla}' en '{nombre_db}'.")

    except FileNotFoundError:
        print(f"Error: El archivo Excel no se encuentra en la ruta: {ruta_excel}")
    except pd.errors.EmptyDataError:
        print(f"Error: El archivo Excel '{ruta_excel}' está vacío.")
    except Exception as e:
        print(f"Ocurrió un error al importar los datos: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    # Asegúrate de reemplazar 'tu_archivo_bufandas.xlsx' con la ruta real de tu Excel
    # Si el Excel está en la misma carpeta que el script, solo el nombre del archivo
    excel_file = 'Bufanda Bilduma.xlsx' # ¡CAMBIA ESTO!
    db_file = 'bufandas.db' # Nombre del archivo de la base de datos

    # --- NUEVO: Eliminar el archivo de la base de datos si existe ---
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Archivo de base de datos '{db_file}' eliminado para asegurar una creación limpia.")
        except OSError as e:
            print(f"Error: No se pudo eliminar el archivo '{db_file}': {e}")
            print("Por favor, asegúrate de que no está abierto en DB Browser for SQLite u otra aplicación.")
            exit() # Salir si no se puede eliminar el archivo, ya que la creación fallaría o usaría la antigua

    if not os.path.exists(excel_file):
        print(f"Advertencia: El archivo '{excel_file}' no se encontró. Por favor, asegúrate de que está en la misma carpeta o proporciona la ruta completa.")
        print("Creando un archivo Excel de ejemplo para que puedas probarlo.")
        # Crear un DataFrame de ejemplo
        data = {
            'ZENBAKIA': [1, 2, 3, 4],
            'Equipo': ['Real Madrid', 'FC Barcelona', 'Athletic Club', 'Manchester Utd'],
            'Año': [2000, 2005, 1998, 2010],
            'Tipo': ['Colección', 'Partido', 'Conmemorativa', 'Fan'],
            'Material': ['Poliéster', 'Lana', 'Seda', 'Acrílico'],
            'Observaciones': ['Firmada', 'Edición limitada', 'Vieja', 'Nueva'],
            'RutaImagen': ['real_madrid.jpg', 'barcelona.jpg', 'athletic.jpg', 'man_utd.jpg'],
            'Foto2': ['real_madrid_2.jpg', None, None, None],
            'Foto3': [None, None, None, None]
        }
        df_example = pd.DataFrame(data)
        df_example.to_excel(excel_file, index=False)
        print(f"Archivo de ejemplo '{excel_file}' creado. Por favor, edítalo con tus datos reales.")
        print("Vuelve a ejecutar este script después de editar el archivo Excel.")
    else:
        importar_excel_a_db(excel_file)