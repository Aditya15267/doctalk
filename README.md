# DocTalk 📄💬
### Chat with your documents. Stop reading, start asking.

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![React](https://img.shields.io/badge/react-18+-61DAFB)
![License](https://img.shields.io/badge/license-MIT-green)

DocTalk is a full-stack AI application that lets you upload a PDF and have a natural conversation with it. Ask questions in plain English, get accurate answers, and see exactly which part of the document the answer came from.

> **Built as a portfolio project demonstrating:** RAG architecture, full-stack development, LLM integration, and production-grade engineering practices.

---

## ✨ Features

- **PDF Upload** — Drag and drop or browse to upload any PDF (up to 10MB)
- **AI-Powered Chat** — Ask questions in plain English, get answers grounded in your document
- **Source Citations** — Every answer shows exactly which section it came from
- **Streaming Responses** — Answers stream token by token, just like ChatGPT
- **Chat History** — Your conversation is saved and restored when you return

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      React + Vite                        │
│              (Upload UI + Chat Interface)                │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / SSE (streaming)
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│                                                          │
│  /upload ──► Extract Text ──► Chunk ──► Embed ──► Store │
│                                                 │        │
│  /chat ──► Embed Query ──► Search ◄─────────────┘        │
│               │                                          │
│               ▼                                          │
│         Claude API ──► Stream Response                   │
└──────────────────────────────────────────────────────────┘
         │                        │
   ChromaDB                   SQLite
  (vectors)                (chat history)
```

### How RAG Works in This App

1. **Ingest** — When you upload a PDF, the text is extracted and split into overlapping chunks
2. **Embed** — Each chunk is converted into a vector (numerical representation of meaning) using `sentence-transformers`
3. **Store** — Vectors are stored in ChromaDB, a local vector database
4. **Query** — When you ask a question, it is also embedded into a vector
5. **Retrieve** — The most semantically similar chunks are retrieved from ChromaDB
6. **Generate** — Those chunks are passed as context to Claude, which generates a grounded answer

---

## 🛠 Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React + Vite | Fast setup, no SSR complexity |
| Styling | Plain CSS Modules | Clean, scoped, no build complexity |
| Backend | FastAPI (Python) | Async-native, perfect for AI/streaming APIs |
| LLM | Anthropic Claude API | Large context window, strong instruction following |
| Embeddings | sentence-transformers | Free, runs locally, no API dependency |
| Vector DB | ChromaDB | Zero setup, runs in-process |
| Database | SQLite | Single file, zero server, perfect for V1 |
| Deployment | Vercel + Railway | Simplest available for this stack |
| CI/CD | GitHub Actions | Automated testing and deployment on push |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- An Anthropic API key ([get one here](https://console.anthropic.com))

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/doctalk.git
cd doctalk
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
uvicorn main:app --reload
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Open the app

Visit `http://localhost:5173` in your browser.

---

## 📁 Project Structure

```
doctalk/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── routes/
│   │   ├── upload.py        # PDF upload + processing endpoint
│   │   └── chat.py          # Chat + streaming endpoint
│   ├── services/
│   │   ├── pdf_processor.py # Text extraction + chunking
│   │   ├── embedder.py      # sentence-transformers wrapper
│   │   ├── vector_store.py  # ChromaDB operations
│   │   └── llm.py           # Claude API + prompt engineering
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response models
│   ├── db/
│   │   └── session_store.py # SQLite chat history
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadZone/  # PDF drag-and-drop upload
│   │   │   ├── ChatWindow/  # Message list + streaming
│   │   │   ├── MessageBubble/ # Individual message + citation
│   │   │   └── CitationCard/  # Source reference display
│   │   ├── hooks/
│   │   │   ├── useUpload.js # Upload state + API call
│   │   │   └── useChat.js   # Chat state + SSE streaming
│   │   ├── api/
│   │   │   └── client.js    # API calls to backend
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions pipeline
│
└── README.md
```

---

## 🔌 API Reference

### `POST /upload`

Upload and process a PDF document.

**Request:** `multipart/form-data`
```
file: <pdf file>
```

**Response:**
```json
{
  "session_id": "abc123",
  "filename": "research_paper.pdf",
  "pages": 24,
  "chunks": 87,
  "status": "ready"
}
```

---

### `POST /chat`

Ask a question about the uploaded document. Returns a streaming response.

**Request:**
```json
{
  "session_id": "abc123",
  "question": "What is the main conclusion of this paper?"
}
```

**Response:** Server-Sent Events (SSE) stream
```
data: {"token": "The"}
data: {"token": " main"}
data: {"token": " conclusion"}
...
data: {"citations": [{"text": "...", "page": 12, "chunk_index": 34}], "done": true}
```

---

### `GET /history/{session_id}`

Retrieve chat history for a session.

**Response:**
```json
{
  "session_id": "abc123",
  "messages": [
    {
      "role": "user",
      "content": "What is the main conclusion?",
      "timestamp": "2026-04-23T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "The main conclusion is...",
      "citations": [...],
      "timestamp": "2026-04-23T10:00:03Z"
    }
  ]
}
```

---

## ⚙️ Environment Variables

```bash
# backend/.env
ANTHROPIC_API_KEY=your_key_here
CHROMA_PERSIST_DIR=./chroma_data
SQLITE_DB_PATH=./doctalk.db
MAX_UPLOAD_SIZE_MB=10
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_CHUNKS=5
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test
```

The CI pipeline runs all tests automatically on every push to `main` and every pull request.

---

## 🚢 Deployment

### Frontend → Vercel

```bash
cd frontend
npm run build
# Connect repo to Vercel — it auto-detects Vite and deploys
```

### Backend → Railway

```bash
# Connect repo to Railway
# Set environment variables in Railway dashboard
# Railway auto-detects Python and deploys via Procfile
```

### CI/CD Pipeline

Every push to `main`:
1. Runs backend tests (`pytest`)
2. Runs frontend lint + build check
3. Deploys to Vercel (frontend) and Railway (backend) on success

---

## 📋 Known Limitations (V1)

- **Scanned PDFs** — If a PDF is image-only (no text layer), text extraction will fail. OCR support is planned for V2.
- **Single document per session** — V1 supports one PDF per chat session.
- **No user accounts** — Sessions are stored locally by session ID. Clearing browser storage removes history.
- **ChromaDB is not persistent on Railway** — Vector data is rebuilt on each deployment. This is acceptable for V1.

---

## 🗺 Roadmap

- [ ] **V1 (Current)** — Single PDF upload, chat, citations, history
- [ ] **V2** — Multiple document support, document comparison
- [ ] **V3** — User accounts, saved sessions, sharing
- [ ] **V4** — Support for Word, Excel, and web page URLs
- [ ] **V5** — Mobile app

---

## 🤝 Contributing

This is a portfolio project but contributions and feedback are welcome.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [Anthropic](https://anthropic.com) for the Claude API
- [ChromaDB](https://www.trychroma.com/) for the vector database
- [sentence-transformers](https://www.sbert.net/) for local embeddings
- [pdfplumber](https://github.com/jsvine/pdfplumber) for PDF text extraction