import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
from urllib.parse import urljoin

# -----------------------------------
# NEWS SOURCES & CATEGORY PAGES
# -----------------------------------
sources = {
    "The Indian Express": {
        "Politics": "https://indianexpress.com/section/political-pulse/",
        "Sports": "https://indianexpress.com/section/sports/",
        "Business & Economy": "https://indianexpress.com/section/business/",
        "Technology": "https://indianexpress.com/section/technology/",
        "Entertainment": "https://indianexpress.com/section/entertainment/",
        "National": "https://indianexpress.com/section/india/",
        "Science": "https://indianexpress.com/section/technology/science/"
    },
    "The Hindu": {
        "Politics": "https://www.thehindu.com/news/national/politics/",
        "Sports": "https://www.thehindu.com/sport/",
        "Business & Economy": "https://www.thehindu.com/business/",
        "Technology": "https://www.thehindu.com/sci-tech/",
        "Entertainment": "https://www.thehindu.com/entertainment/",
        "Science": "https://www.thehindu.com/sci-tech/science/"
    },
    "NDTV": {
        "Politics": "https://www.ndtv.com/topic/indian-politics",
        "Sports": "https://sports.ndtv.com",
        "Business & Economy": "https://www.ndtv.com/business",
        "Technology": "https://www.ndtv.com/technology",
        "Entertainment": "https://www.ndtv.com/entertainment",
        "National": "https://www.ndtv.com/india-news",
        "Science": "https://www.ndtv.com/science"
    },
    "The Times of India": {
        "Politics": "https://timesofindia.indiatimes.com/india/politics",
        "Sports": "https://timesofindia.indiatimes.com/sports",
        "Business & Economy": "https://timesofindia.indiatimes.com/business",
        "Technology": "https://timesofindia.indiatimes.com/technology",
        "Entertainment": "https://timesofindia.indiatimes.com/entertainment",
        "Science": "https://timesofindia.indiatimes.com/home/science"
    },
    "Hindustan Times": {
        "Politics": "https://www.hindustantimes.com/india-news",
        "Sports": "https://www.hindustantimes.com/sports",
        "Business & Economy": "https://www.hindustantimes.com/business",
        "Technology": "https://www.hindustantimes.com/technology",
        "Entertainment": "https://www.hindustantimes.com/entertainment",
        "Science": "https://www.hindustantimes.com/science"
    },
    "The Economic Times": {
        "Politics": "https://economictimes.indiatimes.com/news/politics-nation",
        "Business & Economy": "https://economictimes.indiatimes.com/news/economy",
        "Technology": "https://economictimes.indiatimes.com/tech",
        "Markets": "https://economictimes.indiatimes.com/markets"
    },
    "Business Standard": {
        "Business & Economy": "https://www.business-standard.com/category/economy-policy-0101.htm",
        "Markets": "https://www.business-standard.com/category/markets-10201.htm",
        "Technology": "https://www.business-standard.com/category/technology-1040101.htm"
    },
    "Mint": {
        "Business & Economy": "https://www.livemint.com/news/india",
        "Markets": "https://www.livemint.com/market",
        "Politics": "https://www.livemint.com/politics"
    },
    "Scroll.in": {
        "Politics": "https://scroll.in/topic/6/politics",
        "Sports": "https://scroll.in/topic/8/sports",
        "Business & Economy": "https://scroll.in/topic/10/business-economy",
        "Technology": "https://scroll.in/topic/116/technology",
        "Culture": "https://scroll.in/topic/25/culture"
    }
}

# -----------------------------------
# SITE-SPECIFIC SCRAPER
# -----------------------------------
def scrape_articles(base_url, category, source, pages=5, limit_per_page=40):
    articles = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for page in range(1, pages + 1):
        url = base_url
        # Pagination rules (basic)
        if "indianexpress.com" in base_url and page > 1:
            url = f"{base_url}page/{page}/"
        elif "hindustantimes.com" in base_url and page > 1:
            url = f"{base_url}/page/{page}"
        elif "ndtv.com" in base_url and page > 1:
            url = f"{base_url}/page-{page}"
        elif "timesofindia.indiatimes.com" in base_url and page > 1:
            url = f"{base_url}?page={page}"
        elif "business-standard.com" in base_url and page > 1:
            url = f"{base_url}?p={page}"
        elif "livemint.com" in base_url and page > 1:
            url = f"{base_url}/page-{page}"
        elif "scroll.in" in base_url and page > 1:
            url = f"{base_url}?page={page}"

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")

            # Generalized selectors (customize per site if needed)
            nodes = soup.find_all(["h2", "h3", "div", "span", "a"])
            for n in nodes:
                a = n.find("a") if n.name != "a" else n
                if a:
                    title = a.get_text(strip=True)
                    link = urljoin(base_url, a.get("href"))
                    # Filter junk links
                    if not title or len(title) < 15:
                        continue
                    if "Opens in new window" in title or "login" in link or "facebook" in link:
                        continue
                    if not link.startswith("http"):
                        continue
                    articles.append({
                        "title": title,
                        "date": "2025-09-07",  # placeholder
                        "category": category,
                        "source": source,
                        "url": link
                    })
                    if len(articles) >= pages * limit_per_page:
                        return articles

        except Exception as e:
            print("Error scraping", url, e)

        time.sleep(random.uniform(1, 3))  # polite delay

    return articles

# -----------------------------------
# BUILD DATASET
# -----------------------------------
dataset = []
for source, cats in sources.items():
    for cat, url in cats.items():
        print(f"Scraping {source} - {cat}")
        dataset.extend(scrape_articles(url, cat, source, pages=5, limit_per_page=40))

# Deduplicate by URL
seen = set()
unique_dataset = []
for row in dataset:
    if row["url"] not in seen:
        seen.add(row["url"])
        unique_dataset.append(row)

# Add IDs
for idx, row in enumerate(unique_dataset, start=1):
    row["id"] = idx

# Save CSV
df = pd.DataFrame(unique_dataset, columns=["id", "title", "date", "category", "source", "url"])
df.to_csv("indian_news_dataset.csv", index=False, encoding="utf-8-sig")
print("Saved indian_news_dataset.csv with", len(df), "rows.")
