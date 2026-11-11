import pandas as pd
import sqlite3
import os

def importar_excel_a_db(ruta_excel, nombre_db='bufandas.db', nombre_tabla='bufandas'):
    try:
        # Leer el archivo Excel
        df = pd.read_excel(ruta_excel)
        df['ZENBAKIA'] = df['ZENBAKIA'].astype(int)

        # --- Novedad: Convertir coordenadas a tipo numérico (float) ---
        if 'NONDIK X' in df.columns:
            df['NONDIK X'] = pd.to_numeric(df['NONDIK X'], errors='coerce')
        if 'NONDIK Y' in df.columns:
            df['NONDIK Y'] = pd.to_numeric(df['NONDIK Y'], errors='coerce')

        # Conectar a la base de datos
        conn = sqlite3.connect(nombre_db)
        cursor = conn.cursor()

        # --- Lógica para definir los tipos de columna ---
        column_definitions = []
        for col in df.columns:
            col_upper = col.upper()
            if col_upper == 'ZENBAKIA':
                column_definitions.append(f'"{col}" INTEGER PRIMARY KEY')
            elif col_upper in ['NONDIK X', 'NONDIK Y']:
                # Coordenadas como REAL (float numérico) en SQLite
                column_definitions.append(f'"{col}" REAL')
            else:
                column_definitions.append(f'"{col}" TEXT')
        
        # Unir las definiciones de columna para la sentencia CREATE TABLE
        columns_sql = ', '.join(column_definitions)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {nombre_tabla} ({columns_sql})"
        cursor.execute(create_table_sql)
        conn.commit()

        # Insertar los datos manteniendo el esquema de la tabla (usando 'append')
        df.to_sql(nombre_tabla, conn, if_exists='append', index=False) 

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
    # Ajusta aquí el nombre exacto de tu archivo Excel
    excel_file = 'Bufanda_Bilduma.xlsx'
    db_file = 'bufandas.db'

    # Eliminar la base de datos anterior para regenerarla limpiamente
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Archivo de base de datos '{db_file}' eliminado para asegurar una creación limpia.")
        except OSError as e:
            print(f"Error: No se pudo eliminar el archivo '{db_file}': {e}")
            exit()

    if os.path.exists(excel_file):
        importar_excel_a_db(excel_file)
    else:
        print(f"Advertencia: El archivo '{excel_file}' no se encontró.")