from retriever import get_or_create_collection
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

def test_search():
    # Provide a session ID that exists in your Qdrant database (look at your chats)
    session_id = input("Enter a Chat Session ID that has an uploaded document: ")
    query = input("Enter a search query: ")

    vectorstore = get_or_create_collection(session_id)
    
    print("\n--- 1. Dense Retriever Results (Semantic Meaning) ---")
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    dense_docs = dense_retriever.invoke(query)
    for i, doc in enumerate(dense_docs):
        print(f"Result {i+1}: {doc.page_content[:100]}...")

    print("\n--- 2. BM25 Retriever Results (Exact Keyword Match) ---")
    client = vectorstore.client
    records, _ = client.scroll(collection_name=session_id, limit=1000, with_payload=True)
    if records:
        docs = [Document(page_content=r.payload.get("page_content", "")) for r in records]
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = 2
        bm25_docs = bm25_retriever.invoke(query)
        for i, doc in enumerate(bm25_docs):
            print(f"Result {i+1}: {doc.page_content[:100]}...")
            
        print("\n--- 3. Metadata-Filtered RAG Results (Only 'confidential' PDF files) ---")
        # We use Qdrant's native filters to only search inside documents that have file_type='pdf'
        from qdrant_client.http import models
        
        # FIX: Qdrant requires an 'index' to be created on a metadata field before you can filter by it!
        try:
            client.create_payload_index(
                collection_name=session_id,
                field_name="metadata.category",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
        except Exception as e:
            pass # Index might already exist
            
        filtered_retriever = vectorstore.as_retriever(
            search_kwargs={
                "k": 2,
                "filter": models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.category",
                            match=models.MatchValue(value="confidential")
                        )
                    ]
                )
            }
        )
        filtered_docs = filtered_retriever.invoke(query)
        for i, doc in enumerate(filtered_docs):
            # Print the text AND the metadata tags to prove it worked!
            print(f"Result {i+1} (Tags: {doc.metadata}): {doc.page_content[:80]}...")
            
    else:
        print("No documents found in this session.")

if __name__ == "__main__":
    test_search()
