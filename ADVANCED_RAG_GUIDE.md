# 🚀 Enterprise-Grade Advanced RAG Architecture (ChatGPT Clone)

Welcome to the ultimate **AI Engineering** project. This is not just a simple ChatGPT clone; it is a fully modular, locally-hosted, Enterprise-grade RAG (Retrieval-Augmented Generation) pipeline that implements the top 10 most advanced AI research techniques used by Silicon Valley startups today.

---

## 🏗️ 1. The Dynamic LLM Factory Pattern
The backend is completely decoupled from any single AI provider. We use the **Factory Design Pattern** (`llm_factory.py`) to dynamically route traffic based on your `.env` configuration.

- **`LLM_PROVIDER=groq`** ⚡: Uses Groq's LPU (Language Processing Unit) for ultra-fast inference using `qwen/qwen3.8-27b`.
- **`LLM_PROVIDER=ollama`** 🔒: Runs 100% offline and privately on your machine using `llama3`.
- **`LLM_PROVIDER=gemini`** 🌐: Uses Google's `gemini-1.5-flash` via API.
- **Hybrid Strategy**: Even when using Groq/Gemini for chat, the system smartly falls back to local **Ollama (`nomic-embed-text`)** for embeddings, resulting in zero-cost vectorizations.

---

## 🧠 2. The 7-Layer Advanced RAG Pipeline

When a document is uploaded and queried, it goes through a cutting-edge pipeline to ensure zero hallucinations and maximum accuracy:

### Step 1: Multimodal RAG (Vision) 👁️
Normal RAG throws away images in PDFs. Our pipeline uses `PyMuPDF (fitz)` to extract charts, tables, and photos, and sends them to a local Vision model (**LLaVA**) to generate rich text summaries, making visual data searchable.

### Step 2: Contextual Chunking 🧩
Chunking breaks context. We use a secondary LLM to read the *entire* document, generate a global 1-sentence summary, and inject that summary into the metadata of *every single chunk*.

### Step 3: Metadata-Filtered Retrieval 🗂️
Instead of searching the entire Qdrant database, we inject metadata tags (e.g., `file_type`, `source`) into vectors, allowing Qdrant to filter out irrelevant files *before* similarity search begins, drastically saving compute.

### Step 4: Hybrid Search + RRF ⚖️
We don't rely purely on Vector/Dense search (which fails at exact keywords like IDs or names). We use **BM25 (Sparse Search)** combined with **Qdrant (Dense Search)**, and merge their scores using **Reciprocal Rank Fusion (RRF)**.

### Step 5: Cross-Encoder Reranking 🥇
Top 20 results from Hybrid Search are passed through a local HuggingFace Cross-Encoder (`FlashRank`). The Cross-Encoder scores the actual relevance of the document against the query and re-orders them, keeping only the Top 4.

### Step 6: Agentic RAG (Multi-Query + Router) 🤖
The system uses a **ReAct-style Router Pattern**. 
1. The **Router Agent** analyzes the prompt and decides if it needs the `Qdrant DB Tool`, the `Tavily Web Search Tool`, or just casual conversation.
2. The **Multi-Query Agent** takes the user's question, uses an LLM to rewrite it into 3 different variations, searches all 3, and combines the results to overcome poorly worded user queries.

### Step 7: Corrective RAG (CRAG) & Self-RAG 🛑
Before answering, the **Evaluator Agent** reads the retrieved documents. 
- **CRAG**: If the retrieved documents are irrelevant, the AI rejects them and falls back to Web Search (Tavily).
- **Self-RAG**: The LLM writes a draft answer and a strict Hallucination Checker reviews it. If the answer contains hallucinated facts not in the context, it throws an error and forces the LLM to rewrite it!

---

## 💻 Tech Stack
- **Frontend**: React, TypeScript, TailwindCSS, Vite
- **Backend**: FastAPI, Python, LangChain
- **Vector Database**: Qdrant (Local)
- **AI Models**: Groq (Cloud), Ollama LLaMA-3 (Local Text), Ollama LLaVA (Local Vision), Nomic (Local Embeddings)

## 🚀 How to Run

1. **Install Dependencies:**
   ```bash
   cd backend && pip install -r requirements.txt
   cd frontend && npm install
   ```
2. **Start Qdrant (Docker):**
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```
3. **Start the App:**
   ```bash
   # Terminal 1
   cd backend
   uvicorn main:app --reload

   # Terminal 2
   cd frontend
   npm run dev
   ```

*(Built for the modern AI Engineer. Happy Coding!)*
