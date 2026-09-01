import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

async def test_stream():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    print("Without streaming=True:")
    chunks = []
    async for chunk in llm.astream([HumanMessage(content="Count from 1 to 5 slowly")]):
        chunks.append(chunk.content)
        print("CHUNK:", chunk.content)
    print("Total chunks:", len(chunks))

    llm_stream = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        streaming=True,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    print("\nWith streaming=True:")
    chunks = []
    async for chunk in llm_stream.astream([HumanMessage(content="Count from 1 to 5 slowly")]):
        chunks.append(chunk.content)
        print("CHUNK:", chunk.content)
    print("Total chunks:", len(chunks))

asyncio.run(test_stream())
