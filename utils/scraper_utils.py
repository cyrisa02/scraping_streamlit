# utils/scraper_utils.py
import json
import os
import asyncio
import re
from typing import List, Set, Tuple, Optional

# --- Modèle fallback ---
try:
    from models.vetement_ski import VetementSki
except ImportError:
    from pydantic import BaseModel

    class VetementSki(BaseModel):
        modele: str
        description: str
        prix: str


# --- Utils fallback ---
def is_complete_vetement(vetement: dict, required_keys: List[str]) -> bool:
    return all(vetement.get(k) and str(vetement[k]).strip() for k in required_keys)


def is_duplicate_vetement(modele: str, modeles_vus: Set[str]) -> bool:
    clean = str(modele).strip().lower()
    return clean in {m.strip().lower() for m in modeles_vus}


# --- CONFIG BROWSER ---
def get_browser_config():
    return {
        "browser_type": "chromium",
        "headless": True,
        "verbose": False,
        "disable_images": True,
        "disable_webrtc": True,
        "block_urls": [
            "*.google-analytics.com",
            "*.googletagmanager.com",
            "*.hotjar.com",
            "*.doubleclick.net",
            "*.facebook.com",
            "*.trbo.com",
            "*/analytics/*",
            "*/tracking/*",
        ],
    }


# --- STRATÉGIE LLM — CORRIGÉE POUR OPENROUTER ---
def get_llm_strategy(required_keys: Optional[List[str]] = None) -> "LLMExtractionStrategy":
    # ✅ Import local pour éviter NameError
    from crawl4ai.extraction_strategy import LLMExtractionStrategy

    # 🔑 Headers requis par OpenRouter (via litellm)
    os.environ.setdefault("OPENROUTER_SITE_URL", "https://skiwebshop.fr")
    os.environ.setdefault("OPENROUTER_APP_NAME", "SkiScraper")

    schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "modele": {"type": "string"},
                        "description": {"type": "string"},
                        "prix": {"type": "string"},
                    },
                    "required": ["modele", "description", "prix"],
                    "additionalProperties": False,
                }
            }
        },
        "required": ["items"],
    }

    instruction = (
        "Tu es un expert HTML. Extrait TOUS les vêtements de la liste.\n"
        "Pour chaque produit :\n"
        "- 'modele' → texte de <h3 class=\"product-name\"> ou <a> contenant le nom\n"
        "- 'description' → texte de <p class=\"product-description\"> ou similaire\n"
        "- 'prix' → contenu de <span class=\"price\"> ou <span class=\"price-value\">, nettoyé (ex: '53.90')\n"
        "Ne jamais inventer. Si manquant, laisser vide.\n"
        "Renvoie UNIQUEMENT un objet JSON avec clé 'items'."
    )

    return LLMExtractionStrategy(
        provider="openai",  # ✅ OBLIGATOIRE
        api_token=os.getenv("OPENROUTER_API_KEY"),
        model="meta-llama/llama-3.2-3b-instruct:free",  # ✅ Stable & free
        api_base="https://openrouter.ai/api/v1",  # ✅ Sans espace !
        schema=schema,
        extraction_type="schema",
        instruction=instruction,
        input_format="html",
        verbose=False,
    )


# --- DÉTECTION FIN ---
async def check_no_results(crawler, url: str, session_id: str) -> bool:
    from crawl4ai import CrawlerRunConfig, CacheMode

    try:
        result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                session_id=session_id,
                css_selector="body",
                wait_for="body",
                page_timeout=20000,
            ),
        )
        if not result.success or not result.cleaned_html:
            return False

        phrases = [
            "Désolés, nous n'avons pas ça sous la main !",
            "Aucun produit ne correspond",
            "0 résultat",
            "Aucun article trouvé",
        ]
        html = result.cleaned_html.lower()
        return any(p.lower() in html for p in phrases)
    except Exception:
        return False


# --- EXTRACTION PAGE — ROBUSTE ---
async def fetch_and_process_page(
    crawler,
    numero_page: int,
    base_url: str,
    css_selector: str,
    llm_strategy,
    session_id: str,
    required_keys: List[str],
    noms_vus: Set[str],
) -> Tuple[List[dict], bool]:
    sep = "&" if "?" in base_url else "?"
    url = f"{base_url}{sep}page={numero_page}"
    print(f"➡️ Page {numero_page}")

    if await check_no_results(crawler, url, session_id):
        return [], True

    from crawl4ai import CrawlerRunConfig, CacheMode

    try:
        result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=llm_strategy,
                css_selector=css_selector,
                session_id=session_id,
                wait_for=f"{css_selector}:first-of-type",  # ✅ Pas networkidle !
                page_timeout=45000,
            ),
        )

        if not result.success:
            print(f"❌ Page {numero_page} échouée.")
            return [], False

        if not result.extracted_content:
            print(f"⚠️ Page {numero_page} : contenu extrait vide.")
            return [], False

        # 🔍 Parsing sécurisé
        raw = result.extracted_content.strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Tentative : extraire bloc JSON dans du texte
            match = re.search(r"\{.*\"items\".*\}", raw, re.DOTALL)
            if not match:
                print(f"⚠️ Page {numero_page} : JSON non trouvé dans : {raw[:200]}...")
                return [], False
            try:
                data = json.loads(match.group())
            except:
                print(f"⚠️ Page {numero_page} : parsing JSON échoué.")
                return [], False

        items = data.get("items", []) if isinstance(data, dict) else data
        if not isinstance(items, list):
            items = []

        valides = []
        for item in items:
            vetement = {
                "modele": str(item.get("modele", "")).strip(),
                "description": str(item.get("description", "")).strip(),
                "prix": str(item.get("prix", "")).strip(),
            }

            # Nettoyage prix : "53,90 €" → "53.90"
            prix = vetement["prix"]
            if prix:
                prix = re.sub(r"[^\d.,]", "", prix)
                prix = prix.replace(",", ".")
                parts = prix.split(".")
                if len(parts) > 2:
                    prix = parts[0] + "." + "".join(parts[1:])
                vetement["prix"] = prix

            if not is_complete_vetement(vetement, required_keys):
                continue
            if is_duplicate_vetement(vetement["modele"], noms_vus):
                continue

            noms_vus.add(vetement["modele"])
            valides.append(vetement)

        print(f"✅ Page {numero_page} : {len(valides)} vêtements")
        return valides, len(valides) == 0 and len(items) > 0

    except Exception as e:
        print(f"💥 Erreur page {numero_page} : {e}")
        return [], False