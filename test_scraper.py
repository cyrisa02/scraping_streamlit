# test_scraper_full.py
import asyncio
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler

URL = "https://www.skiwebshop.fr/femmes/tenues-de-ski/sous-pulls-de-ski"

async def scrape_products():
    print("🔍 Extraction fiable (modèle + prix + marque + réduction)...")
    
    async with AsyncWebCrawler(
        browser_type="chromium",
        headless=True,
        disable_images=False,
    ) as crawler:
        result = await crawler.arun(
            url=URL,
            wait_for=None,
            page_timeout=30000,
            js_code=["await new Promise(r => setTimeout(r, 2500));"],
            magic=False,  # on veut le HTML brut, pas cleaned_html
        )

        if not result.success or not result.html:
            print("❌ Échec.")
            return []

        soup = BeautifulSoup(result.html, "html.parser")
        products = []

        for li in soup.select("li.product-item"):  # ✅ Sélecteur exact
            try:
                # 🔹 Modèle
                h3 = li.select_one("h3")
                modele = h3.get_text(strip=True) if h3 else ""

                # 🔹 Marque
                brand_link = li.select_one("section > a[href]:not([title])")
                marque = brand_link.get_text(strip=True) if brand_link else ""

                # 🔹 Prix : cherche le 1er span contenant "€"
                price_span = li.find("span", string=lambda t: t and "€" in t)
                prix = ""
                if price_span:
                    prix_text = price_span.get_text().strip()
                    # Extrait "46,90" de "46,90 €"
                    import re
                    match = re.search(r"([\d,\.]+)", prix_text)
                    prix = match.group(1).replace(",", ".") if match else ""

                # 🔹 Réduction
                reduction_p = li.select_one("p")
                reduction = reduction_p.get_text(strip=True) if reduction_p else ""

                if modele:
                    products.append({
                        "marque": marque,
                        "modele": modele,
                        "prix": prix,
                        "reduction": reduction,
                    })
            except Exception as e:
                continue  # ignore erreurs isolées

        print(f"✅ {len(products)} produits extraits :")
        for p in products[:5]:
            print(f"  • {p['marque']} — {p['modele']} | {p['prix']} € ({p['reduction']})")

        if products:
            import csv
            with open("produits.csv", "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["marque", "modele", "prix", "reduction"])
                writer.writeheader()
                writer.writerows(products)
            print("\n📄 Exporté dans 'produits.csv'")
        return products

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(scrape_products())