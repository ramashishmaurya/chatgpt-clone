import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from upload_data import load_and_split

def test_upload():
    print("="*50)
    print("🧪 TESTING MULTIMODAL & CONTEXTUAL RAG UPLOAD")
    print("="*50)
    
    # We will create a dummy txt file to test the Contextual Chunking
    dummy_content = b"This is a highly confidential document about Project Alpha. The project started in 2023. It aims to build a time machine."
    filename = "project_alpha.txt"
    
    print(f"File being processed: {filename}")
    print("Pipeline should trigger Contextual Chunking (Metadata Injection)...")
    
    chunks = load_and_split(dummy_content, filename)
    
    print("\n✅ Processing Complete!")
    print(f"Number of chunks created: {len(chunks)}")
    
    if len(chunks) > 0:
        print("\n🔍 Inspecting First Chunk:")
        print("-" * 30)
        print("PAGE CONTENT:")
        print(chunks[0].page_content)
        print("-" * 30)
        print("METADATA:")
        print(chunks[0].metadata)
        print("-" * 30)
        
        if "[DOCUMENT CONTEXT:" in chunks[0].page_content:
            print("✅ SUCCESS: Contextual Chunking summary was successfully prepended to the chunk!")
        else:
            print("❌ FAILURE: Contextual Chunking summary is missing.")
            
    print("\n(Note: To test Multimodal RAG with LLaVA, pass a real PDF with images as file_bytes instead of .txt)")

if __name__ == "__main__":
    test_upload()
