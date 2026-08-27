from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient

from dotenv import load_dotenv

load_dotenv()

from vector_store import get_or_create_collection


def get_retriever( session_id: str, k: int = 4,):

    vectorstore = get_or_create_collection(session_id)

    retriever = vectorstore.as_retriever( 
        search_kwargs={
            "k": k
        }
    )

    return retriever




