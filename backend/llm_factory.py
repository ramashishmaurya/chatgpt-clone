import os
from dotenv import load_dotenv

load_dotenv()

def get_llm(temperature=0.3):
    """
    Returns the appropriate Chat Model based on the .env LLM_PROVIDER setting.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    
    if provider == "groq":
        from langchain_groq import ChatGroq
        print(f"[FACTORY] Using GROQ (Model: qwen/qwen3.8-27b)")
        return ChatGroq(model="qwen/qwen3.8-27b", temperature=temperature)
        
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        print(f"[FACTORY] Using GEMINI (Model: gemini-1.5-flash)")
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=temperature)
        
    else: 
        # Default to offline Ollama
        from langchain_ollama import ChatOllama
        print(f"[FACTORY] Using OLLAMA (Model: llama3)")
        return ChatOllama(model="llama3", temperature=temperature)

def get_embeddings():
    """
    Returns the appropriate Embeddings based on the .env LLM_PROVIDER setting.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    
    if provider == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        print(f"[FACTORY] Using GEMINI Embeddings")
        return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        
    else:
        # Both Groq and Ollama use local Nomic embeddings (Groq doesn't host embeddings)
        from langchain_ollama import OllamaEmbeddings
        print(f"[FACTORY] Using OLLAMA Embeddings (nomic-embed-text)")
        return OllamaEmbeddings(model="nomic-embed-text")

def get_vector_size():
    """Returns vector dimension size for the current embedding model."""
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    if provider == "gemini":
        return 768
    return 768 # Nomic is also 768
