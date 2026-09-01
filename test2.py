from backend.rag_services import ask_question
import asyncio
import sys
sys.path.append('backend')
from vector_store import get_or_create_collection
async def main():
    vectorstore = get_or_create_collection('00e62214-c630-4b11-9437-98cb2c1a8c56')
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    docs = await retriever.ainvoke("test")
    print(docs)
asyncio.run(main())
