from flask import Flask, render_template, g, redirect, url_for, request, session
import sqlite3
import random
from datetime import date
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'futbol-bufanda-bilduma-secret-key-2026')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'bufandas.db')
BUFANDA_DEL_DIA_FILE = os.path.join(BASE_DIR, 'bufanda_del_dia.txt')

# Translations dictionary (Basque 'eu' and English 'en')
TRANSLATIONS = {
    'eu': {
        'site_title': 'Futbol Bufanda Bilduma',
        'nav_home': 'Hasiera',
        'nav_collection': 'Bilduma',
        'nav_map': 'Munduko Mapa',
        'hero_badge': 'Bilduma Pertsonala · 1994tik gaur egunera',
        'hero_title': 'Futbol Bufanda Bilduma',
        'hero_subtitle': 'Munduko txoko guztietako estadio, bidaia eta lagunen oroitzapenak biltzen dituen bilduma.',
        'hero_cta_collection': 'Arakatu Bilduma',
        'hero_cta_map': 'Ikusi Munduko Mapa',
        'about_title': 'Bildumari buruz',
        'about_p1': (
            'Ongi etorri nire futbol bufanda bildumaren txoko digitalera. Bilduma hau 1990eko hamarkadaren '
            'amaieran eta 2003ko Oktoberfesteko lehen bidaia hartan hasi zen hazten, Donostiatik abiatuta '
            'munduko zelai eta hiri ugaritara zabalduz.'
        ),
        'about_p2': (
            'Bufanda bakoitzak bere istorio propioa du: bertatik bertara ikusitako partidak, eztei-bidaian '
            'lortutako altxorrak, Erasmus egonaldiak, eta familiak, lagunek zein lankideek munduan zehar '
            'egindako bidaietatik ekarritako oroigarriak. Ez dira oihal zati hutsak; futbolaren kulturaren '
            'eta partekatutako pasioaren lekukoak dira.'
        ),
        'about_p3': (
            'Webgune honetan bilduma osoa arakatu dezakezu talde, liga, urte edo emailearen arabera iragaziz, '
            'baita bufanda guztien jatorria munduko mapa interaktiboan kokatu ere.'
        ),
        'stat_scarves': 'Bufanda Guztira',
        'stat_cities': 'Hiri Ezberdin',
        'stat_leagues': 'Liga eta Herrialde',
        'stat_since': 'Hasiera Urtea',
        'sotd_badge': 'Gaurko Nabarmendua',
        'sotd_title': 'Eguneko Bufanda',
        'sotd_cta': 'Ikusi bufandaren fitxa →',
        'search_label': 'Bilatu:',
        'search_placeholder': 'Sartu bilaketa terminoa...',
        'select_year': 'Aukeratu urtea',
        'search_btn': 'Bilatu',
        'clear_btn': 'Garbitu',
        'grid_view': 'Grid Ikuspegia',
        'list_view': 'Zerrenda Ikuspegia',
        'results_count': 'bufanda aurkitu dira',
        'col_image': 'Irudia',
        'col_team': 'Taldea',
        'col_city': 'Hiria',
        'col_league': 'Liga',
        'col_date': 'Noiz',
        'col_who': 'Nork',
        'filter_all': 'Eremu Guztiak',
        'filter_team': 'Taldea',
        'filter_city': 'Hiria',
        'filter_league': 'Liga',
        'filter_date': 'Noiz Ekarria',
        'filter_who': 'Nork Ekarria',
        'filter_story': 'Historia',
        'no_results': 'Ez da bilaketa honekin bat datorren bufandarik aurkitu.',
        'detail_city': 'Hiria',
        'detail_date': 'Data',
        'detail_league': 'Liga',
        'detail_who': 'Nork Ekarria',
        'detail_story': 'Istorioa',
        'detail_no_story': 'Oraindik ez da istorio zehatzik gehitu bufanda honetarako.',
        'detail_coords': 'Koordenatuak',
        'detail_view_on_map': 'Kokatu munduko mapan',
        'detail_photos': 'Argazkiak',
        'detail_no_photos': 'Ez dago argazkirik eskuragarri momentuz.',
        'back_to_collection': '← Itzuli bildumara',
        'map_title': 'Bufanden Munduko Mapa',
        'map_subtitle': 'Egin klik edozein puntutan bufandaren informazioa ikusteko eta bere fitxara joateko.',
        'map_search_placeholder': 'Bilatu taldea, hiria, liga edo emailea...',
        'map_league_all': 'Liga / Herrialde guztiak',
        'map_reset': 'Berrezarri',
        'map_showing': 'Erakusten:',
        'map_scarves_unit': 'bufanda',
        'map_style_osm': 'Estandarra',
        'map_style_satellite': 'Satelitea',
        'map_popup_city': 'Hiria',
        'map_popup_league': 'Liga',
        'map_popup_who': 'Nork',
        'map_popup_date': 'Noiz',
        'map_popup_link': 'Ikusi bufandaren fitxa →',
        'map_sidebar_title': 'Kokalekuen Zerrenda',
        'footer_text': 'Futbol Bufanda Bilduma · Euskal Herria',
        'not_found': 'Bufanda ez da aurkitu',
    },
    'en': {
        'site_title': 'Football Scarf Collection',
        'nav_home': 'Home',
        'nav_collection': 'Collection',
        'nav_map': 'World Map',
        'hero_badge': 'Personal Archive · Since 1994',
        'hero_title': 'Football Scarf Collection',
        'hero_subtitle': 'A personal archive of stadiums, travels, and shared football memories from every corner of the globe.',
        'hero_cta_collection': 'Browse Collection',
        'hero_cta_map': 'Explore World Map',
        'about_title': 'About the Collection',
        'about_p1': (
            'Welcome to the digital home of my football scarf collection. What started in the late 1990s '
            'and took off during a 2003 Oktoberfest trip has grown from Donostia / San Sebastián into a '
            'worldwide archive spanning clubs and national teams across continents.'
        ),
        'about_p2': (
            'Every scarf tells its own story: matches attended in person, treasures found on our honeymoon, '
            'Erasmus adventures, and souvenirs thoughtfully brought back by family, friends, and colleagues '
            'from their travels around the world. More than fabric, each piece captures football culture and friendship.'
        ),
        'about_p3': (
            'Explore the full catalog by filtering by team, city, league, year, or contributor, or browse '
            'the interactive world map to discover where every single scarf comes from.'
        ),
        'stat_scarves': 'Total Scarves',
        'stat_cities': 'Unique Cities',
        'stat_leagues': 'Leagues & Countries',
        'stat_since': 'Collecting Since',
        'sotd_badge': 'Daily Highlight',
        'sotd_title': 'Scarf of the Day',
        'sotd_cta': 'View scarf page →',
        'search_label': 'Search:',
        'search_placeholder': 'Enter search term...',
        'select_year': 'Select year',
        'search_btn': 'Search',
        'clear_btn': 'Clear',
        'grid_view': 'Grid View',
        'list_view': 'List View',
        'results_count': 'scarves found',
        'col_image': 'Image',
        'col_team': 'Team',
        'col_city': 'City',
        'col_league': 'League',
        'col_date': 'Date',
        'col_who': 'Brought By',
        'filter_all': 'All Fields',
        'filter_team': 'Team',
        'filter_city': 'City',
        'filter_league': 'League',
        'filter_date': 'Year Acquired',
        'filter_who': 'Brought By',
        'filter_story': 'Story',
        'no_results': 'No scarves matched your search criteria.',
        'detail_city': 'City',
        'detail_date': 'Date Acquired',
        'detail_league': 'League',
        'detail_who': 'Brought By',
        'detail_story': 'Story',
        'detail_no_story': 'No detailed story has been added for this scarf yet.',
        'detail_coords': 'Coordinates',
        'detail_view_on_map': 'Locate on World Map',
        'detail_photos': 'Photos',
        'detail_no_photos': 'No photos available at the moment.',
        'back_to_collection': '← Back to collection',
        'map_title': 'World Map of Scarves',
        'map_subtitle': 'Click any marker to inspect the scarf details and jump directly to its page.',
        'map_search_placeholder': 'Search team, city, league, or contributor...',
        'map_league_all': 'All Leagues / Countries',
        'map_reset': 'Reset',
        'map_showing': 'Showing:',
        'map_scarves_unit': 'scarves',
        'map_style_osm': 'Standard',
        'map_style_satellite': 'Satellite',
        'map_popup_city': 'City',
        'map_popup_league': 'League',
        'map_popup_who': 'Brought By',
        'map_popup_date': 'Date',
        'map_popup_link': 'View scarf page →',
        'map_sidebar_title': 'Locations List',
        'footer_text': 'Football Scarf Collection · Basque Country',
        'not_found': 'Scarf not found',
    }
}

MONTH_MAP_EN = {
    'Urtarrila': 'January',
    'Otsaila': 'February',
    'Martxoa': 'March',
    'Apirila': 'April',
    'Maiatza': 'May',
    'Ekaina': 'June',
    'Uztaila': 'July',
    'Abuztua': 'August',
    'Iraila': 'September',
    'Urria': 'October',
    'Azaroa': 'November',
    'Abendua': 'December',
}


def format_date_display(noiz_str, lang='eu'):
    if not noiz_str:
        return ''
    text = str(noiz_str).strip()
    if lang == 'en':
        parts = text.split(' ', 1)
        if len(parts) == 2 and parts[1] in MONTH_MAP_EN:
            return f"{MONTH_MAP_EN[parts[1]]} {parts[0]}"
    return text


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_existing_scarf_images(bufanda):
    """Return only image filenames that actually exist inside static/images."""
    if not bufanda:
        return []
    images_dir = os.path.join(app.static_folder, 'images')
    img_cols = ['main_image', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5']
    available_keys = set(bufanda.keys())
    valid_imgs = []
    seen = set()
    for col in img_cols:
        if col not in available_keys:
            continue
        raw_val = bufanda[col]
        if not raw_val:
            continue
        img_name = str(raw_val).strip()
        if not img_name or img_name.lower() == 'nan' or img_name in seen:
            continue
        # Prevent path traversal and verify the file exists on disk
        if os.path.basename(img_name) != img_name:
            continue
        if os.path.isfile(os.path.join(images_dir, img_name)):
            valid_imgs.append(img_name)
            seen.add(img_name)
    return valid_imgs


def cargar_o_seleccionar_bufanda_del_dia():
    bufanda_zenbakia_del_dia = None

    # 1. Irakurri zenbakia bufanda_del_dia.txt fitxategitik (hutsik ez badago)
    if os.path.exists(BUFANDA_DEL_DIA_FILE):
        with open(BUFANDA_DEL_DIA_FILE, 'r', encoding='utf-8') as f:
            lineas = [linea.strip() for linea in f.readlines() if linea.strip()]
            if len(lineas) == 1:
                try:
                    bufanda_zenbakia_del_dia = int(lineas[0])
                except ValueError:
                    bufanda_zenbakia_del_dia = None
            elif len(lineas) >= 2:
                # Bateragarritasuna mantentzeko (data + zenbakia formatua badu)
                try:
                    bufanda_zenbakia_del_dia = int(lineas[1])
                except ValueError:
                    try:
                        bufanda_zenbakia_del_dia = int(lineas[0])
                    except ValueError:
                        bufanda_zenbakia_del_dia = None

    conn = get_db_connection()
    try:
        # Fitxategian zenbaki baliodun bat badago, bilatu datu-basean
        if bufanda_zenbakia_del_dia is not None:
            bufanda = conn.execute(
                'SELECT * FROM bufandas WHERE ZENBAKIA = ?',
                (bufanda_zenbakia_del_dia,)
            ).fetchone()
            if bufanda is not None:
                return bufanda

        # 2. Fitxategia hutsik badago (edo zenbakia ez bada existitzen),
        # gaurko data hartu eta horren arabera aukeratu zenbakia
        today = date.today()
        cursor = conn.cursor()
        cursor.execute("SELECT ZENBAKIA FROM bufandas ORDER BY ZENBAKIA")
        zenbakiak_disponibles = [row[0] for row in cursor.fetchall()]
        if zenbakiak_disponibles:
            rng = random.Random(today.isoformat())
            bufanda_zenbakia_del_dia = rng.choice(zenbakiak_disponibles)
            return conn.execute(
                'SELECT * FROM bufandas WHERE ZENBAKIA = ?',
                (bufanda_zenbakia_del_dia,)
            ).fetchone()
    finally:
        conn.close()

    return None


@app.before_request
def before_request_func():
    requested_lang = request.args.get('lang')
    if requested_lang in ('eu', 'en'):
        session['lang'] = requested_lang
    g.lang = session.get('lang', 'eu')
    g.bufanda_del_dia = cargar_o_seleccionar_bufanda_del_dia()


@app.context_processor
def inject_globals():
    lang = getattr(g, 'lang', 'eu')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['eu'])

    def switch_lang_url(target_lang):
        args = request.args.to_dict(flat=True)
        args['lang'] = target_lang
        view_args = dict(request.view_args or {})
        endpoint = request.endpoint or 'home'
        try:
            return url_for(endpoint, **view_args, **args)
        except Exception:
            return url_for('home', lang=target_lang)

    return {
        'lang': lang,
        't': t,
        'switch_lang_url': switch_lang_url,
        'format_date': lambda val: format_date_display(val, lang),
    }


@app.route('/')
def home():
    conn = get_db_connection()
    total_scarves = conn.execute("SELECT COUNT(*) FROM bufandas").fetchone()[0]
    total_cities = conn.execute(
        "SELECT COUNT(DISTINCT NONDIK) FROM bufandas WHERE NONDIK IS NOT NULL AND NONDIK != ''"
    ).fetchone()[0]
    total_leagues = conn.execute(
        "SELECT COUNT(DISTINCT LIGA) FROM bufandas WHERE LIGA IS NOT NULL AND LIGA != ''"
    ).fetchone()[0]
    years_raw = conn.execute(
        "SELECT DISTINCT SUBSTR(NOIZ, 1, 4) FROM bufandas WHERE NOIZ IS NOT NULL AND LENGTH(NOIZ) >= 4"
    ).fetchall()
    valid_years = sorted([y[0] for y in years_raw if y[0] and y[0].isdigit()])
    earliest_year = valid_years[0] if valid_years else '1994'
    conn.close()

    stats = {
        'total_scarves': total_scarves,
        'total_cities': total_cities,
        'total_leagues': total_leagues,
        'earliest_year': earliest_year,
    }

    return render_template(
        'home.html',
        stats=stats,
        bufanda_del_dia=g.bufanda_del_dia,
    )


@app.route('/bilduma')
def bilduma():
    lang = getattr(g, 'lang', 'eu')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['eu'])
    conn = get_db_connection()

    try:
        years_raw = conn.execute(
            "SELECT DISTINCT SUBSTR(NOIZ, 1, 4) FROM bufandas WHERE NOIZ IS NOT NULL AND LENGTH(NOIZ) >= 4"
        ).fetchall()
        all_years = sorted(list(set([y[0] for y in years_raw if y[0] and y[0].isdigit()])))
    except Exception as e:
        print(f"Error al obtener años: {e}")
        all_years = []

    search_field = request.args.get('search_field', 'all')
    search_query_text = request.args.get('search_query', '').strip()
    search_query_year = request.args.get('search_query_year', '').strip()

    if search_field == 'NOIZ':
        current_search_query = search_query_year
    else:
        current_search_query = search_query_text

    query = "SELECT * FROM bufandas"
    params = []
    where_clauses = []

    if current_search_query:
        if search_field == 'all':
            cursor = conn.execute("PRAGMA table_info(bufandas)")
            excluded = {'ZENBAKIA', 'NONDIK X', 'NONDIK Y', 'MAIN_IMAGE', 'IMAGE_1', 'IMAGE_2', 'IMAGE_3', 'IMAGE_4', 'IMAGE_5'}
            all_cols = [col[1] for col in cursor.fetchall() if col[1].upper() not in excluded]

            search_like_clauses = []
            for col in all_cols:
                search_like_clauses.append(f'"{col}" LIKE ?')
                params.append(f"%{current_search_query}%")
            if search_like_clauses:
                where_clauses.append(f"({' OR '.join(search_like_clauses)})")

        elif search_field == 'NOIZ':
            where_clauses.append("SUBSTR(NOIZ, 1, 4) = ?")
            params.append(current_search_query)
        else:
            allowed_fields = {'TALDEA', 'NONDIK', 'LIGA', 'NORK', 'BESTE'}
            if search_field in allowed_fields:
                where_clauses.append(f'"{search_field}" LIKE ?')
                params.append(f"%{current_search_query}%")

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += " ORDER BY TALDEA, NOIZ"

    bufandas = conn.execute(query, params).fetchall()
    conn.close()

    filterable_columns = [
        {'value': 'all', 'label': t['filter_all']},
        {'value': 'TALDEA', 'label': t['filter_team']},
        {'value': 'NONDIK', 'label': t['filter_city']},
        {'value': 'LIGA', 'label': t['filter_league']},
        {'value': 'NOIZ', 'label': t['filter_date']},
        {'value': 'NORK', 'label': t['filter_who']},
        {'value': 'BESTE', 'label': t['filter_story']},
    ]

    return render_template(
        'index.html',
        bufandas=bufandas,
        bufanda_del_dia=g.bufanda_del_dia,
        filterable_columns=filterable_columns,
        all_years=all_years,
        current_search_field=search_field,
        current_search_query=current_search_query,
    )


@app.route('/mapa')
def mapa():
    lang = getattr(g, 'lang', 'eu')
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT * FROM bufandas WHERE "NONDIK X" IS NOT NULL AND "NONDIK Y" IS NOT NULL ORDER BY TALDEA'
    ).fetchall()
    conn.close()

    scarves_map_data = []
    leagues_set = set()
    for r in rows:
        liga_val = r['LIGA'] or ''
        if liga_val:
            leagues_set.add(liga_val)
        scarves_map_data.append({
            'zenbakia': r['ZENBAKIA'],
            'taldea': r['TALDEA'] or '',
            'nondik': r['NONDIK'] or '',
            'lon': float(r['NONDIK X']),
            'lat': float(r['NONDIK Y']),
            'liga': liga_val,
            'nork': r['NORK'] or '',
            'noiz': format_date_display(r['NOIZ'], lang),
            'beste': r['BESTE'] or '',
            'main_image': r['main_image'] or '',
            'url': url_for('bufanda_detalle', bufanda_id=r['ZENBAKIA']),
        })

    focus_zenbakia = request.args.get('zenbakia', type=int)

    return render_template(
        'mapa.html',
        scarves_map_data=scarves_map_data,
        all_leagues=sorted(list(leagues_set)),
        focus_zenbakia=focus_zenbakia,
    )


@app.route('/bufanda/<int:bufanda_id>')
def bufanda_detalle(bufanda_id):
    lang = getattr(g, 'lang', 'eu')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['eu'])
    conn = get_db_connection()
    bufanda = conn.execute('SELECT * FROM bufandas WHERE ZENBAKIA = ?', (bufanda_id,)).fetchone()
    conn.close()
    if bufanda is None:
        return t['not_found'], 404
    valid_imgs = get_existing_scarf_images(bufanda)
    return render_template('detalle_bufanda.html', bufanda=bufanda, valid_imgs=valid_imgs)
