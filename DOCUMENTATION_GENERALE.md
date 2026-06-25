# Documentation générale (Ce fichier)

Objectif : fournir une documentation technique en français décrivant le projet, son architecture, son déploiement, et des exemples d'intégration backend / persistance.

## Résumé
pdf_searchIA_v0.1 est un prototype de moteur de recherche sémantique pour PDF : frontend minimal (HTML/JS) -> backend FastAPI -> indexation via LangChain -> vectorstore (FAISS) -> LLM pour la génération de réponse.

## Arborescence importante
Racine du dépôt (extrait) :
- api/
  - main.py              # serveur FastAPI et logique d'indexation
  - pdf/                 # emplacement attendu des PDF (ex: Réseaux.pdf)
- index.html             # frontend minimal
- script.js              # intégration frontend -> backend
- ARCHITECTURE.md        # résumé architecture (fichier ajouté)

## Composants et responsabilités
- Frontend : saisie question, envoi POST /ask, affichage réponse.
- Backend (api/main.py) :
  - Chargement et parsing du PDF (PyPDFLoader)
  - Création d'embeddings (OpenAIEmbeddings)
  - Indexation dans FAISS via LangChain
  - Construction d'une "QA chain" (retriever → prompt → ChatOpenAI)
  - Endpoint /ask pour interroger la chaîne.
- Persistance : prototype utilise FAISS en mémoire ; options de production listées ci‑dessous.

## Diagramme de composants (logique)
1. PDF -> PyPDFLoader -> documents (pages)
2. Embeddings(OpenAI) pour chaque document
3. VectorStore (FAISS) : indexation et recherche par similarité
4. Retriever récupère top-k documents
5. Prompt + LLM (ChatOpenAI) → réponse finale

## Guides rapides (voir README.md pour installation détaillée)
- Pour lancer localement : fournir clé OpenAI dans .env, installer dépendances, lancer uvicorn api.main:app.
- Frontend : ouvrir index.html et poser une question (ou héberger via un petit serveur static).
- Pour persistance : exemple FAISS.save_local / load_local (cf. section Exemples).

## Exemples d'intégration backend / persistance

1) FAISS (persistant sur disque) — pattern LangChain (exemple)
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Charger docs
loader = PyPDFLoader("api/pdf/Réseaux.pdf")
docs = loader.load()

#Créer index et sauvegarder localement
emb = OpenAIEmbeddings()
db = FAISS.from_documents(docs, emb)
db.save_local("faiss_index")  # répertoire créé contenant les fichiers d'index

#Recharger plus tard
db2 = FAISS.load_local("faiss_index", emb)
retriever = db2.as_retriever()
```

2) Postgres + pgvector (concept)
- Installer Postgres + extension pgvector.
- Stocker embeddings (float[]) et champs texte, effectuer recherche par <-> (distance cos/sqeuclid) :
```python
# Exemple minimal (conceptuel)
from langchain_openai import OpenAIEmbeddings
import psycopg2
import numpy as np

emb = OpenAIEmbeddings()
vec = emb.embed_query("Texte à indexer")  # pseudo-fonction selon implémentation
# INSERT INTO documents(id, content, embedding) VALUES(..., %s, %s)
# SELECT id, content, embedding <-> %s AS dist FROM documents ORDER BY dist LIMIT 5;
```
- Avantage : persistance relationnelle, sauvegardes, multi‑tenant, facile à scaler avec Postgres géré.

## Bonnes pratiques
- Ne jamais committer les clés (OpenAI API key) dans le dépôt.
- Versionner le format d'index (si vous sauvegardez FAISS).
- Mettre en place des tests unitaires et d'intégration pour la chaîne RA (retrieval + answer).
- Mettre en place de la surveillance (logs, métriques latence/erreurs) et backups d'index.

## Checklist rapide (déploiement / production)
- [ ] .env.example avec variables nécessaires (OPENAI_API_KEY, PORT, etc.)
- [ ] Validation & sanitation des entrées utilisateurs
- [ ] Authentification (API keys, JWT)
- [ ] TLS/HTTPS, CORS restreint
- [ ] Logging structuré et monitoring
- [ ] Sauvegarde / persistance des index
- [ ] Stratégie de rebuild d'index
- [ ] Tests automatisés & CI
