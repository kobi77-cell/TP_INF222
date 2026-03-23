import nest_asyncio
import uvicorn
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 1. Configuration pour environnement asynchrone (Jupyter/Notebook)
nest_asyncio.apply()

# 2. Initialisation de l'application
app = FastAPI(
    title="Blog API - Version SQLite",
    description="Accédez à /docs pour tester l'API",
    version="1.1.0"
)

# 3. Initialisation de la Base de Données SQLite
def init_db():
    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            contenu TEXT NOT NULL,
            auteur TEXT NOT NULL,
            categorie TEXT NOT NULL,
            date TEXT NOT NULL,
            tags TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 4. Modèle de données (Pydantic V2)
class ArticleSchema(BaseModel):
    titre: str = Field(..., min_length=3, json_schema_extra={"example": "Mon premier article"})
    contenu: str = Field(..., min_length=5, json_schema_extra={"example": "Voici le contenu complet..."})
    auteur: str = Field(..., json_schema_extra={"example": "Paul Alin"})
    categorie: str = Field(..., json_schema_extra={"example": "Tech"})
    tags: List[str] = Field(default=["news"], json_schema_extra={"example": ["python", "fastapi"]})

# 5. Endpoints (Routes)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API du Blog. Allez sur /docs pour tester."}

@app.post("/api/articles", status_code=201)
async def create_article(article: ArticleSchema):
    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()
    date_now = datetime.now().strftime("%d/%m/%Y %H:%M")
    tags_str = ",".join(article.tags)

    cursor.execute('''
        INSERT INTO articles (titre, contenu, auteur, categorie, date, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (article.titre, article.contenu, article.auteur, article.categorie, date_now, tags_str))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"message": "Article créé avec succès", "id": new_id}

@app.get("/api/articles")
async def get_articles(categorie: Optional[str] = None):
    conn = sqlite3.connect("blog.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if categorie:
        cursor.execute("SELECT * FROM articles WHERE LOWER(categorie) = LOWER(?)", (categorie,))
    else:
        cursor.execute("SELECT * FROM articles")

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        item["tags"] = item["tags"].split(",") if item["tags"] else []
        result.append(item)
    return result

@app.get("/api/articles/search")
async def search_articles(query: str = Query(..., min_length=1)):
    conn = sqlite3.connect("blog.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    search_val = f"%{query}%"
    cursor.execute("SELECT * FROM articles WHERE titre LIKE ? OR contenu LIKE ?", (search_val, search_val))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/articles/{article_id}")
async def get_one_article(article_id: int):
    conn = sqlite3.connect("blog.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return dict(row)

@app.delete("/api/articles/{article_id}")
async def delete_article(article_id: int):
    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Impossible de supprimer : ID inexistant")
    return {"message": f"Article {article_id} supprimé définitivement"}

# 6. Lancement du serveur
if __name__ == "__main__":
    print("\n--- SERVEUR ACTIF ---")
    print("1. Testez la racine : http://127.0.0.1:8000")
    print("2. Testez le Swagger : http://127.0.0.1:8000/docs")
    config = uvicorn.Config(app, host="127.0.0.1", port=8000)
    server = uvicorn.Server(config)
    server.run()
