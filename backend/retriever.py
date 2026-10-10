from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient

from dotenv import load_dotenv

load_dotenv()

from vector_store import get_or_create_collection

from langchain_community.retrievers import BM25Retriever

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
from typing import List

try:
    from flashrank import Ranker, RerankRequest
    # Initialize the cross-encoder model globally (it will download a tiny ~30MB model on first run)
    rerank_model = Ranker(cache_dir=".")
except ImportError:
    rerank_model = None
    print("WARNING: flashrank not installed. Reranking will be disabled.")

class CustomRerankerRetriever(BaseRetriever):
    """
    RERANKING RAG: Takes a base retriever (which fetches many documents),
    and uses a Cross-Encoder to deeply score and return the best Top N.
    """
    base_retriever: BaseRetriever = Field(...)
    top_n: int = Field(default=4)
    
    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        # 1. Fetch many candidates (e.g., 20) from the base retriever (Hybrid)
        candidates = self.base_retriever.invoke(query)
        if not candidates or rerank_model is None:
            return candidates[:self.top_n]
            
        # 2. Format for Flashrank Cross-Encoder
        passages = [
            {"id": i, "text": doc.page_content, "meta": doc.metadata}
            for i, doc in enumerate(candidates)
        ]
        
        # 3. Rerank them based on deep attention between Query and Text
        rerank_request = RerankRequest(query=query, passages=passages)
        results = rerank_model.rerank(rerank_request)
        
        # 4. Return strictly Top N best documents
        final_docs = []
        for res in results[:self.top_n]:
            final_docs.append(Document(page_content=res["text"], metadata=res.get("meta", {})))
            
        return final_docs

class CustomHybridRetriever(BaseRetriever):
    dense_retriever: BaseRetriever = Field(...)
    bm25_retriever: BaseRetriever = Field(...)
    
    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        dense_docs = self.dense_retriever.invoke(query)
        bm25_docs = self.bm25_retriever.invoke(query)
        
        doc_scores = {}
        for rank, doc in enumerate(dense_docs):
            doc_scores[doc.page_content] = doc_scores.get(doc.page_content, 0) + 1 / (60 + rank)
            
        for rank, doc in enumerate(bm25_docs):
            doc_scores[doc.page_content] = doc_scores.get(doc.page_content, 0) + 1 / (60 + rank)
            
        sorted_docs = sorted(doc_scores.keys(), key=lambda k: doc_scores[k], reverse=True)
        # Fetch TOP 20 candidates here so the Reranker has a big pool to choose from!
        return [Document(page_content=content) for content in sorted_docs[:20]]

from llm_factory import get_llm
from langchain_core.language_models.chat_models import BaseChatModel

class CustomMultiQueryRetriever(BaseRetriever):
    """
    AGENTIC RAG: Uses LLM to break down the user's question into 3 sub-queries,
    fetches documents for all of them, and combines the results.
    """
    base_retriever: BaseRetriever = Field(...)
    llm: BaseChatModel = Field(...)
    
    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        # 1. Ask LLM to generate 3 variations/sub-questions
        prompt = f"You are an AI assistant. Break down the following user question into 3 different search queries that can help find the answer in a database (to solve multi-hop reasoning). Output only the 3 queries, one per line. Question: {query}"
        try:
            response = self.llm.invoke(prompt).content
            queries = [q.strip("- 1234567890.") for q in response.split("\n") if q.strip()]
            queries = queries[:3] # Ensure max 3 queries
        except Exception as e:
            print("Failed to generate multi-queries:", e)
            queries = []
            
        if query not in queries:
            queries.append(query) # Always include the original query!
            
        print(f"\n[Agentic RAG] Generated Queries: {queries}\n")
            
        # 2. Fetch documents for ALL queries using the base retriever
        all_docs = []
        seen_content = set()
        
        for q in queries:
            docs = self.base_retriever.invoke(q)
            for doc in docs:
                if doc.page_content not in seen_content:
                    all_docs.append(doc)
                    seen_content.add(doc.page_content)
                    
        return all_docs

class CorrectiveRetriever(BaseRetriever):
    """
    CORRECTIVE RAG (CRAG): Evaluates retrieved documents. If they are weak/irrelevant,
    it falls back to a Web Search (Tavily) to find the correct answer!
    """
    base_retriever: BaseRetriever = Field(...)
    llm: BaseChatModel = Field(...)
    
    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        # 1. Fetch documents from the entire pipeline
        docs = self.base_retriever.invoke(query)
        
        if not docs:
            print("\n[CRAG] No documents found! Falling back to Web Search...")
            return self._web_search(query)
            
        # 2. Evaluate relevance using LLM (The "Teacher")
        combined_text = "\n".join([d.page_content for d in docs[:2]]) # Check top 2 docs
        prompt = f"You are a strict grader. Determine if the following documents contain information relevant to answering the question. Output exactly one word: 'yes' or 'no'.\nQuestion: {query}\nDocuments:\n{combined_text}"
        
        try:
            grade = self.llm.invoke(prompt).content.strip().lower()
            print(f"\n[CRAG Evaluator] Grade: {grade.upper()}")
            
            if "yes" in grade:
                return docs # Good retrieval, proceed normally!
            else:
                print("[CRAG Evaluator] Retrieval is weak or irrelevant. Falling back to Web Search...")
                return self._web_search(query)
                
        except Exception as e:
            print("[CRAG] Evaluation failed, continuing with retrieved docs:", e)
            return docs
            
    def _web_search(self, query: str) -> List[Document]:
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            tavily = TavilySearchResults(max_results=3)
            results = tavily.invoke({"query": query})
            
            web_docs = []
            for res in results:
                web_docs.append(Document(
                    page_content=res.get("content", ""), 
                    metadata={"source": res.get("url", "web"), "category": "web_search"}
                ))
            print("[CRAG] Web Search successful!")
            return web_docs
        except Exception as e:
            print(f"[CRAG] Web Search failed (Check API keys): {e}")
            # Instead of hallucinating, return a safe fallback document
            return [Document(page_content="Sorry, I do not have this information in my documents and web search is disabled.", metadata={"source": "system"})]

def get_retriever( session_id: str, k: int = 4,):

    vectorstore = get_or_create_collection(session_id)

    # 1. Dense Retriever fetches 20 candidates
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 20})

    try:
        client = vectorstore.client
        records, _ = client.scroll(collection_name=session_id, limit=10000, with_payload=True)
        
        if not records:
            base_retriever = CustomRerankerRetriever(base_retriever=dense_retriever, top_n=k)
        else:
            docs = []
            for record in records:
                page_content = record.payload.get("page_content", "")
                metadata = record.payload.get("metadata", {})
                docs.append(Document(page_content=page_content, metadata=metadata))
                
            bm25_retriever = BM25Retriever.from_documents(docs)
            bm25_retriever.k = 20
            
            hybrid_retriever = CustomHybridRetriever(
                dense_retriever=dense_retriever,
                bm25_retriever=bm25_retriever
            )
            
            base_retriever = CustomRerankerRetriever(
                base_retriever=hybrid_retriever, 
                top_n=k
            )
            
        # 5. Agentic RAG (Multi-Query)
        llm = get_llm(temperature=0.0)
        agentic_retriever = CustomMultiQueryRetriever(
            base_retriever=base_retriever,
            llm=llm
        )
        
        # 6. Corrective RAG (Evaluator + Web Search Fallback)
        final_crag_retriever = CorrectiveRetriever(
            base_retriever=agentic_retriever,
            llm=llm
        )
        
        print("6-Layer Ultimate RAG (CRAG + Agentic + Rerank + Hybrid) initialized successfully!")
        return final_crag_retriever
        
    except Exception as e:
        print(f"Failed to build complex retriever: {e}")
        return CustomRerankerRetriever(base_retriever=dense_retriever, top_n=k)






