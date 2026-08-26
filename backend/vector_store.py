import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client import models

load_dotenv()


_embeddings = None
_qdrant_client = None


def get_embeddings():
    """Return Gemini Embeddings (Cached)."""

    global _embeddings

    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )

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
                size=3072,
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


def add_documents(session_id: str, documents):
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

