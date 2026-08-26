import os
import requests

URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_FILE = "cache/catalogue-page-1.html"
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/irene06/flyrank-polite-scraper)"

def fetch_catalogue_page():
    # Asegurarnos de que la carpeta de caché existe
    os.makedirs("cache", exist_ok=True)
    
    # Comprobar si ya existe en caché para desarrollo educado
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"CACHE HIT: Loaded from {CACHE_FILE} (Size: {len(content)} bytes)")
        return content

    # Si no está en caché, hacemos la petición real con politeness
    print(f"FETCH: Requesting {URL}")
    headers = {"User-Agent": USER_AGENT}
    
    try:
        # Timeout configurado para no colgarse para siempre
        response = requests.get(URL, headers=headers, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None

    # Verificar estrictamente el código 200
    if response.status_code != 200:
        print(f"Failed to fetch. Status code: {response.status_code}")
        return None

    # Guardar en caché
    html_content = response.text
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"FETCH SUCCESS: Saved to {CACHE_FILE} (Size: {len(html_content)} bytes)")
    return html_content

if __name__ == "__main__":
    fetch_catalogue_page()