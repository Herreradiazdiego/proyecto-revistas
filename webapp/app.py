import os
import json
from flask import Flask, render_template, request, abort

# ── Configuración ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'datos', 'json', 'revistas_scimago.json')

app = Flask(__name__)

def load_data():
    with open(DATA_PATH, encoding='utf-8') as f:
        return json.load(f)

# ── Rutas ──
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/area')
def listar_areas():
    data = load_data()
    areas = sorted({a for rev in data.values() for a in rev['areas']})
    return render_template('areas.html', areas=areas)

@app.route('/area/<area>')
def ver_area(area):
    data = load_data()
    subset = {t: v for t, v in data.items() if area in v['areas']}
    return render_template('tabla.html',
                           titulo=f'Área: {area}',
                           items=subset)

@app.route('/catalogo')
def listar_catalogos():
    data = load_data()
    catalogos = sorted({c for rev in data.values() for c in rev['catalogos']})
    return render_template('catalogos.html', catalogos=catalogos)

@app.route('/catalogo/<cat>')
def ver_catalogo(cat):
    data = load_data()
    subset = {t: v for t, v in data.items() if cat in v['catalogos']}
    return render_template('tabla.html',
                           titulo=f'Catálogo: {cat}',
                           items=subset)

@app.route('/explorar')
def explorar():
    abecedario = [chr(c) for c in range(ord('A'), ord('Z')+1)]
    return render_template('explorar.html', letras=abecedario)

@app.route('/explorar/<letra>')
def ver_letra(letra):
    data = load_data()
    subset = {t: v for t, v in data.items() if t.upper().startswith(letra.upper())}
    return render_template('tabla.html',
                           titulo=f'Revistas que empiezan con "{letra.upper()}"',
                           items=subset)

@app.route('/buscar')
def buscar():
    q = request.args.get('q', '').strip().lower()
    if not q:
        return render_template('buscar.html', items={}, q=q)
    data = load_data()
    palabras = q.split()
    resultado = {}
    for t, v in data.items():
        if any(p in t for p in palabras):
            resultado[t] = v
    return render_template('buscar.html', items=resultado, q=q)

@app.route('/revista/<titulo>')
def ver_revista(titulo):
    data = load_data()
    rev = data.get(titulo)
    if rev is None:
        abort(404)
    return render_template('revista.html', titulo=titulo, rev=rev)

@app.route('/creditos')
def creditos():
    autores = [
        'Diego Herrera Díaz',
        'Carlos Sebastián Sapién Cano'
    ]
    return render_template('creditos.html', autores=autores)

if __name__ == '__main__':
    app.run(debug=True)