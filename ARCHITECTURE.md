# Architecture du projet pdf_searchIA_v0.1

Ce document résume l'architecture de l'application, le flux des données et les composants principaux.

## Vue d'ensemble

pdf_searchIA_v0.1 est une petite application de recherche sémantique sur des documents PDF. Elle expose une API REST (FastAPI) qui :
- charge un PDF,
- segmente et vectorise les pages avec des embeddings OpenAI (via LangChain),
- indexe les vecteurs dans une vectorstore (FAISS dans la version actuelle),
- fournit un endpoint /ask pour interroger le contenu via un LLM (ChatOpenAI).

Un frontend très simple (index.html + script.js) envoie des requêtes POST vers l'API.

## Stack
- Langage principal : Python (FastAPI)
- Frontend : HTML + JavaScript
- Vector store initial : FAISS (local, en mémoire / persistant sur disque selon l'usage)
- Embeddings / LLM : OpenAI (via langchain_openai)
- Chargement de PDF : langchain_community.document_loaders.PyPDFLoader

## Composants principaux
- api/main.py : serveur FastAPI, charge un PDF au démarrage, construit la chaîne QA (retriever -> prompt -> LLM) et expose /ask.
- index.html, script.js : petite interface cliente qui envoie la question à http://localhost:8000/ask.
- api/pdf/ : emplacement attendu des PDF (le code référence api/pdf/Réseaux.pdf).

## Diagramme de flux
Voici un diagramme de flux décrivant le cheminement d'une requête utilisateur :

```mermaid
flowchart LR
  A[Utilisateur - Frontend] -->|POST /ask| B[FastAPI: /ask]
  B --> C{QA initialisée?}
  C -- non --> D[Chargement du PDF (PyPDFLoader)]
  D --> E[Documents découpés]
  E --> F[Embeddings (OpenAIEmbeddings)]
  F --> G[VectorStore (FAISS)]
  G --> H[Retrieval (Retriever)]
  H --> I[Prompt template (ChatPromptTemplate)]
  I --> J[LLM (ChatOpenAI)]
  J --> B
  B -->|Réponse JSON| A

  C -- oui --> H
```

## Comments & recommandations
- Le prototype actuel utilise FAISS en mémoire via FAISS.from_documents(...). Pour la production, il est recommandé d'utiliser une vectorstore persistante (ex: Chroma, Milvus, Weaviate, ou FAISS sur disque) ou une base de données vectorielle partagée (Postgres + pgvector, Milvus).
- Externaliser les clés d'API OpenAI et paramètres dans un fichier .env ou via secrets manager.
- Préparer des étapes d'initialisation permettant de recharger l'index ou de le reconstruire en batch (script de pré-processing) plutôt que de charger le PDF à chaud au startup uniquement.

## Fichiers cités
- api/main.py
- index.html
- script.js

---

Fichier généré automatiquement à partir de l'inspection du dépôt.