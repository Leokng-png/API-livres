from fastapi import FastAPI
from datetime import datetime
import httpx

app = FastAPI()

@app.get("/recherche")
async def recherche(q: str, tri: str = None, ordre: str = "asc"):
    url = "https://openlibrary.org/search.json"
    params = {"q": q}

    async with httpx.AsyncClient() as client:
        reponse = await client.get(url, params=params)
        data = reponse.json()

    docs = data["docs"]
    annee_courante = datetime.now().year

    livres = []
    for livre in docs:
        annee = livre.get("first_publish_year")

        if annee is not None and annee >= 2025 and annee <= annee_courante:
            livres.append({
                "titre": livre.get("title"),
                "auteurs": livre.get("author_name"),
                "annee": annee
            })

    decroissant = (ordre == "desc")

    if tri == "titre":
        livres = sorted(livres, key=lambda livre: livre["titre"] or "", reverse=decroissant)
    elif tri == "annee":
        livres = sorted(livres, key=lambda livre: livre["annee"], reverse=decroissant)
    elif tri == "auteur":
        livres = sorted(livres, key=lambda livre: livre["auteurs"][0] if livre["auteurs"] else "", reverse=decroissant)

    return livres