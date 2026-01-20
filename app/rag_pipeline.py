import streamlit as st
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def extract_text_from_pdfs(pdf_files):
    text = ""
    for pdf in pdf_files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def create_vector_store(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_text(text)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store


def ingest_pdfs(pdf_files):
    text = extract_text_from_pdfs(pdf_files)
    if not text.strip():
        return None
    return create_vector_store(text)


def rag_query(query: str):
    if "vector_store" not in st.session_state:
        return "No documents uploaded yet. Please upload PDFs first."

    docs = st.session_state.vector_store.similarity_search(query, k=3)

    if not docs:
        return "I could not find relevant information in the uploaded documents."

    context = "\n\n".join([doc.page_content for doc in docs])

    # Simple RAG response (LLM will be added later)
    return f"📄 **Based on the uploaded documents:**\n\n{context}"
