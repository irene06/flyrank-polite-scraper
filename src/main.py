import os
import time
from datetime import datetime
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
            return f.read(), True

    time.sleep(0.5) # Pausa de cortesía
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
    unique_book_data = [] # Guardará tuplas de (book_url, source_page_url)
    seen_urls = set()
    
    current_url = START_URL
    page_num = 1

    while current_url and page_num <= 3:
        cache_filename = f"cache/catalogue-page-{page_num}.html"
        html_content, _ = fetch_and_cache(current_url, cache_filename)
        
        if not html_content:
            break

        soup = BeautifulSoup(html_content, "html.parser")
        
        # Encontrar libros y su página de origen
        book_pods = soup.select("article.product_pod h3 a")
        for book_a in book_pods:
            relative_href = book_a.get("href")
            absolute_url = urljoin(current_url, relative_href)
            if absolute_url not in seen_urls:
                seen_urls.add(absolute_url)
                unique_book_data.append({
                    "book_url": absolute_url,
                    "source_page": current_url
                })

        next_button = soup.select_one("li.next a")
        if next_button:
            next_href = next_button.get("href")
            current_url = urljoin(current_url, next_href)
            page_num += 1
        else:
            current_url = None

    return unique_book_data

def extract_book_details(book_info, index):
    book_url = book_info["book_url"]
    source_page = book_info["source_page"]
    
    # Archivo de caché individual para cada libro para evitar re-descargas
    cache_filename = f"cache/book-{index}.html"
    html_content, _ = fetch_and_cache(book_url, cache_filename)
    
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Título
    title_el = soup.select_one("div.product_main h1")
    title = title_el.get_text(strip=True) if title_el else "N/A"

    # 2. Precio
    price_el = soup.select_one("div.product_main p.price_color")
    price = price_el.get_text(strip=True) if price_el else "N/A"

    # 3. Disponibilidad
    availability_el = soup.select_one("div.product_main p.instock.availability")
    availability = availability_el.get_text(strip=True) if availability_el else "N/A"

    # 4. Calificación (Rating) - viene en una clase CSS tipo "star-rating Three"
    rating_el = soup.select_one("div.product_main p.star-rating")
    rating = "N/A"
    if rating_el:
        classes = rating_el.get("class", [])
        # La segunda clase usualmente indica el número en texto (One, Two, Three...)
        rating = [c for c in classes if c != "star-rating"]
        rating = rating[0] if rating else "N/A"

    # 5. Descripción
    # En books.toscrape, la descripción suele estar en un div con id "product_description" seguido de un <p>
    desc_el = soup.select_one("#product_description ~ p")
    description = desc_el.get_text(strip=True) if desc_el else "N/A"

    record = {
        "title": title,
        "url": book_url,
        "price": price,
        "availability": availability,
        "rating": rating,
        "description": description,
        "source_page": source_page,
        "scraped_at": datetime.utcnow().isoformat() + "Z"
    }

    return record

def main():
    print("--- INICIANDO DESCUBRIMIENTO DE CATÁLOGO ---")
    books_meta = discover_catalogue_and_books()
    print(f"Libros descubiertos: {len(books_meta)}")

    print("\n--- INICIANDO EXTRACCIÓN DE REGISTROS DE LIBROS ---")
    raw_records = []
    for idx, meta in enumerate(books_meta, start=1):
        record = extract_book_details(meta, idx)
        if record:
            raw_records.append(record)

    print("\n--- CHECKPOINT STAGE 3 ---")
    print(f"Total registros extraídos: {len(raw_records)}")
    if raw_records:
        print("Ejemplo de registro extraído:")
        print(raw_records[0])

if __name__ == "__main__":
    main()