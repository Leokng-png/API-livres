import time
import requests
import json
import os

url = "https://openlibrary.org/search.json"
params = {
    "q": "first_publish_year:[2025 TO *]",
    "limit": 100,
    "page": 1
}

response = requests.get(url, params=params)
data = response.json()
nb_pages_total = data["numFound"] // params["limit"] + 1

dossier_sortie = "livres_json"
os.makedirs(dossier_sortie, exist_ok=True)  # crée le dossier s'il n'existe pas déjà

def nettoyer_livre(doc):
    return {
        "key": doc.get("key"),
        "title": doc.get("title"),
        "author_name": doc.get("author_name", []),
        "first_publish_year": doc.get("first_publish_year"),
        "language": doc.get("language", []),
    }

def sauvegarder_livre_individuel(livre, dossier):
    key = livre.get("key")
    if not key:
        return  # pas de key, on ne peut pas nommer le fichier, on saute ce livre
    id_livre = key.split("/")[-1]
    chemin = os.path.join(dossier, f"{id_livre}.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(livre, f, ensure_ascii=False, indent=2)

page = 1
while True:
    params["page"] = page

    tentatives = 0
    succes = False
    docs = []

    while tentatives < 3 and not succes:
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            docs = data.get("docs", [])
            succes = True
        except requests.exceptions.RequestException as e:
            tentatives += 1
            print(f"Erreur page {page}, tentative {tentatives}/3 : {e}")
            time.sleep(2)

    if not succes:
        print(f"Page {page} abandonnée après 3 tentatives.")
        page += 1
        time.sleep(1)
        continue

    if not docs:
        break

    for doc in docs:
        livre = nettoyer_livre(doc)
        sauvegarder_livre_individuel(livre, dossier_sortie)

    print(f"Page {page}/{nb_pages_total} traitée.")

    if page >= nb_pages_total:
        break

    time.sleep(1)
    page += 1