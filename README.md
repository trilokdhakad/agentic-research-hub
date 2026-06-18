# 🧠 Agentic Research Hub

An Agentic Retrieval-Augmented Generation (RAG) system built using **LangGraph**, **FastAPI**, **React**, **ChromaDB**, and **Ollama**.

The system allows users to upload PDF and TXT documents, generate embeddings, store them in a vector database, extract document-level intelligence, and query the knowledge base through a multi-agent workflow. Unlike traditional RAG systems that directly retrieve and generate responses, this project introduces a planning layer that helps guide document retrieval before answer generation.

---

# ✨ Features

### 📄 Document Management

* Upload PDF and TXT documents
* Automatic chunking and embedding generation
* Duplicate document protection
* Document deletion from the knowledge base
* Indexed document dashboard with chunk statistics

### 🧠 Agentic RAG Pipeline

* Planner Agent generates a retrieval strategy
* Retriever fetches relevant chunks from ChromaDB
* Writer Agent synthesizes grounded responses
* Source attribution for every answer
* Built using LangGraph state-driven workflows

### 🔍 Document Intelligence

* Automatic metadata extraction during upload
* Title generation
* Summary generation
* Keyword extraction
* Metadata persistence and retrieval
* Interactive metadata viewer in the frontend

### 💻 Fully Local AI Stack

* Local LLM execution using Ollama
* Local vector database using ChromaDB
* HuggingFace sentence-transformer embeddings
* No external API dependency required

---

# 🏗️ Architecture

```text
User
 │
 ▼
React Frontend
 │
 ▼
FastAPI Backend
 │
 ├── Document Processing
 │      ├── PDF/TXT Loader
 │      ├── Text Chunking
 │      └── Metadata Extraction
 │
 ├── ChromaDB Vector Store
 │
 └── LangGraph Workflow
        │
        ├── Planner Agent
        ├── Retriever
        └── Writer Agent
```

---

# 🛠️ Tech Stack

## Frontend

* React
* Vite
* Tailwind CSS
* Axios
* Lucide React

## Backend

* FastAPI
* Python

## AI & Orchestration

* LangChain
* LangGraph
* Ollama (Gemma 2B)

## Vector Database

* ChromaDB

## Embeddings

* HuggingFace
* all-MiniLM-L6-v2

---

# 📂 Project Structure

```text
Agentic-Research-Hub/
│
├── backend/
│   ├── main.py
│   ├── rag_graph.py
│   ├── database.py
│   ├── document_utils.py
│   ├── metadata_extractor.py
│   ├── metadata_store.py
│   ├── requirements.txt
│   ├── chroma_db/
│   ├── data/
│   └── metadata/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── README.md
└── .gitignore
```

---

# 🚀 Getting Started

## Prerequisites

* Python 3.10+
* Node.js 18+
* Ollama

Install Ollama:

https://ollama.com

Pull the required model:

```bash
ollama pull gemma:2b
```

Verify installation:

```bash
ollama list
```

Start Ollama:

```bash
ollama serve
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend runs on:

```text
http://localhost:8000
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

---

# 🔄 Workflow

### Upload Phase

```text
Document
    │
    ▼
Loader
    │
    ▼
Chunking
    │
    ├── Metadata Extraction
    │
    └── Embedding Generation
            │
            ▼
        ChromaDB
```

### Question Answering Phase

```text
Question
    │
    ▼
Planner Agent
    │
    ▼
Retriever
    │
    ▼
Writer Agent
    │
    ▼
Answer + Sources
```

---

# 🎯 Challenges Solved

### Multi-Agent Coordination

Implemented a LangGraph workflow where separate agents perform planning, retrieval, and response generation while sharing a common state.

### Metadata Extraction from Local Models

Built a metadata extraction pipeline capable of generating document summaries and keywords using a lightweight local LLM.

### Duplicate Document Handling

Prevented duplicate embeddings and duplicate storage by validating uploaded documents before indexing.

### Local-First Architecture

Designed the system to run entirely on local hardware without requiring cloud-hosted LLM APIs.

---

# 🔮 Future Improvements

* Intent classification and intelligent routing
* Hybrid search (semantic + keyword retrieval)
* Conversation memory
* Streaming responses
* Multi-document comparison
* Citation highlighting
* Docker deployment

---

# 📸 Screenshots

Add screenshots of:

1. Knowledge Base & Document Management
2. Document Intelligence Metadata Viewer
3. Multi-Agent RAG Workflow
4. System Architecture

---

# 👨‍💻 Author

Built as a project to explore:

* Agentic AI Systems
* Retrieval-Augmented Generation (RAG)
* LangGraph Workflows
* Local LLM Deployment
* Document Intelligence Systems
