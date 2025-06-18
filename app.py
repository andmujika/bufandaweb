from flask import Flask, render_template, g, redirect, url_for, request
import sqlite3
import random
from datetime import date, timedelta
import os

app = Flask(__name__)
DATABASE = 'bufandas.db'
BUFANDA_DEL_DIA_FILE = 'bufanda_del_dia.txt'

# Función para obtener la conexión a la DB
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Función para cargar o seleccionar la bufanda del día
def cargar_o_seleccionar_bufanda_del_dia():
    today = date.today()
    bufanda_zenbakia_del_dia = None # Usamos ZENBAKIA ahora
    fecha_guardada = None

    # Intentar leer el archivo de la bufanda del día
    if os.path.exists(BUFANDA_DEL_DIA_FILE):
        with open(BUFANDA_DEL_DIA_FILE, 'r') as f:
            lineas = f.readlines()
            if len(lineas) == 2:
                fecha_guardada_str = lineas[0].strip()
                bufanda_zenbakia_del_dia_str = lineas[1].strip()
                try:
                    fecha_guardada = date.fromisoformat(fecha_guardada_str)
                    bufanda_zenbakia_del_dia = int(bufanda_zenbakia_del_dia_str)
                except ValueError:
                    pass

    # Si es un nuevo día o el archivo no existe/está corrupto, selecciona una nueva bufanda
    if fecha_guardada != today or bufanda_zenbakia_del_dia is None:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ZENBAKIA FROM bufandas") # Seleccionamos ZENBAKIA
            zenbakiak_disponibles = [row[0] for row in cursor.fetchall()]
            if zenbakiak_disponibles:
                bufanda_zenbakia_del_dia = random.choice(zenbakiak_disponibles)
                with open(BUFANDA_DEL_DIA_FILE, 'w') as f:
                    f.write(str(today) + '\n')
                    f.write(str(bufanda_zenbakia_del_dia) + '\n')
            else:
                bufanda_zenbakia_del_dia = None
        finally:
            conn.close()

    # Carga la bufanda seleccionada
    if bufanda_zenbakia_del_dia:
        conn = get_db_connection()
        try:
            bufanda = conn.execute('SELECT * FROM bufandas WHERE ZENBAKIA = ?', (bufanda_zenbakia_del_dia,)).fetchone()
            return bufanda
        finally:
            conn.close()
    return None

@app.before_request
def before_request_func():
    g.bufanda_del_dia = cargar_o_seleccionar_bufanda_del_dia()

@app.route('/')
def index():
    conn = get_db_connection()
    
    # --- Obtener años únicos para el filtro (campo NOIZ) ---
    try:
        years_raw = conn.execute("SELECT DISTINCT SUBSTR(NOIZ, 1, 4) FROM bufandas WHERE NOIZ IS NOT NULL AND LENGTH(NOIZ) >= 4").fetchall()
        all_years = sorted(list(set([y[0] for y in years_raw if y[0] and y[0].isdigit()])))
    except Exception as e:
        print(f"Error al obtener años: {e}")
        all_years = []

    # --- Procesar la búsqueda ---
    search_field = request.args.get('search_field', 'all')
    
    # Orain, bi search_query balio posible ditugu
    search_query_text = request.args.get('search_query', '').strip()
    search_query_year = request.args.get('search_query_year', '').strip() # Aldaketa hemen

    # Zein search_query erabili erabaki
    current_search_query = ''
    if search_field == 'NOIZ':
        current_search_query = search_query_year # Urtearen balioa erabili
    else:
        current_search_query = search_query_text # Testuaren balioa erabili

    query = "SELECT * FROM bufandas"
    params = []
    where_clauses = []

    # Excluir la bufanda del día si existe
    if g.bufanda_del_dia:
        where_clauses.append("ZENBAKIA != ?")
        params.append(g.bufanda_del_dia['ZENBAKIA'])

    if current_search_query: # Erabili current_search_query
        if search_field == 'all':
            # Busca en todas las columnas relevantes
            cursor = conn.execute(f"PRAGMA table_info(bufandas)")
            all_cols = [col[1] for col in cursor.fetchall() if col[1] not in ['ZENBAKIA', 'MAIN_IMAGE', 'IMAGE_1', 'IMAGE_2', 'IMAGE_3', 'IMAGE_4', 'IMAGE_5']] # Excluir claves y rutas de imagen

            search_like_clauses = []
            for col in all_cols:
                search_like_clauses.append(f"{col} LIKE ?")
                params.append(f"%{current_search_query}%") # Erabili current_search_query
            if search_like_clauses:
                where_clauses.append(f"({' OR '.join(search_like_clauses)})")

        elif search_field == 'NOIZ':
            # Para NOIZ, busca los 4 primeros caracteres (el año)
            where_clauses.append("SUBSTR(NOIZ, 1, 4) = ?")
            params.append(current_search_query) # Erabili current_search_query
        else:
            # Búsqueda en un campo específico (TALDEA, LIGA, NORK, BESTE)
            where_clauses.append(f"{search_field} LIKE ?")
            params.append(f"%{current_search_query}%") # Erabili current_search_query
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    # Ordenar los resultados (opcional)
    query += " ORDER BY TALDEA, NOIZ"

    bufandas = conn.execute(query, params).fetchall()
    conn.close()

    # Columnas disponibles para el filtro (se usan en el HTML)
    filterable_columns = [
        {'value': 'all', 'label': 'Eremu Guztiak'},
        {'value': 'TALDEA', 'label': 'Taldea'},
        {'value': 'LIGA', 'label': 'Liga'},
        {'value': 'NOIZ', 'label': 'Noiz Ekarria'}, # Este se tratará como año
        {'value': 'NORK', 'label': 'Nork Ekarria'},
        {'value': 'BESTE', 'label': 'Historia'}
    ]

    return render_template(
        'index.html',
        bufandas=bufandas,
        bufanda_del_dia=g.bufanda_del_dia,
        filterable_columns=filterable_columns,
        all_years=all_years, # Pasamos los años únicos
        current_search_field=search_field,
        current_search_query=current_search_query # Hemen, gorde behar den balioa pasatzen dugu
    )

@app.route('/bufanda/<int:bufanda_id>')
def bufanda_detalle(bufanda_id):
    conn = get_db_connection()
    bufanda = conn.execute('SELECT * FROM bufandas WHERE ZENBAKIA = ?', (bufanda_id,)).fetchone()
    conn.close()
    if bufanda is None:
        return "Bufanda no encontrada", 404
    return render_template('detalle_bufanda.html', bufanda=bufanda)

if __name__ == '__main__':
    app.run(debug=True)