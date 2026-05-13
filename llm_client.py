import os
from dotenv import load_dotenv
import ollama


load_dotenv()


OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


SYSTEM_PROMPT = (
    "You are a personal finance assistant. "
    "Explain transaction analysis clearly and carefully. "
    "Do not invent numbers. Use only the provided tool results."
)


def call_llm(prompt, model=OLLAMA_MODEL):
    """
    Call a local LLM through Ollama.

    Make sure Ollama is installed and the model has been pulled locally.
    Example:
        ollama pull qwen2.5:3b
    """
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        options={
            "temperature": 0.2
        }
    )

    return response["message"]["content"]


def get_llm_provider_info():
    """
    Return current local LLM backend information for displaying in Streamlit.
    """
    return {
        "provider": "ollama",
        "model": OLLAMA_MODEL
    }