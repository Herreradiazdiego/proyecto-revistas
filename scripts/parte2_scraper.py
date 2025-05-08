import os
import json
import time
import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_JSON   = os.path.join(BASE_DIR, 'datos', 'json', 'revistas.json')
OUTPUT_JSON  = os.path.join(BASE_DIR, 'datos', 'json', 'revistas_scimago.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

def load_existing():
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_output(data):
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_journal_info(title):
    """Busca en SCImago y extrae los datos solicitados."""
    info = {
        'site_web': '',
        'h_index': '',
        'subject_area_and_category': [],
        'publisher': '',
        'issn': '',
        'widget': '',
        'publication_type': ''
    }

    # 1) Buscar el journal
    q = title.replace(' ', '+')
    url_search = f'https://www.scimagojr.com/journalsearch.php?q={q}'
    r1 = requests.get(url_search, headers=HEADERS)
    soup1 = BeautifulSoup(r1.text, 'html.parser')

    # Tomar el primer resultado de la tabla
    tabla = soup1.find('table', class_='searchresults')
    if not tabla:
        print(f'⚠️ No hay resultados para: {title}')
        return info
    filas = tabla.find_all('tr')
    if len(filas) < 2:
        print(f'⚠️ Sin filas en resultados: {title}')
        return info
    primera = filas[1].find('a')
    if not primera or 'href' not in primera.attrs:
        print(f'⚠️ Sin enlace al detalle: {title}')
        return info

    detalle_url = 'https://www.scimagojr.com/' + primera['href']
    r2 = requests.get(detalle_url, headers=HEADERS)
    soup2 = BeautifulSoup(r2.text, 'html.parser')

    # 2) Site web (si existe un enlace externo)
    ext = soup2.find('a', class_='external-link')
    if ext and 'href' in ext.attrs:
        info['site_web'] = ext['href'].strip()

    # 3) H-Index
    hi_tag = soup2.find('div', string='H index')
    if hi_tag:
        sib = hi_tag.find_next_sibling('div')
        if sib:
            info['h_index'] = sib.text.strip()

    # 4) Subject Area and category
    dt = soup2.find('dt', string=lambda t: t and 'Subject Area and category' in t)
    if dt:
        dd = dt.find_next_sibling('dd')
        if dd:
            # separa por comas
            info['subject_area_and_category'] = [s.strip() for s in dd.text.split(',')]

    # 5) Publisher, ISSN y Publication Type (en el bloque dl#journalinfo)
    ji = soup2.find('div', id='journalinfo')
    if ji:
        dl = ji.find('dl')
        if dl:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            for key, val in zip(dts, dds):
                k = key.text.strip().lower()
                v = val.text.strip()
                if 'publisher' in k:
                    info['publisher'] = v
                elif 'issn' in k:
                    # si hay varios, puedes concatenar
                    info['issn'] = v
                elif 'type' == k:
                    info['publication_type'] = v

    # 6) Widget (el código embebible)
    widget = soup2.find('textarea', id='scimagoWidget')
    if widget:
        info['widget'] = widget.text.strip()

    return info

def main():
    # Cargar JSON de entrada y existentes
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        revistas = json.load(f)
    enriched = load_existing()

    total = len(revistas)
    print(f'Se van a procesar {total} revistas (ya hay {len(enriched)} cacheadas).')

    for i, (title, base) in enumerate(revistas.items(), start=1):
        if title in enriched:
            print(f'[{i}/{total}] ✔️ {title} (cached)')
            continue
        print(f'[{i}/{total}] Procesando: {title}...')
        info = fetch_journal_info(title)
        enriched[title] = {**base, **info}
        # Guardamos tras cada uno para poder reiniciar si interrumpe
        save_output(enriched)
        time.sleep(1)   # educadamente esperamos 1s

    print('✅ Scraping completado.')
    print(f'Archivo JSON enriquecido en: {OUTPUT_JSON}')

if __name__ == '__main__':
    main()