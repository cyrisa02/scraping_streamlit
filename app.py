# app.py
import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path

# === CONFIGURATION ===
EXPORTS_DIR = Path("exports")

# === STYLE PERSONNALISÉ ===
st.set_page_config(
    page_title="🎿 Catalogue SkiWebShop",
    page_icon="⛷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé : thème montagne
st.markdown("""
<style>
    :root {
        --glacier: #e6f0fa;
        --snow: #ffffff;
        --alpine-blue: #1e56a0;
        --piste-red: #d92b2b;
        --pine-green: #2d5016;
    }
    .stApp {
        background: linear-gradient(135deg, var(--glacier) 0%, #f8fbff 100%);
    }
    .main-header {
        color: var(--alpine-blue);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
    }
    .stat-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--alpine-blue);
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    .highlight {
        background-color: #fff8e6;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 600;
    }
    footer { visibility: hidden; }
    .footer {
        text-align: center;
        padding: 10px;
        color: #777;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# === TITRE ===
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://cdn-icons-png.flaticon.com/512/2536/2536401.png", width=60)
with col_title:
    st.markdown('<h1 class="main-header">Catalogue des sous-pulls de ski 🎿</h1>', unsafe_allow_html=True)

st.caption("Données extraites depuis [skiwebshop.fr](https://www.skiwebshop.fr/femmes/tenues-de-ski/sous-pulls-de-ski) — 332 produits → 137 modèles uniques")

# === CHARGEMENT DES DONNÉES ===
@st.cache_data
def load_data():
    # Cherche le dernier fichier JSON dans exports/
    json_files = list(EXPORTS_DIR.glob("sous_pulls_ski_*.json"))
    if not json_files:
        return None, None
    latest = max(json_files, key=os.path.getmtime)
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Nettoyage
    df["prix_num"] = pd.to_numeric(df["prix"], errors="coerce")
    df["reduction_num"] = df["reduction"].str.replace("%", "").str.replace("−", "-").astype(float, errors="ignore")
    return df, latest.name

df, filename = load_data()

if df is None:
    st.error("❌ Aucun fichier de données trouvé dans `exports/`. Exécutez `scrape_and_export.py` d'abord.")
    st.stop()

# === SIDEBAR ===
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2536/2536401.png", width=40)
st.sidebar.title("🎿 Filtres")

# Recherche libre
search = st.sidebar.text_input("🔍 Recherche (modèle/marque)", placeholder="ex: Fwc'Cruz, O'Neill")

# Filtres
marques = st.sidebar.multiselect(
    "Marque",
    options=sorted(df["marque"].dropna().unique()),
    default=[]
)

# Prix
min_price = float(df["prix_num"].min()) if not df["prix_num"].isna().all() else 0
max_price = float(df["prix_num"].max()) if not df["prix_num"].isna().all() else 100
price_range = st.sidebar.slider(
    "Prix (€)",
    min_value=0.0,
    max_value=200.0,
    value=(0.0, 100.0),
    step=5.0
)

# Réduction
reduc_min = st.sidebar.slider(
    "Réduction ≥",
    -100, 0, -10,
    help="Ex: -30 = réduction d'au moins 30%"
)

# Tri
sort_by = st.sidebar.selectbox(
    "Trier par",
    ["Prix croissant", "Prix décroissant", "Réduction", "Marque", "Modèle"],
    index=0
)

# === FILTRAGE ===
filtered = df.copy()

if search:
    filtered = filtered[
        filtered["modele"].str.contains(search, case=False, na=False) |
        filtered["marque"].str.contains(search, case=False, na=False)
    ]

if marques:
    filtered = filtered[filtered["marque"].isin(marques)]

# Prix
filtered = filtered[
    (filtered["prix_num"] >= price_range[0]) &
    (filtered["prix_num"] <= price_range[1])
]

# Réduction : filtre seulement si reduction_num est numérique
if pd.notna(reduc_min):
    filtered = filtered[
        (pd.notna(filtered["reduction_num"])) &  # ✅ Correction ici
        (filtered["reduction_num"] <= reduc_min)
    ]
else:
    # Si aucun filtre sur réduction, ne rien faire
    pass

# Tri
if sort_by == "Prix croissant":
    filtered = filtered.sort_values("prix_num", ascending=True)
elif sort_by == "Prix décroissant":
    filtered = filtered.sort_values("prix_num", ascending=False)
elif sort_by == "Réduction":
    filtered = filtered.sort_values("reduction_num", ascending=True)
elif sort_by == "Marque":
    filtered = filtered.sort_values("marque")
elif sort_by == "Modèle":
    filtered = filtered.sort_values("modele")


# === STATS ===
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{len(df)}</div>
        <div class="stat-label">Produits bruts</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{len(filtered)}</div>
        <div class="stat-label">Affichés ({len(df)} uniques)</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    prix_moy = filtered["prix_num"].mean()
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{"{:.2f}".format(prix_moy) if not pd.isna(prix_moy) else "—"}</div>
        <div class="stat-label">Prix moyen (€)</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    max_reduc = filtered["reduction_num"].min()
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{"{}%".format(int(max_reduc)) if not pd.isna(max_reduc) else "—"}</div>
        <div class="stat-label">Meilleure réduction</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# === AFFICHAGE TABLEAU ===
st.subheader(f"🛍️ {len(filtered)} sous-pulls sélectionnés")

if len(filtered) == 0:
    st.info("Aucun produit ne correspond aux filtres. Essayez d’élargir les critères.")
else:
    # Formatage du tableau
    display_df = filtered[["marque", "modele", "prix", "reduction"]].copy()
    display_df.columns = ["Marque", "Modèle", "Prix (€)", "Réduction"]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=min(600, 50 + len(filtered) * 35),
        column_config={
            "Prix (€)": st.column_config.NumberColumn(
                "Prix (€)",
                format="%.2f €"
            ),
            "Réduction": st.column_config.TextColumn(
                "Réduction",
                help="Réduction appliquée"
            )
        }
    )

    # Export
    csv = display_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Télécharger (CSV)",
        csv,
        "sous_pulls_ski_filtres.csv",
        "text/csv",
        icon="⬇️"
    )

# === FOOTER ===
st.markdown(f"""
<div class="footer">
    🗂️ Données : <code>{filename}</code> | 
    🕒 Mis à jour le {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
    <br>
    ⛷️ Projet réalisé avec ❤️ pour les passionnés de glisse
</div>
""", unsafe_allow_html=True)