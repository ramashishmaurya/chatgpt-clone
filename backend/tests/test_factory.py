import sys
import os

# Add parent directory to path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_factory import get_llm, get_embeddings, get_vector_size

def test_factory():
    print("="*50)
    print("🧪 TESTING LLM FACTORY")
    print("="*50)
    
    provider = os.getenv("LLM_PROVIDER", "Not Set (Defaults to Ollama)")
    print(f"Current .env LLM_PROVIDER: {provider}\n")
    
    print("[1] Loading Chat LLM...")
    llm = get_llm(temperature=0.0)
    print(f"✅ Success! Loaded Chat Model: {type(llm).__name__}")
    
    print("\n[2] Loading Embeddings...")
    embeddings = get_embeddings()
    print(f"✅ Success! Loaded Embeddings Model: {type(embeddings).__name__}")
    
    print("\n[3] Checking Vector Size...")
    size = get_vector_size()
    print(f"✅ Success! Expected Qdrant Vector Size: {size}")
    
    print("\n[4] Running a quick LLM test (Ping)...")
    try:
        response = llm.invoke("Reply with exactly one word: 'pong'")
        print(f"🤖 LLM Response: {response.content.strip()}")
        print("✅ Factory is working perfectly!")
    except Exception as e:
        print(f"❌ LLM Test Failed. Is your API key correct or Ollama running? Error: {e}")

if __name__ == "__main__":
    test_factory()
