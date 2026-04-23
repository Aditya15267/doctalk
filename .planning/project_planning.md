# DocTalk — Project Plan

**Methodology:** Agile-inspired, solo dev  
**Daily commitment:** 1-2 hours  
**Estimated total:** ~3.5 weeks  
**Skill level:** Intermediate  

---

## How to Use This File

- Work top to bottom — each phase depends on the one before it
- Check off tasks with `[x]` as you complete them
- Each task is scoped to fit in **one focused session (1-2 hrs)**
- Never start a new phase until the previous one is fully checked off
- If a task blocks you, note it inline with `⚠️ BLOCKED: reason` and move to the next unblocked task

---

## Phase 0 — Project Setup
> Goal: Empty repo → running skeleton on your machine. No AI logic yet.  
> Estimated time: 2-3 days

### Repo & Structure
- [X] Create GitHub repo named `doctalk`
- [X] Add `.gitignore` (Python + Node)
- [X] Add `LICENSE` (MIT)
- [X] Create folder structure:
  ```
  doctalk/
  ├── backend/
  ├── frontend/
  ├── .github/workflows/
  └── README.md  ← (already written)
  ```
- [X] Make first commit: "chore: initial project structure"

### Backend Skeleton
- [X] Create Python virtual environment inside `backend/`
- [X] Create `requirements.txt` with initial dependencies:
  ```
  fastapi
  uvicorn[standard]
  python-multipart
  pydantic
  python-dotenv
  ```
- [X] Create `backend/main.py` with a single health check endpoint:
  ```python
  GET /health → {"status": "ok"}
  ```
- [X] Create `backend/.env.example` with all required keys (empty values)
- [X] Verify: `uvicorn main:app --reload` runs without errors
- [X] Commit: "feat: backend skeleton with health check"

### Frontend Skeleton
- [X] Scaffold with Vite: `npm create vite@latest frontend -- --template react`
- [X] Delete boilerplate (App.css content, logo, counter component)
- [X] Create empty placeholder components:
  - `src/components/UploadZone.jsx`
  - `src/components/ChatWindow.jsx`
  - `src/components/MessageBubble.jsx`
  - `src/components/CitationCard.jsx`
- [X] Create `src/api/client.js` (empty for now)
- [X] Verify: `npm run dev` runs without errors
- [X] Commit: "feat: frontend skeleton with placeholder components"

### CI/CD Skeleton
- [X] Create `.github/workflows/ci.yml`:
  - Trigger: push to `main`, all pull requests
  - Jobs: `backend-test` (pip install + pytest), `frontend-check` (npm install + build)
- [X] Push to GitHub — verify both CI jobs pass (they will, nothing to test yet)
- [X] Commit: "ci: add GitHub Actions pipeline"

---

## Phase 1 — PDF Processing (Backend Core)
> Goal: Given a PDF, produce a list of embedded chunks stored in ChromaDB.  
> No API yet — just the service functions working correctly.  
> Estimated time: 4-5 days

### Dependencies
- [X] Add to `requirements.txt`:
  ```
  pdfplumber
  sentence-transformers
  chromadb
  ```
- [X] Run `pip install -r requirements.txt` and verify no errors
- [X] Commit: "chore: add PDF processing dependencies"

### PDF Extraction Service
- [X] Create `backend/services/pdf_processor.py`
- [X] Write `extract_text(file_bytes: bytes) -> str`:
  - Uses `pdfplumber` to extract raw text from PDF bytes
  - Returns cleaned plain text string
- [X] Write `chunk_text(text: str, chunk_size=500, overlap=50) -> list[dict]`:
  - Splits text into overlapping chunks
  - Each chunk: `{"text": str, "chunk_index": int, "page_number": int}`
- [X] Write a quick local test (not pytest yet — just `if __name__ == "__main__"`):
  - Point it at any real PDF on your machine
  - Print first 3 chunks to verify output looks right
- [X] Commit: "feat: PDF text extraction and chunking service"

### Embedding Service
- [X] Create `backend/services/embedder.py`
- [X] Write `get_embedder()` — loads `all-MiniLM-L6-v2` model once (singleton pattern)
- [X] Write `embed_chunks(chunks: list[dict]) -> list[dict]`:
  - Adds `"embedding": list[float]` to each chunk dict
- [X] Write `embed_query(query: str) -> list[float]`
- [X] Local test: embed 3 chunks, print shape of embedding vector
- [X] Commit: "feat: sentence-transformers embedding service"

### Vector Store Service
- [X] Create `backend/services/vector_store.py`
- [ ] Write `store_chunks(session_id: str, chunks: list[dict]) -> None`:
  - Creates a ChromaDB collection named by session_id
  - Stores text + embedding + metadata (page_number, chunk_index)
- [X] Write `search_chunks(session_id: str, query_embedding: list[float], top_k=5) -> list[dict]`:
  - Returns top-K most similar chunks with their metadata and similarity score
- [X] Write `delete_session(session_id: str) -> None` (cleanup utility)
- [X] Local test: store 5 chunks, search with a question, verify relevant chunks return
- [X] Commit: "feat: ChromaDB vector store service"

### Wire the Pipeline Together
- [ ] Create `backend/services/ingest.py`
- [ ] Write `ingest_pdf(session_id: str, file_bytes: bytes) -> dict`:
  - Calls extract → chunk → embed → store in sequence
  - Returns `{"chunks": int, "pages": int}`
- [ ] Local test: run ingest on a real PDF end-to-end, verify ChromaDB is populated
- [ ] Write first real pytest test in `backend/tests/test_ingest.py`:
  - Test with a small sample PDF
  - Assert chunk count > 0
  - Assert ChromaDB collection exists for session_id
- [ ] Commit: "feat: end-to-end PDF ingest pipeline + tests"

---

## Phase 2 — Database (Chat History)
> Goal: SQLite stores and retrieves sessions, messages, and citations.  
> Estimated time: 2 days

### Dependencies
- [ ] Add to `requirements.txt`:
  ```
  aiosqlite
  ```
- [ ] Commit: "chore: add aiosqlite dependency"

### Database Setup
- [ ] Create `backend/db/database.py`:
  - Async SQLite connection using `aiosqlite`
  - `init_db()` function — creates all tables on startup if they don't exist
- [ ] Create all 3 tables from the data model:
  ```sql
  sessions (session_id, filename, pages, chunk_count, created_at, status)
  messages (message_id, session_id, role, content, created_at)
  citations (citation_id, message_id, chunk_text, page_number, chunk_index, score)
  ```
- [ ] Commit: "feat: SQLite schema with sessions, messages, citations"

### Database Operations
- [ ] Create `backend/db/session_store.py`:
  - `create_session(session_id, filename, pages, chunk_count)`
  - `get_session(session_id) -> dict | None`
- [ ] Create `backend/db/message_store.py`:
  - `save_message(session_id, role, content) -> message_id`
  - `save_citations(message_id, citations: list[dict])`
  - `get_history(session_id) -> list[dict]`
- [ ] Write pytest tests in `backend/tests/test_db.py`:
  - Create session → get session → assert fields match
  - Save message + citations → get history → assert returned
- [ ] Commit: "feat: database CRUD operations + tests"

---

## Phase 3 — API Layer (FastAPI Endpoints)
> Goal: All 3 endpoints working and testable via curl or Postman.  
> Estimated time: 3 days

### Pydantic Models
- [ ] Create `backend/models/schemas.py`:
  ```python
  class UploadResponse(BaseModel)
  class ChatRequest(BaseModel)
  class CitationSchema(BaseModel)
  class MessageSchema(BaseModel)
  class HistoryResponse(BaseModel)
  ```
- [ ] Commit: "feat: Pydantic request/response schemas"

### Upload Endpoint
- [ ] Create `backend/routes/upload.py`
- [ ] Implement `POST /upload`:
  - Accept `UploadFile` from FastAPI
  - Validate: must be PDF, under 10MB
  - Generate `session_id` (uuid4)
  - Call `ingest_pdf(session_id, file.read())`
  - Save session to SQLite
  - Return `UploadResponse`
- [ ] Register router in `main.py`
- [ ] Test with curl:
  ```bash
  curl -X POST http://localhost:8000/upload \
    -F "file=@yourdoc.pdf"
  ```
- [ ] Commit: "feat: POST /upload endpoint"

### LLM Service
- [ ] Add to `requirements.txt`: `anthropic`
- [ ] Create `backend/services/llm.py`
- [ ] Write `build_prompt(question: str, chunks: list[dict]) -> str`:
  - System message: "Answer only from the provided context. If the answer is not in the context, say so."
  - Includes all retrieved chunk texts as numbered context blocks
- [ ] Write `stream_answer(question: str, chunks: list[dict]) -> AsyncGenerator`:
  - Calls Anthropic API with `stream=True`
  - Yields tokens one by one
- [ ] Test locally: call with a sample question and chunks, verify streaming output
- [ ] Commit: "feat: LLM service with prompt builder and streaming"

### Chat Endpoint
- [ ] Create `backend/routes/chat.py`
- [ ] Implement `POST /chat` with SSE streaming:
  - Validate session exists in SQLite
  - Embed the question
  - Search ChromaDB for top-5 chunks
  - Save user message to SQLite
  - Stream LLM response token by token
  - On stream complete: save assistant message + citations to SQLite
  - SSE event format: `data: {"type": "token", "value": "..."}` and `data: {"type": "done", "citations": [...]}`
- [ ] Test with curl:
  ```bash
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"session_id": "your-id", "question": "What is this document about?"}'
  ```
- [ ] Commit: "feat: POST /chat endpoint with SSE streaming"

### History Endpoint
- [ ] Create `backend/routes/history.py`
- [ ] Implement `GET /history/{session_id}`:
  - Fetch session + all messages + citations from SQLite
  - Return `HistoryResponse`
  - Return 404 if session not found
- [ ] Test with curl
- [ ] Commit: "feat: GET /history/{session_id} endpoint"

### API Tests
- [ ] Write `backend/tests/test_api.py` using FastAPI `TestClient`:
  - Test upload with a valid PDF → assert 200 + session_id
  - Test upload with invalid file type → assert 400
  - Test upload with oversized file → assert 400
  - Test history with unknown session_id → assert 404
- [ ] Verify all tests pass in CI
- [ ] Commit: "test: API endpoint integration tests"

---

## Phase 4 — Frontend
> Goal: Working UI that connects to the backend end-to-end.  
> Estimated time: 4-5 days

### API Client
- [ ] Implement `src/api/client.js`:
  - `uploadPDF(file) -> Promise<{session_id, filename, pages, chunks}>`
  - `streamChat(session_id, question, onToken, onDone, onError)` — handles SSE
  - `getHistory(session_id) -> Promise<{messages}>`
- [ ] Commit: "feat: API client with upload, chat, and history calls"

### Upload Zone Component
- [ ] Implement `UploadZone.jsx`:
  - Drag-and-drop area + click to browse
  - Shows file name and size on selection
  - Upload button triggers `uploadPDF()`
  - Shows spinner during upload
  - Shows error message on failure
  - On success: calls `onUploadComplete(session_id)`
- [ ] Basic CSS: centered card, dashed border on drag, hover state
- [ ] Test: upload a real PDF, verify session_id returned and stored in localStorage
- [ ] Commit: "feat: UploadZone component with drag-and-drop"

### Chat Window Component
- [ ] Implement `ChatWindow.jsx`:
  - Renders list of `MessageBubble` components
  - Text input + send button at the bottom
  - Calls `streamChat()` on submit
  - Appends tokens to the assistant message as they stream in
  - Auto-scrolls to bottom on new message
  - Disables input while streaming
- [ ] Commit: "feat: ChatWindow component with SSE streaming"

### Message Bubble Component
- [ ] Implement `MessageBubble.jsx`:
  - User messages: aligned right, different background
  - Assistant messages: aligned left
  - Shows a blinking cursor while streaming
  - Renders `CitationCard` components below assistant messages
- [ ] Commit: "feat: MessageBubble component"

### Citation Card Component
- [ ] Implement `CitationCard.jsx`:
  - Collapsed by default — shows "Source: Page X"
  - Expands on click to show the raw chunk text
  - Visually distinct from the message bubble (smaller font, muted color)
- [ ] Commit: "feat: CitationCard with expand/collapse"

### Session Persistence (localStorage)
- [ ] On successful upload: save `session_id` and `filename` to localStorage
- [ ] On app load: check localStorage for existing session_id
- [ ] If found: call `GET /history/{session_id}` and restore the conversation
- [ ] If not found: show the upload screen
- [ ] Add a "New document" button that clears localStorage and resets state
- [ ] Commit: "feat: session persistence with localStorage and history restore"

### App Layout & Wiring
- [ ] Implement `App.jsx`:
  - State: `session` (null or `{session_id, filename}`)
  - If no session: render `<UploadZone />`
  - If session: render `<ChatWindow />` with document name in header
- [ ] Add minimal global CSS: font, colors, max-width container, mobile-friendly
- [ ] Commit: "feat: App layout and component wiring"

---

## Phase 5 — Integration & Polish
> Goal: Everything works together seamlessly. Edge cases handled. Ready to show.  
> Estimated time: 3-4 days

### End-to-End Testing
- [ ] Upload a research paper PDF → ask 5 different questions → verify answers are grounded
- [ ] Upload a contract PDF → ask questions → verify citations point to correct pages
- [ ] Refresh the page mid-conversation → verify history restores correctly
- [ ] Try uploading a non-PDF → verify error message shows in UI
- [ ] Try uploading a large file → verify size error shows in UI
- [ ] Ask a question that has no answer in the document → verify model says so (no hallucination)

### Error Handling
- [ ] Backend: all routes wrapped in try/except with proper HTTP status codes
- [ ] Frontend: all API calls have `.catch()` with user-facing error messages
- [ ] SSE stream: handle `type: "error"` event and show message in UI
- [ ] If history fetch fails on load: gracefully fall back to upload screen

### UX Polish
- [ ] Loading state on app startup (while history is fetching)
- [ ] "Processing your document..." message with estimated wait time
- [ ] Empty state message in chat: "Your document is ready. Ask anything."
- [ ] Smooth scroll animation when new messages appear
- [ ] Disable send button with visual feedback when question is empty

### CORS Configuration
- [ ] Add CORS middleware to FastAPI allowing the Vercel frontend domain
- [ ] Test that frontend on `localhost:5173` can reach backend on `localhost:8000`
- [ ] Commit: "fix: CORS configuration for frontend-backend connection"

---

## Phase 6 — Deployment
> Goal: Live on the internet, accessible via a public URL.  
> Estimated time: 1-2 days

### Backend → Railway
- [ ] Create `backend/Procfile`: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Push to GitHub
- [ ] Connect Railway to GitHub repo, set root to `backend/`
- [ ] Add all environment variables from `.env.example` in Railway dashboard
- [ ] Verify health check endpoint returns 200 on Railway URL
- [ ] Commit: "chore: add Procfile for Railway deployment"

### Frontend → Vercel
- [ ] Update `src/api/client.js` to use env variable for backend URL:
  ```js
  const API_BASE = import.meta.env.VITE_API_URL
  ```
- [ ] Add `VITE_API_URL` = Railway backend URL in Vercel dashboard
- [ ] Connect Vercel to GitHub repo, set root to `frontend/`
- [ ] Verify frontend loads and can reach backend
- [ ] Commit: "chore: use env variable for API base URL"

### CI/CD Final Pass
- [ ] Update `ci.yml` to deploy to Railway on push to `main` (backend)
- [ ] Vercel auto-deploys on push to `main` (no config needed)
- [ ] Verify full pipeline: push → tests pass → both services redeploy

### Smoke Test (Production)
- [ ] Upload a real PDF on the live URL
- [ ] Ask 3 questions, verify answers and citations work
- [ ] Refresh page, verify history restores
- [ ] Share URL with one other person and have them test it

---

## Phase 7 — README Final Pass
> Goal: GitHub repo looks professional to any recruiter who lands on it.  
> Estimated time: 1 day

- [ ] Add a demo GIF or screenshot to the README (record with Loom or macOS screenshot)
- [ ] Fill in actual Railway and Vercel URLs in the README
- [ ] Update the "Known Limitations" section with anything discovered during testing
- [ ] Verify all README setup instructions work on a clean machine (or ask someone else to try)
- [ ] Add architecture diagram image to README (screenshot the system design diagram)

---

## Summary

| Phase | Focus | Est. Days |
|---|---|---|
| 0 | Project setup | 2-3 |
| 1 | PDF processing pipeline | 4-5 |
| 2 | Database (chat history) | 2 |
| 3 | API layer (3 endpoints) | 3 |
| 4 | Frontend (React UI) | 4-5 |
| 5 | Integration & polish | 3-4 |
| 6 | Deployment | 1-2 |
| 7 | README final pass | 1 |
| **Total** | | **~20-25 days** |

At 1-2 hours/day → approximately **3.5 weeks**

---

## Git Branch Strategy

```
main          ← always deployable, protected
  └── feat/phase-0-setup
  └── feat/pdf-processing
  └── feat/database
  └── feat/api-upload
  └── feat/api-chat
  └── feat/api-history
  └── feat/frontend-upload
  └── feat/frontend-chat
  └── feat/session-persistence
  └── fix/cors
  └── chore/deployment
```

**Rules:**
- Never commit directly to `main`
- One branch per feature/phase
- Merge via PR (even solo — it keeps your history clean and looks professional on GitHub)
- Write a meaningful PR description: what you built, how to test it

---

## Commit Message Convention

```
feat:    new feature
fix:     bug fix
test:    adding or updating tests
chore:   setup, config, dependencies
refactor: code change with no behaviour change
docs:    README or comments
ci:      GitHub Actions changes
```

Examples:
```
feat: POST /upload endpoint with file validation
fix: ChromaDB session not found returns 404 not 500
test: add integration tests for chat endpoint
chore: add pdfplumber and sentence-transformers to requirements
```

---

*Cross off tasks as you complete them. The plan is a guide, not a cage — if something takes longer, adjust. The goal is a working, deployed project, not a perfect one.*