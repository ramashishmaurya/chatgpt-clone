import os

from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client import models
from llm_factory import get_embeddings as factory_get_embeddings
from llm_factory import get_vector_size

load_dotenv()


_embeddings = None 
_qdrant_client = None


def get_embeddings():
    """Return Embeddings from Factory (Cached)."""

    global _embeddings

    if _embeddings is None:
        _embeddings = factory_get_embeddings()

    return _embeddings

def get_qdrant_client():
    """Return cached Qdrant client."""

    global _qdrant_client

    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )

    return _qdrant_client


def get_or_create_collection(session_id: str):
    """
    Return QdrantVectorStore for a session.

    If collection does not exist, create it.
    """

    client = get_qdrant_client()

    if not client.collection_exists(collection_name=session_id):
        client.create_collection(
            collection_name=session_id,
            vectors_config=models.VectorParams(
                size=get_vector_size(),
                distance=models.Distance.COSINE,
            ),
        )

        print(
            f"Created new Qdrant collection: {session_id}"
        )

    return QdrantVectorStore(
        client=client,
        collection_name=session_id,
        embedding=get_embeddings(),
    )


def add_documents(session_id: str, documents): # expected only the session id and documents 
    """
    Embed documents using Gemini and store them in Qdrant.
    """

    vectorstore = QdrantVectorStore.from_documents(
        documents=documents,
        embedding=get_embeddings(),
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        collection_name=session_id,
    )

    print(
        f"Data successfully stored in Qdrant collection: "
        f"'{session_id}'"
    )

    return vectorstore


