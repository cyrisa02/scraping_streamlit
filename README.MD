🎿 SkiWebShop Scraper — Extraction de sous-pulls de ski
Script Python automatisé pour extraire tous les sous-pulls de ski femmes depuis skiwebshop.fr , avec export en JSON, CSV et Excel. 

✅ 332 produits bruts → 137 modèles uniques (dé-duplication par marque + modèle)
✅ Sans LLM ni API tierce → 100 % fiable, rapide, et reproductible
✅ Pagination automatique, extraction robuste (prix, réduction, marque, modèle)

📦 Fonctionnalités
🔍 Scraping multi-pages (jusqu’à la fin des résultats)
🧹 Nettoyage et dé-duplication intelligente
💰 Extraction de :
Marque (ex: O'Neill, Regatta)
Modèle (ex: Fwc'Cruz pull de ski femmes)
Prix (ex: 46.90)
Réduction (ex: -6%)
📤 Export dans 3 formats :
JSON (structuré, pour API/CRM)
CSV (UTF-8-BOM, compatible Excel FR)
Excel (.xlsx, avec mise en forme via pandas)
📊 Statistiques : prix moyen, min, max
🚀 Démarrage rapide
1. Prérequis
Python ≥ 3.9
Environnement virtuel (recommandé)
2. Installation
bash


# Cloner ou copier le projet
git clone https://github.com/votre-nom/ski-scraper.git
cd ski-scraper

# Créer et activer un environnement (optionnel mais conseillé)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS

# Installer les dépendances
pip install -r requirements.txt

# Installer Chromium (obligatoire pour Playwright)
playwright install chromium
# Cloner ou copier le projet
git clone https://github.com/votre-nom/ski-scraper.git
cd ski-scraper

# Créer et activer un environnement (optionnel mais conseillé)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS

# Installer les dépendances
pip install -r requirements.txt

# Installer Chromium (obligatoire pour Playwright)
playwright install chromium
3. Exécution
bash

python scrape_and_export.py
➡️ Les fichiers sont sauvegardés dans ./exports/ :


exports/
├── sous_pulls_ski_137_20251111_184523.json
├── sous_pulls_ski_137_20251111_184523.csv
└── sous_pulls_ski_137_20251111_184523.xlsx  (si pandas installé)

📁 Structure du projet

ski-scraper/
├── scrape_and_export.py     # ✅ Script principal
├── requirements.txt         # Dépendances
├── .env                     # Variables d'environnement (optionnel)
├── utils/                   # Helpers (ex: scraper_utils.py)
└── exports/                 # 📁 Généré automatiquement
🛠️ Personnalisation
URL cible
scrape_and_export.py
BASE_URL = "..."
Sélecteur CSS
scrape_and_export.py
CSS_SELECTOR = "li.product-item"
Format date export
scrape_and_export.py
time.strftime("%Y%m%d_%H%M%S")

⚠️ Limites & Bonnes pratiques
Le site utilise du JavaScript → le script attend 2s après chargement (ajustable via js_code).
Respectez robots.txt et la fréquence de requêtes (await asyncio.sleep(1) entre pages).
En cas de blocage (CAPTCHA), passez à l’API backend ou utilisez un proxy rotatif.
📄 Exemple de sortie (extrait)
json



[
  {
    "marque": "O'Neill",
    "modele": "Fwc'Cruz pull de ski femmes",
    "prix": "46.90",
    "reduction": "-6%"
  },
  {
    "marque": "Regatta",
    "modele": "Yonder II pull de ski femmes",
    "prix": "34.90",
    "reduction": "-30%"
  }
]
