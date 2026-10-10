# 🌟 Complete Feature List of Your ChatGPT Clone

This file lists every single feature currently active in your full-stack ChatGPT clone, divided into **Core App Features** (Frontend/Basic Backend) and **Advanced AI/RAG Features** (The Brain).

---

## 💻 1. Core Application Features

### Frontend (React + TypeScript + Tailwind)
- **ChatGPT-like UI**: A beautiful, responsive chat interface that looks and feels exactly like ChatGPT.
- **Chat History Management**: Create new chats, switch between past conversations, and delete old chats permanently from the sidebar.
- **Real-Time Streaming**: Words appear on the screen one by one as the AI thinks, exactly like OpenAI's website.
- **Markdown Support**: The chat properly renders code blocks, bold text, bullet points, and tables.
- **Document Upload**: A smooth drag-and-drop or click-to-upload button to ingest PDFs, DOCX, and TXT files directly into the current chat context.

### Backend (FastAPI + SQL)
- **Persistent SQL Database**: Every message, session, and user action is saved permanently in a local SQLite database (`chat.db`).
- **REST API Architecture**: Clean API endpoints for handling `GET /chats`, `POST /chat/stream`, and `POST /upload`.

---

## 🧠 2. Advanced AI & RAG Features (The Brain)

### Dynamic Model Routing
- **LLM Factory Pattern**: Swap between `Groq` (ultra-fast cloud), `Ollama` (100% offline local), or `Gemini` simply by changing one word in the `.env` file. No code changes required!
- **Free Offline Embeddings**: No matter which chat model you use, the system always uses local `nomic-embed-text` to vectorize PDFs, saving API costs.

### Ingestion & Chunking
- **Contextual Chunking**: Before breaking a PDF into small pieces, the AI reads the whole PDF, creates a 1-sentence summary, and attaches that summary to *every single piece* so the AI never loses context.
- **Multimodal RAG (Vision)**: When you upload a PDF with charts, graphs, or photos, the backend uses `PyMuPDF` to extract the images and sends them to a local `LLaVA` vision model to convert the images into searchable text descriptions!
- **Metadata Tagging**: Every chunk is tagged with its source filename and file type so the Vector Database can filter searches easily.

### Retrieval & Search
- **BM25 + Dense Hybrid Search**: Searches the Qdrant database using both "Semantic Meaning" (Dense Vectors) and "Exact Keyword Matching" (BM25 Sparse Vectors).
- **Reciprocal Rank Fusion (RRF)**: Merges the scores of the Dense and Sparse searches mathematically to find the absolute best result.
- **Cross-Encoder Reranking (FlashRank)**: Takes the top 20 search results and uses a HuggingFace AI to read them again and re-rank them, keeping only the top 4 most relevant pieces of information.

### Agentic AI (Reasoning & Evaluation)
- **Agentic Router**: When you ask a question, an AI Agent secretly decides if it needs to search your PDFs, search the Internet, or just chat normally.
- **Multi-Query Generation**: If the Agent searches your PDFs, it rewrites your question 3 different ways to ensure it doesn't miss any data due to bad wording.
- **Tavily Web Search Fallback**: If the PDF doesn't contain the answer, the AI automatically connects to the internet to find real-time data.
- **Corrective RAG (CRAG)**: If the database returns irrelevant documents, the AI rejects them and searches the Web instead.
- **Self-RAG (Hallucination Checker)**: Before sending the final answer to the user, an internal "Judge AI" reviews the answer. If the answer contains made-up facts (hallucinations), it forces the AI to rewrite it!

---
*(This project represents the cutting edge of GenAI Engineering in 2026.)*
