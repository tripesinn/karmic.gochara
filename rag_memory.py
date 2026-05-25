import os
from datetime import datetime
import uuid

# Si on est sur Google Cloud Run, le RAG local sur disque éphémère est désactivé
# (Il est destiné à l'utilisation locale / hors-ligne)
IS_CLOUD = bool(os.environ.get("K_SERVICE"))

_collection = None
_initialized = False

def _get_collection():
    global _collection, _initialized
    if _initialized:
        return _collection
        
    _initialized = True
    
    if IS_CLOUD:
        print("[RAG] Désactivé sur Cloud Run (disque éphémère).")
        return None
        
    try:
        import chromadb
        from chromadb.utils import embedding_functions
        
        # Configuration du dossier pour la base vectorielle locale
        VAULT_DIR = os.path.join(os.path.dirname(__file__), "karmic_vault")
        os.makedirs(VAULT_DIR, exist_ok=True)
        DB_DIR = os.path.join(VAULT_DIR, "vector_db")
        os.makedirs(DB_DIR, exist_ok=True)

        # Initialisation du client ChromaDB local persistant
        chroma_client = chromadb.PersistentClient(path=DB_DIR)

        # Initialisation de la fonction d'embedding via SentenceTransformers
        try:
            emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[RAG] Warning: Failed to initialize SentenceTransformer. Fallback. Error: {e}")
            emb_fn = chromadb.utils.embedding_functions.DefaultEmbeddingFunction()

        # Création ou récupération de la collection globale pour tous les utilisateurs
        _collection = chroma_client.get_or_create_collection(
            name="karmic_memory",
            embedding_function=emb_fn,
            metadata={"description": "Persistent memory of Karmic Gochara readings"}
        )
    except Exception as e:
        print(f"[RAG] Erreur critique d'initialisation: {e}")
        _collection = None
        
    return _collection


def save_reading(pseudo: str, content: str, reading_type: str, date_str: str = None):
    """Sauvegarde une lecture ou un échange dans la mémoire vectorielle locale."""
    col = _get_collection()
    if not col or not pseudo or not content:
        return
        
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        
    doc_id = f"{pseudo}_{reading_type}_{uuid.uuid4().hex[:8]}"
    metadata = {
        "pseudo": pseudo,
        "reading_type": reading_type,
        "date": date_str
    }
    
    try:
        col.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"[RAG] Souvenir enregistré pour {pseudo} (Type: {reading_type}, ID: {doc_id})")
    except Exception as e:
        print(f"[RAG] Erreur lors de l'enregistrement pour {pseudo}: {e}")

def retrieve_context(pseudo: str, query: str, limit: int = 3) -> str:
    """Recherche les souvenirs les plus pertinents pour l'utilisateur en fonction de la requête."""
    col = _get_collection()
    if not col or not pseudo or not query:
        return ""
        
    try:
        results = col.query(
            query_texts=[query],
            n_results=limit,
            where={"pseudo": pseudo}
        )
        
        if not results or not results["documents"] or not results["documents"][0]:
            return ""
            
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        
        context_lines = []
        for doc, meta in zip(documents, metadatas):
            date_s = meta.get("date", "Date inconnue")
            r_type = meta.get("reading_type", "Lecture")
            context_lines.append(f"[{date_s} - {r_type}]\n{doc}")
            
        return "\n\n---\n\n".join(context_lines)
    except Exception as e:
        print(f"[RAG] Erreur lors de la récupération de contexte pour {pseudo}: {e}")
        return ""
