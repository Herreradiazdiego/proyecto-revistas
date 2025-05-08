# Catálogo de Revistas – Universidad de Sonora

**Integrantes:**  
- Diego Herrera Díaz  
- Carlos Sebastián Sapién Cano  

**Asistente digital utilizado:** Durante el desarrollo de este proyecto se utilizó Github Copilot como asistente para generación de código y revisión de lógica para agilizar procesos.

---

## Requisitos previos

- Python 3.10 o superior  
- Git  
- (Opcional) Un entorno virtual Python (`venv`) para aislar dependencias

---

## Instalación

1. Clona este repositorio y sitúate en él:  
   ```bash
   git clone https://github.com/Herreradiazdiego/proyecto-revistas.git
   cd proyecto-revistas


2. Se crea y activa un entorno virtual (Powershell)
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\.venv\Scripts\Activate.ps1


3. Se instalan dependencias
pip install -r requirements.txt


4. Se genera JSON base
python scripts/parte1_csv_to_json.py


5. Scrapear SCImago
python scripts/parte2_scraper.py


6. Execucion en la web
cd webapp
python app.py
