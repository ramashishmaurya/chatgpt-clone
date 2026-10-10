# 🚀 The Ultimate AI Engineering Guide: Advanced RAG Architecture

This guide breaks down exactly how the **Top 10 Advanced RAG Techniques** are implemented in this project. We have mapped every advanced feature to its specific file and folder so that any developer can easily trace the code, understand the flow, and learn how to build enterprise-grade AI pipelines.

---

## 📁 1. The Dynamic LLM Factory Pattern
**File:** `backend/llm_factory.py`

**What happens here?**
Instead of hardcoding OpenAI or Gemini everywhere, this file acts as the central brain for model selection. It reads your `backend/.env` file and dynamically imports the correct model.
- If `LLM_PROVIDER=groq`, it routes to the lightning-fast Groq LPU (`qwen/qwen3.8-27b`).
- If `LLM_PROVIDER=gemini`, it routes to `gemini-1.5-flash`.
- Otherwise, it falls back to a 100% offline, local **Ollama** model. 
- **Bonus:** It enforces local `nomic-embed-text` embeddings regardless of the chat model, ensuring zero API costs for vectorization.

---

## 📁 2. Data Ingestion: Multimodal & Contextual RAG
**File:** `backend/upload_data.py` (Function: `load_and_split`)

**What happens here?**
When a user uploads a document, it goes through an intense pre-processing phase before hitting the database:
1. **Multimodal RAG (Vision):** The code uses `PyMuPDF (fitz)` to scan the PDF for images and charts. It extracts them, converts them to base64, and sends them to a local **LLaVA Vision Model**. LLaVA generates a text description of the image which is saved as a chunk.
2. **Contextual Chunking:** Normal chunking destroys context (e.g. knowing what document a paragraph belongs to). We use an LLM to read the entire document, summarize it in 1 sentence, and then inject that summary (`[DOCUMENT CONTEXT: ...]`) at the beginning of *every single chunk*.
3. **Metadata Injection:** We inject metadata tags (like `source` and `file_type`) into the chunks for future database filtering.

---

## 📁 3. Storage: Hybrid Search Vector DB
**File:** `backend/vector_store.py`

**What happens here?**
We initialize our **Qdrant Vector Database** here. However, instead of a basic Dense Vector search, we configure Qdrant to use **BM25 Sparse Vectors** as well. 
This means when we search, the database performs both Semantic meaning search (Dense) AND exact Keyword matching (Sparse).

---

## 📁 4. The Retrieval Pipeline: Multi-Query, Reranker, & CRAG
**File:** `backend/retriever.py` (Function: `get_advanced_retriever`)

**What happens here?**
This file builds the pipeline that fetches the answer. It combines 4 advanced techniques:
1. **Agentic Multi-Query:** The `CustomMultiQueryRetriever` takes the user's question and uses an LLM to generate 3 different variations of it. It searches the DB for all 3 variations, fixing cases where the user asked a poorly-worded question.
2. **Hybrid Retrieval:** It fetches results using both Dense and Sparse methods and merges them.
3. **Cross-Encoder Reranking (FlashRank):** The DB returns 20 documents. A local HuggingFace AI (`FlashRank`) reads all 20, scores their actual relevance to the question, and throws away the garbage, keeping only the top 4.
4. **CRAG (Corrective RAG):** The `CRAGEvaluatorRetriever` looks at the final 4 documents. If it deems them "Irrelevant", it completely drops them and falls back to a Web Search (Tavily).

---

## 📁 5. The Brain: Router Agent & Self-RAG
**File:** `backend/rag_services.py`

**What happens here?**
This file is the orchestra conductor. It handles the final decision making and generation:
1. **Router Agent (`route_question`):** Before doing anything, an LLM evaluates the user's prompt and decides: "Should I search the Qdrant DB? Should I search the Web? Or is this just a casual chat (like 'Hi')?"
2. **Streaming Generation (`stream_question`):** It routes the query to the correct pipeline (Document vs Web vs Chat) and begins streaming the response chunk by chunk to the React frontend.
3. **Self-RAG (Hallucination Checker):** Inside `answer_document`, after generating a draft response, an internal Hallucination Checker reviews the answer against the provided context. If the AI made up facts, it throws an error and is forced to rewrite the answer!

---

## 📁 6. Testing the Pipeline
**Folder:** `backend/tests/`

**What happens here?**
This folder contains individual scripts allowing you to isolate and test each feature without running the full frontend:
- `test_factory.py`: Tests if the LLM provider switching works.
- `test_router.py`: Tests if the Agent correctly routes different types of questions.
- `test_upload_pipeline.py`: Tests the metadata and contextual chunking logic.

---
*By reading these files in this exact order (`llm_factory` -> `upload_data` -> `vector_store` -> `retriever` -> `rag_services`), any developer can perfectly understand the flow of this Advanced AI Pipeline.*
