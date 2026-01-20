import streamlit as st
import requests


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def generate_llm_response(query: str, context: str) -> str:
    if "GROQ_API_KEY" not in st.secrets:
        return None

    api_key = st.secrets["GROQ_API_KEY"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a medical assistant.\n"
                    "Answer ONLY using the provided document context.\n"
                    "If the answer is not present, say:\n"
                    "'The information is not available in the uploaded documents.'"
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{query}",
            },
        ],
    }

    try:
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            return None

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception:
        return None
    