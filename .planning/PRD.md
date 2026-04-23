# Product Requirements Document (PRD)
## DocTalk — Chat with Your Documents

**Version:** 1.0 (MVP)
**Status:** Draft
**Last Updated:** April 2026
**Author:** [Your Name]

---

## 1. Problem Statement

People receive, download, and are expected to read long PDF documents every day — research papers, reports, contracts, manuals, government documents. Most of it never gets read properly because reading a 60-page PDF to find one answer is slow, tedious, and mentally exhausting.

**The problem is not access to information. It is the time and effort required to extract it.**

---

## 2. Objective

Build a web application that allows any user to upload a PDF document and have a natural conversation with it — asking questions, getting accurate answers, and seeing exactly which part of the document the answer came from.

**Success looks like:** A user uploads a PDF, asks a question in plain English, and gets a relevant, cited answer in under 10 seconds.

---

## 3. Target Users

**Primary:** General public — anyone who regularly reads or needs to extract information from PDF documents. No technical background assumed.

**User personas:**
- A student who needs to quickly understand a 40-page research paper
- A job seeker trying to decode a lengthy employment contract
- A citizen trying to understand a government policy document
- A professional reviewing a vendor's technical report

---

## 4. Core Value Proposition

> "Stop reading. Start asking."

DocTalk saves time by letting users ask questions about a document instead of reading it end to end. The answer comes back in seconds, with a reference to the exact source in the document.

---

## 5. Scope

### In Scope (V1 — MVP)

| Feature | Description |
|---|---|
| PDF Upload | User uploads a single PDF (max 10MB) |
| Document Processing | Text is extracted, chunked, and embedded |
| Chat Interface | User asks questions in natural language |
| AI Answers | LLM generates answers grounded in document content |
| Source Citations | Every answer shows which section of the PDF it came from |
| Chat History | Previous questions and answers are saved per session |

### Out of Scope (V1)

- User authentication / accounts
- Multiple document uploads
- Document comparison
- Mobile app
- Sharing conversations
- Support for file types other than PDF (Word, Excel, etc.)
- Real-time collaboration

> These are candidates for V2 and beyond. Keeping V1 focused is intentional.

---

## 6. Functional Requirements

### 6.1 PDF Upload

- User can upload a PDF via drag-and-drop or file picker
- Accepted format: `.pdf` only
- Max file size: 10MB
- System must show a processing indicator while the document is being embedded
- System must show a clear error if the file is invalid or too large

### 6.2 Document Processing (Backend)

- Extract raw text from the PDF
- Split text into overlapping chunks (e.g., 500 tokens with 50 token overlap)
- Generate vector embeddings for each chunk
- Store embeddings in a local vector database (ChromaDB)
- Associate all chunks with a session ID

### 6.3 Chat Interface

- User sees a chat window after upload is complete
- User types a question in a text input and submits
- The system retrieves the most relevant chunks from the vector DB
- Those chunks are passed as context to the LLM along with the question
- The LLM response streams back token by token (no waiting for full response)

### 6.4 Source Citations

- Every AI response must include a reference indicating which part of the document the answer is from (e.g., page number or section heading if available)
- Citations are shown below the answer in a visually distinct style
- User can see the raw chunk text that was used to generate the answer

### 6.5 Chat History

- All questions and answers in a session are stored locally
- When a user returns to the same session, previous conversation is loaded
- Each session is tied to a document upload
- Sessions are stored using a session ID (no login required in V1)

---

## 7. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Response time | First token streamed within 3 seconds of question submission |
| Upload processing | PDF processed and ready within 15 seconds for a 10MB file |
| Accuracy | Answers must be grounded in document content — no hallucination without citation |
| Availability | 99% uptime (best effort for a portfolio project) |
| Browser support | Chrome, Firefox, Safari (latest versions) |

---

## 8. Technical Constraints

- Backend must be Python (FastAPI)
- Frontend must be React + Vite
- No paid external services in V1 (sentence-transformers for embeddings, ChromaDB locally)
- LLM: Anthropic Claude API (or OpenAI as fallback)
- Deployment: Vercel (frontend) + Railway (backend)

---

## 9. User Flow (Happy Path)

```
1. User lands on homepage
2. User uploads a PDF
3. System shows "Processing your document..." indicator
4. Processing completes → Chat interface appears
5. User types: "What is the main conclusion of this paper?"
6. System retrieves relevant chunks → sends to LLM → streams response
7. Response appears with citation: "Source: Page 12, Section 4.2"
8. User continues asking questions
9. User closes browser — returns later — chat history is restored
```

---

## 10. Success Metrics (MVP)

| Metric | Goal |
|---|---|
| Can a user upload a PDF and get an answer? | Yes, reliably |
| Are answers grounded in the document? | Yes, with citations |
| Is chat history preserved? | Yes, within a session |
| Does it work on a real document? | Tested on 5+ real PDFs |
| Is it deployed and publicly accessible? | Yes |

---

## 11. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| LLM hallucination | Always pass retrieved chunks as context; instruct model to only answer from context |
| Poor PDF text extraction | Use `pdfplumber` which handles most PDFs; document known limitations in README |
| Large PDFs timing out | Cap file size at 10MB; show processing progress |
| ChromaDB data loss on redeploy | Acceptable for V1; document this limitation clearly |

---

## 12. Open Questions

- Should we show a confidence score alongside citations?
- What happens when the PDF is scanned (image-only, no text layer)?
- Should session IDs be stored in localStorage or as URL params?

---

## 13. Timeline (Estimated)

| Phase | Tasks | Estimated Time |
|---|---|---|
| Setup | Repo, project structure, CI/CD skeleton | 1 day |
| Backend Core | PDF processing, chunking, embedding, ChromaDB | 3 days |
| API Layer | FastAPI endpoints for upload and chat | 2 days |
| Frontend | Upload UI, chat interface, streaming | 3 days |
| Integration | Connect frontend + backend, test end-to-end | 2 days |
| Polish | Citations UI, chat history, error handling | 2 days |
| Deployment | Vercel + Railway, GitHub Actions | 1 day |
| **Total** | | **~2 weeks** |

---

*This PRD is a living document. It will be updated as decisions are made during design and development.*