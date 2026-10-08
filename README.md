# Road Monitoring — GenAI + Integration Layer

```
YOLO → risk calc → MySQL → FastAPI → Dashboard
                      └────→ GenAI (Ollama + LangChain) → natural-language answers
```

The database holds the facts; the LLM only phrases them (it never invents counts or rankings).

## Layout

```
road-monitoring/
├── backend/
│   ├── main.py              FastAPI app (all endpoints)
│   ├── database.py          MySQL connection (reads .env)
│   ├── queries.py           SQL query functions
│   ├── ai.py                GenAI layer: 5 questions, router, tool calling
│   ├── yolo_integration.py  save_detection() for the YOLO teammate
│   ├── test_db.py           connection check
│   ├── requirements.txt
│   └── .env.example
├── database/schema.sql      table + sample data
└── frontend/index.html      simple dashboard + chat box
```

## Setup

1. **Database** — run the schema (creates DB, table, 6 sample rows):
   ```bash
   mysql -u root -p < database/schema.sql
   ```
2. **Python packages**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Config** — copy `.env.example` to `.env` and set `DB_PASSWORD`.
4. **LLM** — install [Ollama](https://ollama.com), then:
   ```bash
   ollama pull llama3.1
   ollama list
   ```
   If Ollama isn't running, the API still answers using plain-text fallbacks.

## Run (follow the milestones)

**Milestone 1 — DB + Python**
```bash
cd backend
python test_db.py                      # Database connected successfully!
python -c "from queries import get_high_risk_count as f; print(f())"   # 3
```

**Milestone 2 — LLM**
```bash
python ai.py                           # LLM answers a test sentence
python -c "import ai; print(ai.answer_question('How many high-risk potholes were detected?'))"
```

**Milestone 3 — API + dashboard**
```bash
uvicorn main:app --reload              # http://127.0.0.1:8000  (docs at /docs)
```
Then open `frontend/index.html` in a browser.

**Milestone 4 — YOLO**
```bash
python yolo_integration.py             # inserts one test detection
```
In your teammates' code, after a detection + risk calculation:
```python
from yolo_integration import save_detection
save_detection("Route A", 0.91, "HIGH", 0.87, 23.2599, 77.4126)
```
or POST JSON to `/incidents`.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/statistics` | total / high / medium / low |
| GET | `/routes` | per-route counts, most dangerous first |
| GET | `/incidents?limit=100` | latest detections |
| POST | `/incidents` | add a detection (YOLO → DB) |
| GET | `/priority?limit=5` | top incidents by severity |
| GET | `/report` | AI summary of today's inspection |
| POST | `/ask` | `{"question": "...", "use_tools": false}` |

Set `"use_tools": true` on `/ask` to let the LLM choose DB tools itself (LangChain tool calling, Step 18); it falls back to the keyword router on any failure.

## The 5 supported questions

1. How many high-risk potholes were detected?
2. Which route has the most dangerous potholes?
3. Summarize today's inspection.
4. Which incidents should be inspected first?
5. Show me the road condition of Route A.

## Notes

- `get_daily_summary` only counts rows whose timestamp is **today**. The sample data uses `NOW()`, so re-run `schema.sql` on a new day to refresh it.
- Never commit `.env` (it holds your DB password).
- CORS is open (`*`) for development; restrict it before deploying.
