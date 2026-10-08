# RoadWatch — Intelligent Road Monitoring

A full-stack road-inspection prototype that connects **YOLO/OpenCV detection → risk estimation → MySQL → FastAPI → dashboard → GenAI**.

The system is designed around one important rule:

> **The database produces the facts; the LLM only explains them.**

That means the AI does not invent pothole counts or rankings. It reads the latest structured results from MySQL and turns them into natural-language answers and reports.

---

## 1. What the project does

### Detection and integration

```text
Camera / Video
      ↓
   OpenCV
      ↓
    YOLO
      ↓
Risk Estimation
      ↓
    MySQL
   ↙      ↘
Dashboard  GenAI
             ↓
      Natural-language answers
             ↓
       Human decision
```

### GenAI capabilities

The assistant can answer questions such as:

- **How many high-risk potholes were detected?**
- **Which route has the most dangerous potholes?**
- **Summarize today's inspection.**
- **Which incidents should be inspected first?**
- **Show me the road condition of Route A.**

It also supports:

- Route comparison
- Risk summaries
- Inspection-priority explanations
- Daily inspection reports
- YOLO-to-database integration

---

# 2. Requirements

Install these before starting:

- **Python 3.10+**
- **MySQL Server**
- **Ollama** — optional for AI-generated wording, but recommended
- A modern browser
- Git is optional

Download Ollama from:

**https://ollama.com**

### Recommended local model

For a laptop with limited VRAM/RAM, start with:

```bash
ollama pull llama3.2:1b
```

The project defaults to `llama3.2:1b` because it is much lighter than larger models.

> If you already have a different Ollama model, set `OLLAMA_MODEL` in `backend/.env`.

---

# 3. Project structure

```text
road-monitoring/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── queries.py
│   ├── ai.py
│   ├── yolo_integration.py
│   ├── test_db.py
│   ├── requirements.txt
│   └── .env.example
│
├── database/
│   └── schema.sql
│
├── frontend/
│   └── index.html
│
├── .gitignore
└── README.md
```

### Important

The distributed project intentionally does **not** include:

- `backend/.env`
- Python `venv/`
- `__pycache__/`

Never upload your real `.env` file to GitHub because it can contain your MySQL password.

---

# 4. Run the project — follow this order

Do each step successfully before moving to the next one.

## Step 0 — Open the project

Unzip the project and open a terminal in:

```text
road-monitoring/
```

---

# Step 1 — Create the database

Make sure MySQL Server is running.

## Windows

### Option A — MySQL Workbench

1. Open MySQL Workbench.
2. Connect to your local MySQL server.
3. Open:

```text
database/schema.sql
```

4. Click the lightning-bolt **Execute** button.

### Option B — MySQL command line

Open MySQL:

```powershell
mysql -u root -p
```

Then at the `mysql>` prompt:

```sql
source C:/FULL/PATH/TO/road-monitoring/database/schema.sql;
```

Use your actual path.

Then check:

```sql
SELECT COUNT(*) FROM road_monitoring.potholes;
```

Expected:

```text
6
```

Exit:

```sql
exit;
```

## macOS / Linux

From the project root:

```bash
mysql -u root -p < database/schema.sql
```

Then verify:

```bash
mysql -u root -p
```

```sql
SELECT COUNT(*) FROM road_monitoring.potholes;
```

Expected:

```text
6
```

---

# Step 2 — Create the Python virtual environment

Open a terminal in the project root.

```bash
cd backend
```

Create the environment:

```bash
python -m venv venv
```

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
.\venv\Scripts\activate.bat
```

from Command Prompt, or run the Python commands through the environment directly.

### macOS / Linux

```bash
source venv/bin/activate
```

Your terminal should now show something similar to:

```text
(venv) ...
```

---

# Step 3 — Install dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

If `pip` is not recognized:

```bash
python -m pip install -r requirements.txt
```

---

# Step 4 — Configure MySQL

Inside `backend/`, copy:

```text
.env.example
```

to:

```text
.env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Command Prompt

```cmd
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Open `.env`:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_PASSWORD
DB_NAME=road_monitoring
OLLAMA_MODEL=llama3.2:1b
```

Replace:

```text
YOUR_PASSWORD
```

with your actual MySQL root password.

Do **not** put quotation marks around the password unless your password itself requires them.

---

# Step 5 — Test the database connection

Make sure you are still inside `backend/` and the virtual environment is active.

Run:

```bash
python test_db.py
```

Expected:

```text
Database connected successfully!
```

### Stop here if this fails.

Common causes:

- MySQL isn't running.
- The password in `.env` is incorrect.
- The database wasn't created.
- The wrong Python environment is active.

---

# Step 6 — Test the database queries

Run:

```bash
python -c "from queries import get_high_risk_count as f; print(f())"
```

Expected:

```text
3
```

You can also test:

```bash
python -c "import queries; print(queries.get_statistics())"
```

Expected values:

```text
total = 6
high_risk = 3
medium_risk = 2
low_risk = 1
```

---

# Step 7 — Set up Ollama

Open a **new terminal**.

Check that Ollama is available:

```bash
ollama --version
```

Download the recommended lightweight model:

```bash
ollama pull llama3.2:1b
```

Check:

```bash
ollama list
```

You should see:

```text
llama3.2:1b
```

Test it directly:

```bash
ollama run llama3.2:1b
```

Ask:

```text
Explain what a high-risk pothole is in one sentence.
```

Then exit:

```text
/bye
```

---

# Step 8 — Test the GenAI Python layer

Return to the `backend` terminal with the virtual environment active.

Run:

```bash
python ai.py
```

It should print a short explanation.

You can also test the actual project question:

```bash
python -c "import ai; print(ai.answer_question('How many high-risk potholes were detected?'))"
```

Expected answer should mention:

```text
3 high-risk potholes
```

### If Ollama is unavailable

The API still has deterministic fallback answers.

You may see:

```text
[ai] LLM unavailable ...
```

This is not a database failure. The system will still return the correct database-backed answer.

---

# Step 9 — Start the FastAPI backend

Keep the backend terminal open.

From `backend/`:

```bash
uvicorn main:app --reload
```

If `uvicorn` isn't recognized:

```bash
python -m uvicorn main:app --reload
```

You should see:

```text
Uvicorn running on http://127.0.0.1:8000
```

Keep this terminal running.

---

# Step 10 — Test the API

Open:

**http://127.0.0.1:8000/docs**

FastAPI will show interactive API documentation.

Try:

```text
GET /statistics
```

You should get:

```json
{
  "total": 6,
  "high_risk": 3,
  "medium_risk": 2,
  "low_risk": 1
}
```

Try:

```text
GET /routes
```

Then try:

```text
POST /ask
```

with:

```json
{
  "question": "How many high-risk potholes were detected?"
}
```

---

# Step 11 — Open the dashboard

You do **not** need a separate frontend server.

Simply double-click:

```text
frontend/index.html
```

The RoadWatch dashboard should open in your browser.

It automatically refreshes the database data every 5 seconds.

You should see:

```text
Total detections    6
High risk           3
Medium risk         2
Low risk            1
```

The dashboard contains:

- Live KPI cards
- Route condition visualization
- Inspection-priority ranking
- Latest incidents table
- AI assistant
- One-click example questions
- Today's AI inspection report
- API documentation shortcut
- Live API connection status

---

# Step 12 — Test the AI assistant

Click one of the suggested questions.

For example:

```text
How many high-risk potholes were detected?
```

Expected:

```text
3 high-risk potholes were detected.
```

Try:

```text
Which route has the most dangerous potholes?
```

Try:

```text
Summarize today's inspection.
```

Try:

```text
Which incidents should be inspected first?
```

Try:

```text
Show me the road condition of Route A.
```

You can also type your own question.

---

# Step 13 — Generate the daily report

In the dashboard, click:

**Generate today's report**

The dashboard calls:

```text
GET /report
```

The backend:

```text
MySQL
  ↓
Today's statistics
  ↓
GenAI
  ↓
Inspection report
```

---

# Step 14 — Simulate a YOLO detection

Keep the FastAPI server running.

Open a **second terminal**.

Go to the backend:

```bash
cd backend
```

Activate the same virtual environment.

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
source venv/bin/activate
```

Run:

```bash
python yolo_integration.py
```

This inserts one additional high-risk detection.

Before:

```text
High risk: 3
```

After:

```text
High risk: 4
```

The dashboard should update within approximately 5 seconds.

Ask:

```text
How many high-risk potholes were detected?
```

The answer should now be:

```text
4 high-risk potholes were detected.
```

---

# 5. Connecting the real YOLO pipeline

The YOLO teammate does not need to modify the dashboard or GenAI code.

After YOLO detects a pothole and the risk engine calculates its values, call:

```python
from yolo_integration import save_detection

save_detection(
    route="Route A",
    confidence=0.91,
    risk_level="HIGH",
    severity_score=0.87,
    latitude=23.2599,
    longitude=77.4126
)
```

The flow becomes:

```text
YOLO detection
      ↓
Risk calculation
      ↓
save_detection()
      ↓
MySQL
      ↓
┌─────┴─────┐
↓           ↓
Dashboard   GenAI
```

---

# 6. Alternative: POST a detection

The YOLO system can also send JSON to:

```text
POST http://127.0.0.1:8000/incidents
```

Example:

```json
{
  "route": "Route A",
  "confidence": 0.91,
  "risk_level": "HIGH",
  "severity_score": 0.87,
  "latitude": 23.2599,
  "longitude": 77.4126
}
```

This is useful if the YOLO pipeline is written in a separate application.

---

# 7. API reference

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API health/message |
| GET | `/statistics` | Total/high/medium/low counts |
| GET | `/routes` | Route-wise risk statistics |
| GET | `/incidents` | Latest detections |
| POST | `/incidents` | Add a YOLO detection |
| GET | `/priority` | Highest-severity incidents |
| GET | `/report` | Today's AI-generated report |
| POST | `/ask` | Natural-language GenAI query |

### `/ask`

Request:

```json
{
  "question": "Which route has the most dangerous potholes?"
}
```

Optional tool-calling mode:

```json
{
  "question": "Which route has the most dangerous potholes?",
  "use_tools": true
}
```

Tool calling is optional. The default keyword router is deliberately retained as a reliable fallback.

---

# 8. Troubleshooting

## `Access denied for user 'root'`

Your MySQL credentials are wrong.

Check:

```text
backend/.env
```

and update:

```env
DB_PASSWORD=YOUR_PASSWORD
```

---

## `Can't connect to MySQL server`

MySQL is not running.

### Windows

Open:

```text
Services
```

and start the MySQL service.

### macOS with Homebrew

```bash
brew services start mysql
```

---

## `Database connected successfully!` does not appear

Check:

1. MySQL is running.
2. `road_monitoring` exists.
3. `backend/.env` exists.
4. Your password is correct.
5. The virtual environment is active.

---

## Dashboard says `API unavailable`

Start:

```bash
cd backend
python -m uvicorn main:app --reload
```

Keep that terminal open.

---

## Dashboard numbers do not update

The dashboard polls every 5 seconds.

Check:

```text
http://127.0.0.1:8000/statistics
```

If the API shows the new value but the dashboard doesn't, refresh the browser.

---

## Ollama model fails to load / CUDA memory error

If a larger model such as `llama3.1` fails with an error similar to:

```text
failed to allocate CUDA_Host buffer
```

use the lighter model:

```bash
ollama pull llama3.2:1b
```

and set:

```env
OLLAMA_MODEL=llama3.2:1b
```

Restart the API afterward.

The project does not require a large model to perform its database-grounded summarization.

---

## Daily report says no potholes today

The daily query uses:

```sql
DATE(timestamp) = CURDATE()
```

The included `schema.sql` uses `NOW()` for its sample rows.

If you are testing on a different day, re-run the schema:

```text
database/schema.sql
```

This recreates the six sample rows with the current date.

**Warning:** running `schema.sql` drops and recreates the `potholes` table, so do not run it if you need to preserve real detections.

---

# 9. Recommended demo sequence

For a final presentation, use this flow:

### 1. Show the pipeline

```text
Camera → OpenCV → YOLO → Risk → MySQL → Dashboard → GenAI → Human Decision
```

### 2. Show live dashboard

Point out:

- Total detections
- High-risk incidents
- Route condition
- Inspection priority

### 3. Ask the AI

> How many high-risk potholes were detected?

### 4. Compare routes

> Which route has the most dangerous potholes?

### 5. Generate the report

> Summarize today's inspection.

### 6. Explain priorities

> Which incidents should be inspected first?

### 7. Simulate a new YOLO detection

Run:

```bash
python yolo_integration.py
```

### 8. Show the dashboard changing

The new incident appears automatically.

### 9. Ask the AI again

The answer should now use the updated database value.

This demonstrates the complete integration rather than a static chatbot.

---

# 10. Design / architecture principle

The most important architectural decision is:

```text
                  DATABASE
                 /        \
                /          \
        Dashboard          GenAI
                              ↓
                         LLM wording
```

The LLM should **not** be the source of truth.

For example, inspection priority is calculated from the stored severity score:

```text
Database:
Incident 17 → severity 0.92
Incident 31 → severity 0.87
Incident 12 → severity 0.81

             ↓

GenAI explains:

"Incident 17 should be inspected first because
it has the highest severity score."
```

This makes the system more reliable, explainable and suitable for a road-monitoring demonstration.

---

## Final system

```text
┌──────────────────────┐
│    Camera / Video    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│       OpenCV         │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│        YOLO          │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│   Risk Estimation    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│       MySQL          │
└───────┬────────┬─────┘
        ↓        ↓
┌────────────┐ ┌───────────────┐
│ Dashboard  │ │  GenAI Layer  │
└─────┬──────┘ └───────┬───────┘
      │                ↓
      │          Natural Language
      │             Reports
      │                ↓
      └──────────→ Human Decision
```

**RoadWatch turns raw road detections into actionable inspection decisions.**
