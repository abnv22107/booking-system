import streamlit as st
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from utils.faiss_store import (
    save_faiss_index,
    load_faiss_index,
)


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def extract_text_from_pdfs(pdf_files):
    text = ""
    for pdf in pdf_files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def ingest_pdfs(pdf_files):
    """
    Process PDFs once, create FAISS, save to disk.
    """
    text = extract_text_from_pdfs(pdf_files)
    if not text.strip():
        return False

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_text(text)

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )

    from langchain_community.vectorstores import FAISS

    vector_store = FAISS.from_texts(chunks, embeddings)

    save_faiss_index(
        vector_store,
        st.session_state.session_id,
    )

    return True


def rag_query(query: str):
    """
    Load FAISS from disk and perform retrieval.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )

    vector_store = load_faiss_index(
        st.session_state.session_id,
        embeddings,
    )

    if vector_store is None:
        return "No documents uploaded yet. Please upload PDFs first."

    docs = vector_store.similarity_search(query, k=4)

    if not docs:
        return "I could not find relevant information in the uploaded documents."

    context = "\n\n".join(doc.page_content for doc in docs)

    from llm.chatgroq_llm import generate_llm_response

    answer = generate_llm_response(query, context)

    if not answer:
        return "I could not generate an answer at the moment. Please try again."

    return answer
