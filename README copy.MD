# Crawler Deep Seek pour Salles de Sport

Ce projet est un crawler web construit avec Python qui extrait des données de vêtements de sport d'un site web en utilisant la programmation asynchrone avec Crawl4AI. Il utilise une stratégie d'extraction basée sur un modèle de langage et sauvegarde les données collectées dans un fichier CSV.

## Fonctionnalités

- Crawling web asynchrone utilisant Crawl4AI  
- Extraction de données alimentée par un modèle de langage (LLM)  
- Export CSV des informations des salles de sport  
- Structure de code modulaire et facile à suivre, idéale pour les débutants  

## Structure du Projet

```
.
├── main.py               # Point d'entrée principal du crawler
├── config.py             # Contient les constantes de configuration (URL de base, sélecteurs CSS, etc.)
├── models
│   └── gym.py            # Définit le modèle de données Salle de Sport avec Pydantic
├── utils
│   ├── __init__.py       # Marqueur de package (vide) pour utils
│   ├── data_utils.py     # Fonctions utilitaires pour le traitement et la sauvegarde des données
│   └── scraper_utils.py  # Fonctions utilitaires pour configurer et exécuter le crawler
├── requirements.txt      # Dépendances des packages Python
├── .gitignore            # Fichier Git ignore (ex: exclut .env et fichiers CSV)
└── README.md             # Ce fichier
```

## Installation

### 1. Créer et Activer un Environnement Conda

```bash
conda create -n deep-seek-crawler python=3.12 -y
conda activate deep-seek-crawler
```

### 2. Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer vos Variables d'Environnement  

Créez un fichier `.env` dans le répertoire racine avec un contenu similaire à:

```env
GROQ_API_KEY=votre_clé_api_groq_ici
```

*(Note: Le fichier `.env` est dans votre .gitignore, il ne sera donc pas poussé vers le contrôle de version.)*

## Utilisation

Pour démarrer le crawler, exécutez:

```bash
python main.py
```

Le script va crawler le site web spécifié, extraire les données page par page, et sauvegarder les salles de sport complètes dans un fichier `salles_sport_completes.csv` dans le répertoire du projet. De plus, les statistiques d'utilisation de la stratégie LLM seront affichées après le crawling.

## Configuration

Le fichier `config.py` contient les constantes clés utilisées dans le projet:

- **BASE_URL**: L'URL du site web à partir duquel extraire les données des salles.  
- **CSS_SELECTOR**: Chaîne de sélecteur CSS utilisée pour cibler le contenu des salles.  
- **REQUIRED_KEYS**: Liste des champs requis pour considérer une salle comme complète.  

Vous pouvez modifier ces valeurs selon vos besoins.

## Notes Supplémentaires

- **Journalisation:** Le projet utilise actuellement des instructions `print` pour les messages d'état. Pour la production ou le développement ultérieur, envisagez d'intégrer le module `logging` de Python.  
- **Améliorations:** Le code est structuré en plusieurs modules pour maintenir la séparation des préoccupations, facilitant la compréhension et l'extension des fonctionnalités pour les débutants.  
- **Dépendances:** Assurez-vous que les versions des packages spécifiées dans `requirements.txt` sont installées pour éviter les problèmes de compatibilité.  
