import asyncio
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
import asyncio
import csv
import os
import sys
from typing import List, Set
from pathlib import Path

from dotenv import load_dotenv

# Charger les variables d'environnement AVANT tout import crawl4ai
load_dotenv()

# === CONFIGURATION ===
try:
    from config import BASE_URL, CSS_SELECTOR, REQUIRED_KEYS
except ImportError:
    print("❌ Fichier config.py manquant.")
    sys.exit(1)

# === UTILITAIRES LOCAUX (fallback si utils/ absent) ===

def save_to_csv(data: List[dict], filename: str):
    """Sauvegarde en CSV avec encodage UTF-8-BOM pour Excel FR"""
    if not data:
        print("⚠️ Aucune donnée à sauvegarder.")
        return
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_KEYS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ {len(data)} éléments sauvegardés dans '{filepath}'.")


def is_complete(item: dict, keys: List[str]) -> bool:
    return all(item.get(k) and str(item[k]).strip() for k in keys)


def is_duplicate(modele: str, seen: Set[str]) -> bool:
    return modele.strip().lower() in {m.lower() for m in seen}


# === IMPORTS PRINCIPAUX ===
try:
    from crawl4ai import AsyncWebCrawler
    from utils.scraper_utils import get_browser_config, get_llm_strategy, fetch_and_process_page
except ImportError as e:
    print(f"❌ Erreur d'import : {e}")
    print("Veuillez vérifier que 'utils/scraper_utils.py' existe.")
    sys.exit(1)


# === FONCTION PRINCIPALE ===
async def crawl_all_vetements():
    print("🚀 Démarrage du scraping des vêtements de ski…")
    print(f"Base URL : {BASE_URL}")
    print(f"Sélecteur CSS : '{CSS_SELECTOR}'")
    print("-" * 50)

    # 🔑 Vérification clé API
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Erreur : OPENROUTER_API_KEY manquante dans .env")
        sys.exit(1)

    # 🔧 Configuration
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy(REQUIRED_KEYS)
    session_id = "ski_crawl_2025"

    all_items: List[dict] = []
    seen_modeles: Set[str] = set()
    page = 1
    max_pages = 50  # Sécurité anti-boucle infinie

    async with AsyncWebCrawler(**browser_config) as crawler:
        while page <= max_pages:
            print(f"\n📄 Traitement de la page {page}…")

            items, should_stop = await fetch_and_process_page(
                crawler=crawler,
                numero_page=page,
                base_url=BASE_URL,
                css_selector=CSS_SELECTOR,
                llm_strategy=llm_strategy,
                session_id=session_id,
                required_keys=REQUIRED_KEYS,
                noms_vus=seen_modeles,
            )

            if items:
                all_items.extend(items)
                print(f"📈 +{len(items)} → total : {len(all_items)}")

            if should_stop:
                print("🛑 Pagination terminée (plus de résultats).")
                break

            if not items and page > 1:
                print("⚠️ Page vide après la 1ère → fin probable.")
                break

            page += 1
            await asyncio.sleep(2.5)  # Respect du serveur

        # Résumé
        print("\n" + "=" * 50)
        print(f"✅ Scraping terminé.")
        print(f"📦 {len(all_items)} vêtements collectés.")
        print(f"🔍 {len(seen_modeles)} modèles uniques.")

        # Sauvegarde
        if all_items:
            filename = "exports/vetements_ski_2025.csv"
            save_to_csv(all_items, filename)

            # Stats simples
            prix_valides = [
                float(v["prix"].replace("€", "").replace(",", ".").strip())
                for v in all_items
                if v["prix"].replace("€", "").replace(",", ".").replace(".", "").isdigit()
            ]
            if prix_valides:
                print(f"💶 Prix moyen : {sum(prix_valides) / len(prix_valides):.2f} €")
                print(f"📉 Min : {min(prix_valides):.2f} € | 📈 Max : {max(prix_valides):.2f} €")

        else:
            print("❌ Aucun vêtement n’a été extrait. Vérifiez :")
            print("   - Le sélecteur CSS (`li.product-item` ?)")
            print("   - L’URL de base (pagination ? `&page=2` ?)")
            print("   - La clé OpenRouter (testez avec `curl` si besoin)")

        # Affiche l'usage LLM (si supporté)
        try:
            if hasattr(llm_strategy, "_llm_client") and hasattr(llm_strategy._llm_client, "show_usage"):
                llm_strategy._llm_client.show_usage()
        except:
            pass


# === POINT D’ENTRÉE ===
async def main():
    try:
        await crawl_all_vetements()
    except KeyboardInterrupt:
        print("\n🛑 Interruption utilisateur. Arrêt gracieux.")
    except Exception as e:
        print(f"\n💥 Erreur critique : {e}")
        import traceback
        traceback.print_exc()




# --- FIN DE main.py ---

if __name__ == "__main__":
    # 🔧 Correction Windows : force une boucle compatible subprocess
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except AttributeError:
            # Si Proactor n'est pas dispo (ex: WSL1), on force Selector
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # 🔁 Exécute dans une boucle propre, sans dépendre de l'IDE
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "event loop is closed" in str(e):
            # Contournement pour certains IDE (ex: Spyder)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(main())
            finally:
                loop.close()
        else:
            raise
   