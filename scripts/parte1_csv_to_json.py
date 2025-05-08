import os
import csv
import json

def main():
    # Definir rutas base
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    areas_dir = os.path.join(base_dir, 'datos', 'csv', 'areas')
    cats_dir = os.path.join(base_dir, 'datos', 'csv', 'catalogos')
    output_path = os.path.join(base_dir, 'datos', 'json', 'revistas.json')

    revistas = {}

    # --- 1) Procesar CSV de Áreas ---
    for fname in os.listdir(areas_dir):
        if not fname.lower().endswith('.csv'):
            continue
        path = os.path.join(areas_dir, fname)
        with open(path, newline='', encoding='latin-1') as f:
            reader = csv.reader(f)
            # Saltar encabezado si existe
            next(reader, None)
            for row in reader:
                if len(row) < 2:
                    continue
                titulo = row[0].strip().lower()
                area   = row[1].strip().upper()
                if not titulo:
                    continue
                # Inicializar entrada si no existe
                if titulo not in revistas:
                    revistas[titulo] = {'areas': [], 'catalogos': []}
                # Agregar área sin duplicados
                if area and area not in revistas[titulo]['areas']:
                    revistas[titulo]['areas'].append(area)

    # --- 2) Procesar CSV de Catálogos ---
    for fname in os.listdir(cats_dir):
        if not fname.lower().endswith('.csv'):
            continue
        path = os.path.join(cats_dir, fname)
        with open(path, newline='', encoding='latin-1') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) < 2:
                    continue
                titulo   = row[0].strip().lower()
                catalogo = row[1].strip().upper()
                if not titulo:
                    continue
                if titulo not in revistas:
                    revistas[titulo] = {'areas': [], 'catalogos': []}
                if catalogo and catalogo not in revistas[titulo]['catalogos']:
                    revistas[titulo]['catalogos'].append(catalogo)

    # --- 3) Volcar a JSON ---
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(revistas, f, ensure_ascii=False, indent=2)

    print(f'✅ JSON generado en: {output_path}')
    print(f'Total revistas: {len(revistas)}')

if __name__ == '__main__':
    main()
