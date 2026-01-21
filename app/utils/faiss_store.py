import os
import shutil
from pathlib import Path
from langchain_community.vectorstores import FAISS


BASE_FAISS_DIR = Path("/tmp/faiss_indexes")


def get_session_faiss_dir(session_id: str) -> Path:
    """
    Returns the FAISS directory path for a given session.
    """
    session_dir = BASE_FAISS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def save_faiss_index(vector_store: FAISS, session_id: str):
    """
    Save FAISS index to disk for the session.
    """
    session_dir = get_session_faiss_dir(session_id)
    vector_store.save_local(str(session_dir))


def load_faiss_index(session_id: str, embeddings):
    """
    Load FAISS index from disk for the session.
    """
    session_dir = get_session_faiss_dir(session_id)
    if not session_dir.exists():
        return None

    try:
        return FAISS.load_local(
            str(session_dir),
            embeddings,
            allow_dangerous_deserialization=True,
        )
    except Exception:
        return None


def delete_faiss_index(session_id: str):
    """
    Delete FAISS index directory for the session.
    """
    session_dir = BASE_FAISS_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
