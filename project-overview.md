# PDF-to-Discovery Study App: Full Overview

## 1. The Picture (what and why)

A desktop study app that turns a PDF into short discovery cards so you actually remember what you read.

**Flow:** import PDF -> pick a topic -> hook -> reveal (explanation + analogy) -> recall question -> session progress.

**Card stages:** Hook (curious question) -> Reveal (explanation + analogy, with source pages) -> Recall (question + answer).

**Core rule:** generated content is grounded in retrieved PDF passages, with source page numbers. No invented citations.

---

## 2. Stack and why

| Layer | Tech | Why |
|---|---|---|
| Desktop shell | Tauri 2 | Lightweight desktop packaging |
| Frontend | React + TypeScript + Vite | Interactive cards, type safety, fast dev |
| Backend | FastAPI (Python) | PDF + AI pipeline lives in Python |
| PDF extraction | PyMuPDF4LLM | Text with page info |
| Embeddings | TBD (Phase 3) | Semantic search |
| Vector DB | ChromaDB | Chunks + embeddings |
| App DB | SQLite via SQLAlchemy | Documents + sessions, zero setup |
| LLM | Hosted API | Explanations, analogies, recall Qs |
| Frontend <-> backend | HTTP + JSON | Simple, decoupled |

---

## 3. Architectural principles

- Keep it simple; add complexity only when the MVP needs it.
- UI separate from logic.
- API keys stay in the backend, never the frontend.
- Ground output in retrieved passages; preserve source pages.
- Backend binds to `127.0.0.1` only.
- One layer at a time, test each before moving on.

---

## 4. MVP scope

**In:** text-based PDFs, upload + extraction, page numbers, topic selection, chunking + semantic retrieval, hosted LLM, discovery cards, recall Qs, basic session progress, desktop UI.

**Deferred:** OCR/scanned PDFs, agents, auth/accounts, cloud sync, spaced repetition, cross-device progress, local LLMs, production deployment.

---

## 5. Phases

| Phase | Name | Status |
|---|---|---|
| 1 | Define the MVP | Done |
| 2 | Backend foundation | Designed, being built |
| 3 | Document understanding + retrieval | Planned |
| 4 | Discovery engine (LLM) | Planned |
| 5 | Desktop frontend | Planned |
| 6 | Integration + testing | Planned |
| 7 | Refinement | Planned |

### Phase 3 (planned)
- Detect TOC/headings -> topic hierarchy.
- Chunk ~1,000 chars, ~200 overlap, keep page + doc id on every chunk.
- Embed, store in ChromaDB, retrieve passages per topic.
- Evaluate retrieval with example questions; tune chunking.

### Phase 4 (planned)
Pipeline: topic -> retrieve passages -> build prompt -> LLM -> request structured JSON -> validate -> check source pages match retrieved material -> return cards.

Card types: `hook`, `explanation` (with `analogy`, `source_pages`), `recall` (`question`, `answer`).

Reliability: handle malformed LLM output, API errors, usage limits; never invent citations; separate document-backed facts from extra examples.

### Phase 5 (planned)
Screens: Library, Document Explorer, Discovery View, Session Summary. Progressive reveals, progress indicator, separate recall-performance indicator, loading/empty/error states. Dark mode only if time permits.

### Phase 6-7 (planned)
Wire everything together, test the failure scenarios (bad PDFs, no retrieval results, LLM timeout/malformed output), then refine topic detection, retrieval, prompt quality, API usage, packaging.

---

## 6. Phase 2 decisions (locked)

| Decision | Choice |
|---|---|
| Extraction | Background task; frontend polls status |
| Original PDF | Deleted after extraction (success or failure) |
| Size cap | 20 MB |
| Low-content PDFs | No minimum-text rejection; soft `low_text` flag; only zero text fails |
| DB access | SQLite + SQLAlchemy, `create_all`, no Alembic |
| Source of truth after upload | Extracted JSON (`extracted/{id}.json`) |

**Trade-off:** improving extraction later means re-uploading, since the PDF is deleted.

### Structure
```
backend/
  app/
    main.py, config.py, errors.py
    api/        health.py, documents.py
    services/   pdf_extraction.py, storage.py
    db/         models.py, session.py
    schemas/    document.py
  data/         tmp/, extracted/, app.db (gitignored)
  tests/fixtures/
  requirements.txt
```

### API
| Method | Path | Result |
|---|---|---|
| GET | `/health` | `{status: "ok"}` |
| POST | `/documents` | 202 `{id, status: "processing"}` |
| GET | `/documents` | list |
| GET | `/documents/{id}` | status, metadata, error info if failed |
| GET | `/documents/{id}/pages/{n}` | `{page, text}` |
| DELETE | `/documents/{id}` | 204 |

Status: `processing | ready | failed`. Error shape: `{"error": {"code", "message"}}`.

Instant errors: `not_a_pdf`, `file_too_large`, `not_found`. Failure codes saved on the doc: `corrupt_pdf`, `encrypted_pdf`, `no_extractable_text`.

### Upload flow
1. Check `%PDF` magic bytes + 20 MB cap -> instant error if bad.
2. Save to `data/tmp/{id}.pdf`, create row `status=processing`.
3. Return 202.
4. Background task: extract per-page text -> write `extracted/{id}.json` (`[{page, text}]`, 1-based) -> update row (`page_count`, `char_count`, `low_text`, `status=ready`).
5. `finally`: always delete temp PDF. On failure set `status=failed` + error code/message.

### Cleanup
- Startup: mark stuck `processing` rows `failed`, wipe `tmp/`.
- Delete endpoint: remove row + JSON.

---

## 7. Implementation decisions made while building

- **Logging:** `logging.basicConfig` once in `main.py`; `logger = logging.getLogger(__name__)` per file. Levels: `warning` for rejected input, `exception` only inside `except` (gives traceback). Use `%s` args.
- **Errors:** `AppError(code, message, status_code)` + one handler that logs and returns the shared error shape. Failure codes for background extraction are stored on the document row, not raised (the 202 already went out).
- **Filename:** `file.filename` from `UploadFile` is display-only (can be `None`, untrusted). Files on disk use the UUID.
- **Size check:** use `len(contents)`, not `file.size` (may be `None`).
- **DB model:** `Document` with `id, filename, status, page_count, char_count, low_text, error_code, error_message, created_at`. No `file_path` column: the PDF is deleted, and the JSON path is derived from the id (`extracted/{id}.json`), which also survives moving `data/`.
- **Sessions:** `check_same_thread=False` for SQLite. Background task opens its own `SessionLocal()` and closes it in `finally`; never reuse the request's session.

---

## 8. Implementation order (Phase 2)

1. Setup: venv, requirements, `main.py` + `/health`
2. `config.py`
3. DB: `models.py`, `session.py`, `create_all`
4. `pdf_extraction.py` (test against fixtures first, riskiest piece)
5. `storage.py`
6. `errors.py`
7. Endpoints (POST + background task, then GET, pages, DELETE)
8. Startup cleanup
9. End-to-end tests

**Tests:** valid PDF (202 -> ready, correct pages), wrong type, over 20 MB, encrypted, corrupt, zero-text, low-text, bad page/id, startup recovery, delete, temp PDF removed on success and failure.

---

## 9. Development rules

1. Plan each phase before implementing.
2. Understand decisions before committing.
3. One layer at a time, tested.
4. Reuse code you understand.
5. No unnecessary abstractions or dependencies.
6. Validate assumptions with small tests.
7. Working end-to-end beats visual polish.
8. Record decisions and trade-offs.
9. No features outside the MVP without a clear reason.
10. It's a learning project and a portfolio piece.

**Next step:** finish Phase 2, then Phase 3 (chunking + retrieval).
