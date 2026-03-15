from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Charger les variables d'environnement depuis .env
load_dotenv()

app = FastAPI()

# Activer CORS pour les appels du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser la QA chain
qa = None

def load_pdf():
    global qa
    pdf_path = "api/pdf/Réseaux.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"⚠️  PDF non trouvé: {pdf_path}")
        return False
    
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        db = FAISS.from_documents(documents, OpenAIEmbeddings())
        retriever = db.as_retriever()
        
        llm = ChatOpenAI()
        
        template = """Basé sur le contexte fourni, répondez à la question.

Contexte: {context}

Question: {question}

Réponse:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        qa = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
        )
        
        print(f"✓ PDF chargé avec succès: {len(documents)} documents")
        return True
    except Exception as e:
        print(f"✗ Erreur lors du chargement du PDF: {e}")
        return False

@app.on_event("startup")
async def startup():
    load_pdf()

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_pdf(q: Question):
    if qa is None:
        return {"answer": "Erreur: le PDF n'est pas chargé"}
    
    try:
        result = qa.invoke(q.question)
        answer = result.content if hasattr(result, 'content') else str(result)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"Erreur: {str(e)}"}