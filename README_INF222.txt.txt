# API Blog Simple - FastAPI

Ce projet est une API Backend pour gérer un blog, réalisée avec **Python** et **FastAPI**.

## Fonctionnalités
- Gestion complète des articles (CRUD).
- Recherche textuelle par titre ou contenu.
- Filtrage par catégorie ou auteur.
- Documentation interactive via Swagger.

## Installation
1. Cloner le dépôt :
   git clone <lien-du-repo>
2. Installer les dépendances :
   pip install fastapi uvicorn pydantic

## Utilisation
Lancer le serveur :
uvicorn main:app --reload

Accéder à la documentation :
- Swagger UI : http://127.0.0.0
- Redoc: http://127.0.0

## Endpoints principaux
- "POST /api/articles" : Créer un article.
- "GET /api/articles": Liste des articles (filtres optionnels `?categorie=X`).
- "GET /api/articles/search?query=texte" : Recherche.
- "PUT /api/articles/{id}" : Mise à jour.
- "DELETE /api/articles/{id}" : Suppression.

Pydantic (BaseModel) : C'est le "cerveau" de la validation. Si tu envoies un titre trop court ou si tu oublies l'auteur, FastAPI renverra automatiquement une erreur 400 Bad Request.
Swagger UI : FastAPI crée automatiquement une interface interactive sur /docs. Tu peux y tester tes POST, GET, etc., sans installer Postman.
Codes HTTP : J'ai inclus les codes standards : 201 pour la création, 404 si l'ID n'existe pas, et 200 par défaut.
nest_asyncio : Obligatoire pour Jupyter car il possède déjà une boucle d'événements interne qui entrerait en conflit avec celle d'Uvicorn.
