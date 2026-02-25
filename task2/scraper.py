"""
scraper.py – Scrapes 20-30 Samsung phone specs from GSMArena
             and stores them in PostgreSQL.

Run:
    python scraper.py
"""

import logging
import re
import time

import requests
from bs4 import BeautifulSoup

from config import SCRAPE_TARGET
from database import initialize_db, upsert_phone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

BASE_URL = "https://www.gsmarena.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class GSMArenaPhoneScraper:
    """
    Scrapes Samsung phone listings and detail pages from GSMArena,
    extracts key specifications, and stores results in PostgreSQL.
    """

    def __init__(self, target_count: int = SCRAPE_TARGET):
        self.target_count = target_count
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    # ------------------------------------------------------------------
    # Step 1 – Collect phone links from the Samsung listing pages
    # ------------------------------------------------------------------
    def get_phone_links(self) -> list[dict]:
        """Return up to *target_count* {name, url} dicts from GSMArena."""
        links = []
        page  = 1

        while len(links) < self.target_count:
            url = (
                f"{BASE_URL}/samsung-phones-9.php"
                if page == 1
                else f"{BASE_URL}/samsung-phones-9-{page}.php"
            )
            logger.info("Listing page %d: %s", page, url)
            try:
                resp = self.session.get(url, timeout=15)
                if resp.status_code != 200:
                    logger.warning("HTTP %d – stopping listing crawl.", resp.status_code)
                    break

                soup   = BeautifulSoup(resp.text, "html.parser")
                makers = soup.find("div", class_="makers")
                if not makers:
                    logger.warning("No 'makers' div found – stopping.")
                    break

                for li in makers.find_all("li"):
                    a = li.find("a")
                    if not a:
                        continue
                    href   = a.get("href", "")
                    strong = a.find("strong")
                    name   = (
                        strong.get_text(separator=" ", strip=True)
                        if strong
                        else a.get_text(strip=True)
                    )
                    if href and name:
                        links.append({"name": name, "url": f"{BASE_URL}/{href}"})
                        if len(links) >= self.target_count:
                            break

                page += 1
                time.sleep(1.0)

            except Exception as exc:
                logger.error("Error on listing page %d: %s", page, exc)
                break

        return links[: self.target_count]

    # ------------------------------------------------------------------
    # Step 2 – Scrape the spec page for a single phone
    # ------------------------------------------------------------------
    def scrape_phone(self, phone_info: dict) -> dict | None:
        """Parse a GSMArena phone detail page and return a spec dict."""
        try:
            resp = self.session.get(phone_info["url"], timeout=15)
            if resp.status_code != 200:
                logger.warning("HTTP %d for %s", resp.status_code, phone_info["name"])
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            # ── Parse all spec tables ──────────────────────────────────
            specs_by_cat: dict[str, dict[str, str]] = {}
            full_lines   = [f"Model: {phone_info['name']}"]

            specs_div = soup.find("div", id="specs-list")
            if specs_div:
                for table in specs_div.find_all("table"):
                    th       = table.find("th")
                    category = th.get_text(strip=True) if th else "Other"
                    specs_by_cat.setdefault(category, {})

                    for tr in table.find_all("tr"):
                        ttl = tr.find("td", class_="ttl")
                        nfo = tr.find("td", class_="nfo")
                        if ttl and nfo:
                            spec  = ttl.get_text(strip=True)
                            value = nfo.get_text(separator=" ", strip=True)
                            specs_by_cat[category][spec] = value
                            full_lines.append(f"{category} – {spec}: {value}")

            # ── Extract key fields ─────────────────────────────────────
            launch       = specs_by_cat.get("Launch", {})
            release_date = launch.get("Announced", launch.get("Status", "N/A"))

            display_info  = specs_by_cat.get("Display", {})
            display_parts = [display_info[k] for k in ("Type", "Size") if k in display_info]
            display       = " / ".join(display_parts) if display_parts else "N/A"

            battery_info = specs_by_cat.get("Battery", {})
            battery      = battery_info.get("Capacity", battery_info.get("Type", "N/A"))

            # Main camera – try common category names
            camera_info: dict = {}
            for cat_name in ("Main Camera", "Dual Camera", "Triple Camera", "Quad Camera"):
                if cat_name in specs_by_cat:
                    camera_info = specs_by_cat[cat_name]
                    break
            if not camera_info:
                for cat_name, cat_data in specs_by_cat.items():
                    if "camera" in cat_name.lower() and "selfie" not in cat_name.lower():
                        camera_info = cat_data
                        break
            camera = (
                "; ".join(f"{k}: {v}" for k, v in list(camera_info.items())[:4])
                if camera_info
                else "N/A"
            )

            memory_info  = specs_by_cat.get("Memory", {})
            internal_raw = memory_info.get("Internal", "")
            ram_match     = re.search(r"(\d+\s*GB\s*RAM)", internal_raw, re.IGNORECASE)
            ram           = ram_match.group(1) if ram_match else "N/A"
            storage_match = re.search(r"^(\d+\s*(?:GB|TB))", internal_raw)
            storage       = storage_match.group(1) if storage_match else (internal_raw[:100] or "N/A")

            misc_info = specs_by_cat.get("Misc", {})
            price     = misc_info.get("Price", "N/A")

            return {
                "model_name":   phone_info["name"],
                "release_date": str(release_date)[:200],
                "display":      str(display)[:500],
                "battery":      str(battery)[:200],
                "camera":       str(camera)[:1000],
                "ram":          str(ram)[:200],
                "storage":      str(storage)[:200],
                "price":        str(price)[:200],
                "full_specs":   "\n".join(full_lines),
            }

        except Exception as exc:
            logger.error("Error scraping %s: %s", phone_info["name"], exc)
            return None

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def run(self):
        """Run the full scraping pipeline."""
        logger.info("Samsung Phone Scraper  |  Target: %d phones", self.target_count)

        logger.info("Step 1 – Initializing database...")
        initialize_db()

        logger.info("Step 2 – Collecting phone links from GSMArena...")
        phone_links = self.get_phone_links()
        logger.info("Found %d phone links.", len(phone_links))

        logger.info("Step 3 – Scraping phone specs and saving to PostgreSQL...")
        success = 0
        for i, phone_info in enumerate(phone_links, 1):
            logger.info("[%d/%d] %s", i, len(phone_links), phone_info["name"])
            data = self.scrape_phone(phone_info)
            if data:
                upsert_phone(data)
                success += 1
            time.sleep(1.5)  # Respectful rate limiting

        logger.info("Done: %d/%d phones saved to PostgreSQL.", success, len(phone_links))


# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    scraper = GSMArenaPhoneScraper()
    scraper.run()
