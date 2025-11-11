# scrape_and_export.py
import asyncio
import csv
import json
import time
import os
from pathlib import Path
from typing import List, Dict
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler

# Configuration
BASE_URL = "https://www.skiwebshop.fr/femmes/tenues-de-ski/sous-pulls-de-ski"
CSS_SELECTOR = "li.product-item"
OUTPUT_DIR = Path("exports")
OUTPUT_DIR.mkdir(exist_ok=True)


async def scrape_page(crawler, url: str) -> List[Dict]:
    """Scrape une seule page et retourne les produits"""
    print(f"   → Chargement {url}...")
    result = await crawler.arun(
        url=url,
        wait_for=None,
        page_timeout=30000,
        js_code=["await new Promise(r => setTimeout(r, 2000));"],
        disable_images=True,
    )

    if not result.success or not result.html:
        print(f"⚠️ Échec du chargement : {url}")
        return []

    soup = BeautifulSoup(result.html, "html.parser")
    products = []

    for li in soup.select(CSS_SELECTOR):
        try:
            # Modèle (ex: "Fwc'Cruz pull de ski femmes")
            h3 = li.select_one("h3")
            modele = h3.get_text(strip=True) if h3 else ""
            if not modele:
                continue

            # Marque (ex: "O'Neill")
            brand_link = li.select_one("section > a[href]:not([title])")
            marque = brand_link.get_text(strip=True) if brand_link else ""

            # Prix (ex: "46,90 €" → "46.90")
            price_span = li.find("span", string=lambda t: t and "€" in t)
            prix = ""
            if price_span:
                text = price_span.get_text().strip()
                import re
                match = re.search(r"([\d,\.]+)", text.replace("\u00A0", " "))
                if match:
                    prix = match.group(1).replace(",", ".")

            # Réduction (ex: "-6%")
            reduction_p = li.select_one("p")
            reduction = reduction_p.get_text(strip=True) if reduction_p else ""

            products.append({
                "marque": marque,
                "modele": modele,
                "prix": prix,
                "reduction": reduction,
            })
        except Exception:
            continue

    return products


async def scrape_all_pages() -> List[Dict]:
    """Scrape toutes les pages (jusqu’à disparition des produits)"""
    print("🚀 Démarrage du scraping multi-pages...")
    all_products = []
    page = 1
    max_pages = 50

    async with AsyncWebCrawler(
        browser_type="chromium",
        headless=True,
    ) as crawler:
        while page <= max_pages:
            sep = "&" if "?" in BASE_URL else "?"
            url = f"{BASE_URL}{sep}p={page}"

            products = await scrape_page(crawler, url)
            
            if not products:
                if page == 1:
                    print("❌ Aucun produit trouvé sur la première page.")
                break

            print(f"   +{len(products)} produits (page {page})")
            all_products.extend(products)
            page += 1
            await asyncio.sleep(1)

    return all_products


def save_to_json(data: List[Dict], filepath: Path):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON : {filepath}")


def save_to_csv(data: List[Dict], filepath: Path):
    if not data:
        print("⚠️ Aucune donnée à exporter en CSV.")
        return
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["marque", "modele", "prix", "reduction"])
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ CSV  : {filepath}")


def save_to_excel(data: List[Dict], filepath: Path):
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False, engine="openpyxl")
        print(f"✅ Excel: {filepath}")
    except ImportError:
        print("⚠️ pandas/openpyxl non installé → export Excel ignoré.")
        print("   Installez avec : pip install pandas openpyxl")


async def main():
    products = await scrape_all_pages()

    if not products:
        print("❌ Aucun produit extrait.")
        return

    print(f"\n🎉 {len(products)} produits collectés (bruts).")

    # Dé-duplication : un produit = (marque + modèle)
    seen = set()
    unique = []
    for p in products:
        key = (p["marque"], p["modele"])
        if key not in seen:
            seen.add(key)
            unique.append(p)
    print(f"   → {len(unique)} modèles uniques")

    # ✅ Timestamp compatible partout
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    base = OUTPUT_DIR / f"sous_pulls_ski_{len(unique)}_{timestamp}"

    # Export
    save_to_json(unique, base.with_suffix(".json"))
    save_to_csv(unique, base.with_suffix(".csv"))
    save_to_excel(unique, base.with_suffix(".xlsx"))

    # Stats
    prix_valides = [float(p["prix"]) for p in unique if p["prix"]]
    if prix_valides:
        moy = sum(prix_valides) / len(prix_valides)
        print(f"\n💵 Prix moyen : {moy:.2f} €")
        print(f"📉 Min : {min(prix_valides):.2f} € | 📈 Max : {max(prix_valides):.2f} €")

    print(f"\n📁 Fichiers dans : {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())