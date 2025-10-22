import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

DB_NAME = 'database.db'


def create_db():
    """Create SQLite database and jobs table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT UNIQUE,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()


def scrape_ssc():
    """Scrape job notifications (PDFs) from the SSC official website."""
    url = "https://ssc.gov.in"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Error fetching SSC website:", e)
        return []

    soup = BeautifulSoup(response.text, 'lxml')
    jobs = []

    for link in soup.find_all('a', href=True):
        text = link.text.strip()
        href = link['href']

        # Filter for job notification files or relevant job pages
        if 'pdf' in href.lower() or 'notice' in href.lower():
            # Fix relative links
            if href.startswith('/'):
                full_link = url + href
            elif href.startswith('http'):
                full_link = href
            else:
                full_link = f"{url}/{href}"

            if text:
                jobs.append((text, full_link))

    return jobs


def save_jobs(jobs):
    """Insert scraped jobs into SQLite database (avoid duplicates)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for title, link in jobs:
        cursor.execute('''
            INSERT OR IGNORE INTO jobs (title, link, date)
            VALUES (?, ?, ?)
        ''', (title, link, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def run():
    """Run complete scrape and save process."""
    print("Starting SSC job scraper...")
    create_db()
    jobs = scrape_ssc()

    if jobs:
        save_jobs(jobs)
        print(f"✅ Successfully saved {len(jobs)} job records.")
    else:
        print("⚠️ No jobs found or scraping failed.")


if __name__ == '__main__':
    run()
import schedule, time
schedule.every(6).hours.do(run)

while True:
    schedule.run_pending()
    time.sleep(60)
