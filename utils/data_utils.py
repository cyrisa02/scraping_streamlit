import csv
import json
from typing import List, Dict, Set


def save_vetements_ski_to_csv(vetements: List[Dict], filename: str):
    """
    Sauvegarde la liste des vêtements de ski dans un fichier CSV.
    
    Args:
        vetements: Liste de dictionnaires contenant les données des vêtements
        filename: Nom du fichier CSV de sortie
    """
    if not vetements:
        print("Aucune donnée à sauvegarder.")
        return

    # Définit les en-têtes du CSV basés sur les clés du premier vêtement
    fieldnames = list(vetements[0].keys())
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(vetements)


def is_complete_vetement(vetement: Dict, required_keys: List[str]) -> bool:
    """
    Vérifie si un vêtement contient toutes les clés requises avec des valeurs non vides.
    
    Args:
        vetement: Dictionnaire représentant un vêtement
        required_keys: Liste des clés obligatoires
        
    Returns:
        bool: True si le vêtement est complet, False sinon
    """
    for key in required_keys:
        if key not in vetement or not vetement[key]:
            print(f"Vêtement incomplet: clé '{key}' manquante ou vide")
            return False
    return True


def is_duplicate_vetement(modele: str, modeles_vus: Set[str]) -> bool:
    """
    Vérifie si un modèle de vêtement a déjà été traité.
    
    Args:
        modele: Nom du modèle à vérifier
        modeles_vus: Ensemble des modèles déjà traités
        
    Returns:
        bool: True si le modèle est un doublon, False sinon
    """
    return modele in modeles_vus


def clean_prix(prix_str: str) -> str:
    """
    Nettoie et standardise le format des prix.
    
    Args:
        prix_str: Chaîne de caractères représentant le prix
        
    Returns:
        str: Prix nettoyé (ex: "239.90")
    """
    if not prix_str:
        return ""
    
    # Supprime les symboles monétaires et espaces
    cleaned = prix_str.replace('€', '').replace('$', '').replace(' ', '').strip()
    
    # Remplace la virgule par un point pour les décimales
    cleaned = cleaned.replace(',', '.')
    
    # Garde seulement les chiffres, points et éventuellement le signe moins
    cleaned = ''.join(char for char in cleaned if char.isdigit() or char in '.-')
    
    return cleaned


def validate_vetement_data(vetement: Dict) -> Dict:
    """
    Valide et nettoie les données d'un vêtement.
    
    Args:
        vetement: Dictionnaire contenant les données du vêtement
        
    Returns:
        Dict: Vêtement avec données validées et nettoyées
    """
    # Nettoie le prix
    if 'prix' in vetement:
        vetement['prix'] = clean_prix(vetement['prix'])
    
    # Nettoie la description (supprime les espaces superflus)
    if 'description' in vetement:
        vetement['description'] = vetement['description'].strip()
    
    # Nettoie le modèle (supprime les espaces superflus)
    if 'modele' in vetement:
        vetement['modele'] = vetement['modele'].strip()
    
    return vetement


def print_vetements_stats(vetements: List[Dict]):
    """
    Affiche des statistiques sur les vêtements extraits.
    
    Args:
        vetements: Liste des vêtements extraits
    """
    if not vetements:
        print("Aucun vêtement à analyser.")
        return
    
    print(f"\n=== STATISTIQUES DES VÊTEMENTS ===")
    print(f"Nombre total de vêtements: {len(vetements)}")
    
    # Compte par modèle
    modeles_count = {}
    for vetement in vetements:
        modele = vetement.get('modele', 'Inconnu')
        modeles_count[modele] = modeles_count.get(modele, 0) + 1
    
    print(f"Nombre de modèles uniques: {len(modeles_count)}")
    print("\nRépartition par modèle:")
    for modele, count in modeles_count.items():
        print(f"  - {modele}: {count} vêtement(s)")
    
    # Plage de prix
    prix_list = []
    for vetement in vetements:
        prix = vetement.get('prix', '')
        try:
            prix_float = float(prix) if prix else 0
            prix_list.append(prix_float)
        except ValueError:
            continue
    
    if prix_list:
        print(f"\nPlage de prix:")
        print(f"  - Prix minimum: {min(prix_list):.2f}€")
        print(f"  - Prix maximum: {max(prix_list):.2f}€")
        print(f"  - Prix moyen: {sum(prix_list)/len(prix_list):.2f}€")