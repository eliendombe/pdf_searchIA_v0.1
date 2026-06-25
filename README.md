# pdf_searchIA_v0.1

Prototype de moteur de recherche sémantique pour documents PDF. Ce dépôt contient un backend FastAPI qui charge un PDF, indexe ses pages en vecteurs via LangChain + OpenAI, stocke les embeddings dans une vectorstore (prototype : FAISS) et expose un endpoint /ask pour interroger le contenu via un LLM. Un frontend minimal (index.html + script.js) permet d'envoyer des questions.

Ce README explique comment lancer le projet localement et en production avec Docker + Postgres + pgvector (option recommandée pour persistance).

---

## Choix retenu : Postgres + pgvector (docker-compose)
Pour la persistance et la production basique, ce guide crée une base Postgres avec l'extension pgvector (via l'image `ankane/pgvector:postgres15`). Les embeddings peuvent être stockés dans Postgres pour persistance, sauvegarde et scalabilité.

## Contenu ajouté
- README.md (ce fichier)
- requirements.txt
- .env.example
- Dockerfile
- docker-compose.yml (Postgres + app)
- docker/postgres/initdb/000_create_extension.sql (initialisation pgvector)

---

## Développement local (sans Docker)
Prérequis : Python 3.10+, clé OpenAI

1. Cloner le dépôt
```bash
git clone https://github.com/eliendombe/pdf_searchIA_v0.1.git
cd pdf_searchIA_v0.1
```

2. Créer et activer un environnement virtuel
```bash
python -m venv .venv
source .venv/bin/activate    # Linux / macOS
.venv\\Scripts\\Activate.ps1  # Windows PowerShell
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Copier `.env.example` en `.env` et remplir la variable OPENAI_API_KEY
```
cp .env.example .env
# Éditez .env et ajoutez votre clé OPENAI_API_KEY
```

5. Placer votre PDF dans `api/pdf/` ou modifier la variable `PDF_PATH` dans `.env`.

6. Lancer le serveur
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port ${PORT:-8000}
```

7. Ouvrir `index.html` dans le navigateur et poser une question.

---

## Lancer avec Docker (Postgres + pgvector)
Prérequis : Docker, docker-compose, variable d'environnement OPENAI_API_KEY définie localement

1. Copier `.env.example` en `.env` et renseigner la clé OPENAI_API_KEY
```bash
cp .env.example .env
# Éditez .env
```

2. Démarrer les services
```bash
docker compose up --build
```

Le service `db` expose Postgres (non exposé par défaut sur l'hôte dans cette configuration). L'app sera accessible sur http://localhost:8000.

3. Vérifier l'indexation
Au premier démarrage, modifiez `api/main.py` pour persister les embeddings dans Postgres si vous implémentez la logique (exemples dans DOCUMENTATION_GENERALE.md). Le conteneur Postgres crée l'extension `vector` au premier démarrage grâce au script d'initialisation.

---

## Variables d'environnement importantes (voir .env.example)
- OPENAI_API_KEY : clé API OpenAI
- DATABASE_URL : URL de connexion Postgres (ex: postgresql://pguser:pgpassword@db:5432/pdfsearch)
- PORT : port pour l'app (défaut 8000)
- PDF_PATH : chemin relatif vers le PDF à indexer (ex: api/pdf/Réseaux.pdf)

---

## Suggestions d'amélioration
- Implémenter endpoints d'administration pour : rebuild index, sauvegarder/charger index, status de l'index.
- Remplacer FAISS in-memory par stockage dans Postgres (pgvector) ou Chroma/Weaviate pour montée en charge.
- Ajouter tests unitaires et d'intégration.
- Mettre en place authentification, monitoring et gestion des quotas API OpenAI.

---

## Licence
Ajoutez une licence si nécessaire.
