# 🌟 Complete Feature List of Your ChatGPT Clone

This file lists every single feature currently active in your full-stack ChatGPT clone, divided into **Core App Features** and the **10 Advanced AI/RAG Features** (The Brain).

---

## 💻 1. Core Application Features

### Frontend (React + TypeScript + Tailwind)
- **ChatGPT-like UI**: A beautiful, responsive chat interface that looks and feels exactly like ChatGPT.
- **Chat History Management**: Create new chats, switch between past conversations, and delete old chats permanently from the sidebar.
- **Real-Time Streaming**: Words appear on the screen one by one as the AI thinks, exactly like OpenAI's website.
- **Document Upload**: A smooth drag-and-drop or click-to-upload button to ingest PDFs, DOCX, and TXT files directly into the current chat context.

### Backend (FastAPI + SQL)
- **Persistent SQL Database**: Every message, session, and user action is saved permanently in a local SQLite database (`chat.db`).
- **REST API Architecture**: Clean API endpoints for handling `GET /chats`, `POST /chat/stream`, and `POST /upload`.
- **Dynamic LLM Factory Pattern**: Swap between `Groq` (ultra-fast cloud), `Ollama` (offline local), or `Gemini` simply by changing one word in the `.env` file!

---

## 🧠 2. The 10 Advanced RAG Features 

Here are the 10 cutting-edge RAG (Retrieval-Augmented Generation) techniques implemented in this project to prevent hallucinations and provide Enterprise-grade answers:

### 1. Basic RAG (Document Retrieval)
Instead of relying on the AI's memory, the system converts your uploaded PDFs into Vectors (numbers) and saves them in a **Qdrant Vector Database**. When you ask a question, it fetches the most relevant text from your document to answer it.

### 2. Metadata Filtering
Every chunk of text is tagged with metadata (like `source: contract.pdf` and `file_type: pdf`). Before the AI searches the massive database, it uses these tags to filter out irrelevant files, saving compute power and increasing accuracy.

### 3. Advanced Chunking Strategies
Instead of just splitting text randomly, we use **Recursive Character Splitting** with overlap. This ensures that a sentence or a paragraph doesn't get cut in half, keeping the meaning intact.

### 4. Contextual Chunking
Normal chunking destroys the global context of a document. We use a secondary AI to read the *entire* document, generate a global 1-sentence summary, and inject that summary into *every single chunk*. Now, every piece of text knows what document it belongs to!

### 5. Hybrid Search & Reciprocal Rank Fusion (RRF)
Vector Search (Dense) is great for understanding "meaning", but terrible at finding exact names or IDs. We implemented **BM25 (Sparse Search)** alongside Vector Search. The system searches both ways and merges the scores mathematically using **RRF** to find the absolute best match.

### 6. Cross-Encoder Reranking
The database initially returns the Top 20 results. But Vector databases aren't perfect. We pass those 20 results through a local HuggingFace AI (`FlashRank Cross-Encoder`). This AI reads the results, scores their actual relevance to the question, and re-orders them, keeping only the top 4.

### 7. Query Transformation (Multi-Query)
Users often ask poorly-worded questions. Before searching the database, our **Multi-Query Agent** rewrites the user's question into 3 different, optimized variations. It searches the database for all 3 variations to ensure no relevant data is missed.

### 8. Agentic RAG (Router Agent)
When you ask a question, an **AI Router Agent** secretly decides what to do:
- If it's a PDF question: It routes to the Qdrant DB.
- If it's a real-time question (e.g. "Who won the match?"): It routes to the Tavily Web Search Tool.
- If it's a casual greeting: It routes to normal Chat.

### 9. Multimodal RAG (Vision AI)
Normal RAG throws away images in PDFs. When you upload a PDF with charts or photos, our system uses `PyMuPDF` to extract the images and sends them to a local **LLaVA Vision Model**. LLaVA converts the visual data into searchable text descriptions!

### 10. CRAG (Corrective RAG) & Self-RAG
- **CRAG**: If the database returns irrelevant documents, the Evaluator AI rejects them and falls back to Web Search instead of guessing.
- **Self-RAG (Hallucination Checker)**: Before sending the final answer to the user, an internal "Judge AI" reviews the answer. If the answer contains made-up facts (hallucinations), it forces the AI to rewrite it!

---
*(These 10 features represent the absolute pinnacle of GenAI Engineering in 2026.)*
