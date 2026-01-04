import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"

def scrape_quotes(max_pages: int = 5, delay: float = 0.5):
    results = []
    url = f"{BASE_URL}/page/1/"

    for page in range(1, max_pages + 1):
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        quotes = soup.select(".quote")
        if not quotes:
            break

        for q in quotes:
            text = q.select_one(".text").get_text(strip=True)
            author = q.select_one(".author").get_text(strip=True)
            tags = [t.get_text(strip=True) for t in q.select(".tags .tag")]
            results.append({
                "text": text,
                "author": author,
                "tags": ", ".join(tags),
                "source_page": page
            })

        next_link = soup.select_one("li.next a")
        if not next_link:
            break

        url = BASE_URL + next_link.get("href")
        time.sleep(delay)

    return results

if __name__ == "__main__":
    data = scrape_quotes(max_pages=5)
    print("Scraped:", len(data))
    print(data[0] if data else "No data")
