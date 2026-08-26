import os
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/irene06/flyrank-polite-scraper)"

def fetch_and_cache(url, filename):
    os.makedirs("cache", exist_ok=True)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read(), True # True indica que vino de caché

    # Esperar al menos 500ms entre peticiones reales por politeness
    time.sleep(0.5)
    print(f"FETCH: Requesting {url}")
    headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Error during request {url}: {e}")
        return None, False

    if response.status_code != 200:
        print(f"Failed to fetch {url}. Status code: {response.status_code}")
        return None, False

    html_content = response.text
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_content, False

def discover_catalogue_and_books():
    catalogue_pages_count = 0
    unique_book_urls = set()
    
    current_url = START_URL
    page_num = 1

    # Queremos recorrer las 3 primeras páginas del catálogo
    while current_url and page_num <= 3:
        cache_filename = f"cache/catalogue-page-{page_num}.html"
        html_content, from_cache = fetch_and_cache(current_url, cache_filename)
        
        if not html_content:
            break

        catalogue_pages_count += 1
        source_label = "CACHE HIT" if from_cache else "FETCH SUCCESS"
        print(f"{source_label}: Page {page_num} loaded.")

        # Parsear con Beautiful Soup
        soup = BeautifulSoup(html_content, "html.parser")

        # Extraer enlaces de los libros en esta página
        # En Books to Scrape, cada libro está en <article class="product_pod"> -> <h3> -> <a>
        book_pods = soup.select("article.product_pod h3 a")
        for book_a in book_pods:
            relative_href = book_a.get("href")
            # Convertir URL relativa a absoluta de forma segura usando urljoin
            absolute_url = urljoin(current_url, relative_href)
            unique_book_urls.add(absolute_url)

        # Buscar el enlace "next" para la siguiente página de catálogo
        next_button = soup.select_one("li.next a")
        if next_button:
            next_href = next_button.get("href")
            current_url = urljoin(current_url, next_href)
            page_num += 1
        else:
            current_url = None

    print("\n--- CHECKPOINT STAGE 2 ---")
    print(f"catalogue_pages = {catalogue_pages_count}")
    print(f"discovered = {len(unique_book_urls)}")
    print(f"unique_urls = {len(unique_book_urls)}")

    return unique_book_urls

if __name__ == "__main__":
    discover_catalogue_and_books()