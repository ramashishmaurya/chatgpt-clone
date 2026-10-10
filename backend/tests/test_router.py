import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_services import route_question

async def test_router():
    print("="*50)
    print("🧪 TESTING ROUTER (AGENTIC RAG LOGIC)")
    print("="*50)
    
    test_questions = [
        "Hi, how are you today?", # Should be CHAT
        "What does my uploaded contract say about termination?", # Should be DOCUMENT
        "Who won the cricket match yesterday?", # Should be WEB
    ]
    
    for q in test_questions:
        print(f"\nUser Question: '{q}'")
        route = await route_question(q)
        print(f"🤖 Agent Decided Route: [{route}]")
        
        if route == "CHAT":
            print("➡️ Action: I will talk normally from memory.")
        elif route == "DOCUMENT":
            print("➡️ Action: I will use the Qdrant DB Tool to search private PDFs.")
        elif route == "WEB":
            print("➡️ Action: I will use the Tavily Search Tool to browse the internet.")
            
    print("\n✅ Router test complete!")

if __name__ == "__main__":
    asyncio.run(test_router())
