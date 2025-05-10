import os
import json
import requests
from bs4 import BeautifulSoup

# ── Rutas ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_JSON   = os.path.join(BASE_DIR, 'datos', 'json', 'revistas.json')
OUTPUT_JSON  = os.path.join(BASE_DIR, 'datos', 'json', 'revistas_scimago.json')
CACHE        = {}

def scrape_scimagojr(title):
    """
    Visita SCImago y extrae:
      - site_web
      - h_index
      - subject_area_and_category
      - publisher
      - issn
      - widget
      - publication_type
    """
    slug = title.replace(' ', '%20')
    url = f'https://www.scimagojr.com/journalsearch.php?q={slug}'
    try:
        resp = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Site web
        link = soup.select_one('.search_results .result_title a')
        site_web = link['href'] if link and link.has_attr('href') else ''

        # H-Index
        h = soup.select_one('.search_results tbody tr td:nth-of-type(3)')
        h_index = h.text.strip() if h else ''

        # Publisher
        pub = soup.select_one('.search_results tbody tr td:nth-of-type(4)')
        publisher = pub.text.strip() if pub else ''

        # ISSN
        issn_el = soup.find(text='Print ISSN:')
        issn = issn_el.find_next().text.strip() if issn_el else ''

        # Subject area and category
        subj_list = [li.text.strip() for li in soup.select('.search_results tbody tr td:nth-of-type(2) ul li')]
        subject_area_and_category = subj_list

        # Widget (iframe HTML)
        widget = f'<iframe src="https://www.scimagojr.com/journalwidget.php?issn={issn}" width="100%" height="300"></iframe>' if issn else ''

        # Publication type (no siempre presente)
        pubtype_el = soup.find(text='Type:')
        publication_type = pubtype_el.find_next().text.strip() if pubtype_el else ''

        return {
            "site_web": site_web,
            "h_index": h_index,
            "subject_area_and_category": subject_area_and_category,
            "publisher": publisher,
            "issn": issn,
            "widget": widget,
            "publication_type": publication_type
        }
    except Exception:
        return {
            "site_web": "",
            "h_index": "",
            "subject_area_and_category": [],
            "publisher": "",
            "issn": "",
            "widget": "",
            "publication_type": ""
        }

def scrape_resurchify(slug):
    """
    Visita Resurchify y extrae:
      - altmetric_score
      - trending_rank
      - subject_tags
    """
    url = f'https://www.resurchify.com/journal/{slug}.html'
    try:
        resp = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Selector de ejemplo; ajusta según el HTML real
        alt_tag = soup.select_one('#impactScore') or soup.select_one('.altmetric-score .value')
        tr_tag  = soup.select_one('#trendingRank') or soup.select_one('.trending-rank .value')
        tags_el = soup.select('.subject-tags li')

        return {
            "altmetric_score": alt_tag.text.strip() if alt_tag else "",
            "trending_rank" : tr_tag.text.strip()  if tr_tag else "",
            "subject_tags"  : [li.text.strip() for li in tags_el]
        }
    except Exception:
        return {
            "altmetric_score": "",
            "trending_rank": "",
            "subject_tags": []
        }

if __name__ == '__main__':
    # Cargo el JSON base
    with open(INPUT_JSON, encoding='utf-8') as f:
        revistas = json.load(f)

    enriched = {}
    total = len(revistas)
    print(f"Se van a procesar {total} revistas (ya hay {len(CACHE)} cacheadas).")

    for i, (titulo, info) in enumerate(revistas.items(), 1):
        print(f"[{i}/{total}] Procesando: {titulo}...")
        scim = scrape_scimagojr(titulo)
        # slug para Resurchify
        slug = titulo.replace(' ', '-').lower()
        resur = scrape_resurchify(slug)

        # Combino todo
        enriched[titulo] = {
            "areas": info['areas'],
            "catalogos": info['catalogos'],
            **scim,
            "resurchify": resur
        }

    # Escribo JSON enriquecido
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"Scraping completado.")
    print(f"Archivo JSON enriquecido en: {OUTPUT_JSON}")