# RoadGuard AI 🚧

### AI-powered pothole detection, visual risk assessment, and road-inspection intelligence

RoadGuard AI is a computer-vision road-inspection prototype that detects
potholes in images, estimates their **visual risk**, records incidents
in a local SQLite database, and presents inspection data through a
Streamlit dashboard and a GenAI assistant powered by Ollama.

> **Important:** Risk scores are visual estimates derived from detector
> confidence, bounding-box size, and position in the image. They are not
> measurements of pothole depth, structural integrity, or definitive
> road safety.

------------------------------------------------------------------------

## Contents

-   [Features](#features)
-   [System architecture](#system-architecture)
-   [Technology stack](#technology-stack)
-   [Project structure](#project-structure)
-   [Prerequisites](#prerequisites)
-   [Setup](#setup)
-   [Run the application](#run-the-application)
-   [Use the dashboard](#use-the-dashboard)
-   [API endpoints](#api-endpoints)
-   [Risk estimation](#risk-estimation)
-   [Tests and utilities](#tests-and-utilities)
-   [Troubleshooting](#troubleshooting)
-   [Limitations and responsible use](#limitations-and-responsible-use)

------------------------------------------------------------------------

## Features

-   **Pothole detection:** Uses an Ultralytics YOLO model to identify
    potholes in images.
-   **Image processing:** Uses OpenCV to load images and work with
    detections.
-   **Visual risk estimation:** Produces a score from 0--100 and
    classifies detections as `LOW`, `MEDIUM`, or `HIGH`.
-   **Incident records:** Stores detection metadata in a local SQLite
    database, including confidence, bounding box, risk score, timestamp,
    source, and optional coordinates.
-   **REST API:** FastAPI endpoints expose incident records, counts,
    risk distribution, and health status.
-   **Dashboard:** Streamlit displays inspection statistics and
    incidents, and supports image-based inference.
-   **GenAI assistant:** Uses a local Ollama model to answer questions
    and summarize the available inspection data.
-   **Offline-friendly inference:** Once required Python packages and
    model files are available locally, detection can run without sending
    images to a cloud AI service. Ollama must be running for local LLM
    responses.

## System architecture

``` text
Image / Video
     |
     v
OpenCV + YOLO
     |
     v
Pothole detections
     |
     v
Visual Risk Engine
     |
     v
Incident Manager
     |
     v
SQLite database
   /        \
  v          v
FastAPI    Streamlit dashboard
  \          /
   v        v
GenAI assistant (Ollama)
          |
          v
Human review and inspection decisions
```

The API and dashboard are separate processes. The dashboard reads
statistics and incidents from the API and also uses the project's Python
modules for image inference and GenAI features.

## Technology stack

  Component          Technology
  ------------------ ------------------
  Language           Python
  Object detection   Ultralytics YOLO
  Image processing   OpenCV
  Risk estimation    Python
  Database           SQLite
  API                FastAPI, Uvicorn
  Dashboard          Streamlit
  Data handling      Pandas
  Local LLM          Ollama
  Image display      Pillow

------------------------------------------------------------------------

## Project structure

``` text
RoadGuardAI/
├── backend/
│   ├── api.py                 # FastAPI application
│   └── init_db.py             # Database setup helper
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── data/
│   └── roadguard.db           # SQLite database (created/used locally)
├── database/
│   ├── db.py                  # Database operations and schema
│   └── view_database.py       # Database inspection utility
├── dataset/
│   ├── data.yaml              # YOLO dataset configuration
│   └── ...                    # Dataset inspection/validation utilities
├── detection/
│   ├── inference.py           # Reusable image inference
│   ├── detect_image.py        # Image detection runner
│   ├── detect_video.py        # Video detection runner
│   ├── train.py               # Model training
│   └── ...                    # Validation and visualization utilities
├── genai/
│   ├── data_context.py        # Builds context from database data
│   ├── llm_assistant.py       # Ollama-based assistant
│   ├── assistant.py           # Assistant/query logic
│   ├── summary.py             # Inspection summaries
│   └── report_generator.py    # Report generation
├── incident/
│   └── incident_manager.py    # Standard incident representation
├── models/
│   └── pothole_best.pt        # Project model weights, if included
├── risk_engine/
│   └── risk.py                # Visual risk scoring
├── tests/
│   └── test_risk.py           # Risk-engine smoke test
├── main.py                    # Check this file for project entry-point notes
├── requirements.txt           # Add/install dependencies as described below
├── yolo11n.pt                 # YOLO base weights, if included
└── README.md
```

The exact contents can vary by project version. Keep generated files,
private data, virtual environments, and secrets out of version control.

------------------------------------------------------------------------

## Prerequisites

-   Python 3.10 or newer recommended.
-   Windows, macOS, or Linux.
-   Internet access for initial package/model downloads.
-   Ollama installed if you want LLM-generated answers.
-   A compatible image/video file for detection.
-   Enough RAM and disk space for Python dependencies and YOLO weights.
    A GPU is optional; CPU inference may be slower.

Install Ollama from **https://ollama.com**.

### Local LLM

The current assistant configuration in `genai/llm_assistant.py` uses:

``` python
MODEL_NAME = "llama3.2:3b"
```

Download that model before using the LLM features:

``` bash
ollama pull llama3.2:3b
```

Check the installed model:

``` bash
ollama list
```

If your computer runs out of memory, use a smaller model and change
`MODEL_NAME` in `genai/llm_assistant.py` to match the model you
downloaded, for example `llama3.2:1b`.

------------------------------------------------------------------------

## Setup

### 1. Extract and open the project

Extract `RoadGuardAI.zip`, then open a terminal in the folder containing
`backend/`, `dashboard/`, `database/`, `detection/`, and `genai/`.

### 2. Create a virtual environment

**Windows PowerShell:**

``` powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt:

``` cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

The provided `requirements.txt` may be empty in this project snapshot.
Until it is populated, install the runtime packages explicitly:

``` bash
python -m pip install --upgrade pip
python -m pip install ultralytics opencv-python fastapi "uvicorn[standard]" streamlit requests pandas pillow ollama
```

If an import error identifies another third-party dependency, install it
in the activated virtual environment and add it to `requirements.txt` so
other contributors can reproduce the setup.

To create a dependency list after verifying the environment, use a
curated `requirements.txt` rather than blindly freezing every package
from your machine.

### 4. Verify the database

The project uses SQLite; **MySQL is not required**.

The database module stores the database at:

``` text
data/roadguard.db
```

The database helper creates the `incidents` table when
`initialize_database()` is called. The API initializes the database on
startup.

You can initialize it directly from the project root:

``` bash
python -c "from database.db import initialize_database; initialize_database(); print('Database initialized')"
```

### 5. Verify the model path

Before running image detection, open `detection/inference.py` and check
`MODEL_PATH`.

In the supplied source, the model path is configured as an absolute
Windows path. That path will not work on another computer. Update it to
point to the model included with the project, for example:

``` python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = str(PROJECT_ROOT / "models" / "pothole_best.pt")
```

Use the model file that actually exists in your extracted project. If
`models/pothole_best.pt` is absent, provide a compatible trained pothole
model before running inference.

------------------------------------------------------------------------

## Run the application

Run each service in a **separate terminal**. Activate `.venv` in each
terminal.

### Terminal 1 --- Start the FastAPI backend

From the project root:

``` bash
python -m uvicorn backend.api:app --reload
```

The API should be available at:

-   API root: http://127.0.0.1:8000/
-   Health check: http://127.0.0.1:8000/health
-   Interactive API docs: http://127.0.0.1:8000/docs

Leave this terminal running.

### Terminal 2 --- Start the Streamlit dashboard

From the project root:

``` bash
python -m streamlit run dashboard/app.py
```

Streamlit prints a local URL, usually:

http://localhost:8501

Open that URL in your browser. The dashboard calls the API at
`http://127.0.0.1:8000`, so the API should be running first.

### Terminal 3 --- Start Ollama (if required)

Ollama usually runs as a background service after installation. If it is
not running, start the Ollama application/service, then test:

``` bash
ollama run llama3.2:3b
```

Once the model responds, exit its interactive session with `/bye`. The
dashboard's GenAI feature can then call the local model.

------------------------------------------------------------------------

## Use the dashboard

1.  Start the API and dashboard using the commands above.
2.  Open the Streamlit URL shown in the terminal.
3.  Review incident counts and risk distribution.
4.  Use the image-upload/inference controls in the dashboard to analyze
    an image.
5.  Ask the assistant questions about the incidents available in the
    database.
6.  Review generated summaries and reports, then verify high-priority
    detections manually.

Example questions:

-   "How many incidents are in the database?"
-   "How many high-risk incidents are recorded?"
-   "Show the risk distribution."
-   "Which incidents need priority attention?"
-   "Give me a road inspection summary."

Answers are constrained by the data available to the assistant. If the
database does not contain route names or GPS coordinates, the assistant
cannot reliably compare routes or report locations.

------------------------------------------------------------------------

## API endpoints

The FastAPI application currently exposes these endpoints:

  ----------------------------------------------------------------------------
  Method                  Endpoint                     Description
  ----------------------- ---------------------------- -----------------------
  `GET`                   `/`                          API name, status, and
                                                       version

  `GET`                   `/health`                    API/database health and
                                                       incident count

  `GET`                   `/incidents`                 Retrieve incident
                                                       records

  `GET`                   `/incidents/{incident_id}`   Retrieve one incident
                                                       by ID

  `GET`                   `/statistics`                Total incident count
                                                       and risk distribution

  `GET`                   `/risk-distribution`         Counts for `LOW`,
                                                       `MEDIUM`, and `HIGH`
  ----------------------------------------------------------------------------

Example:

``` bash
curl http://127.0.0.1:8000/health
```

On Windows, you can also open the endpoint in your browser or use the
interactive `/docs` page.

------------------------------------------------------------------------

## Risk estimation

The risk engine combines three visual factors:

  Factor                             Maximum contribution
  -------------------------------- ----------------------
  Detector confidence                           50 points
  Relative bounding-box area                    30 points
  Vertical position in the image                20 points
  **Total**                                **100 points**

The current classification thresholds are:

  Score            Classification
  ---------------- ----------------
  Below 40         `LOW`
  40 to below 70   `MEDIUM`
  70 and above     `HIGH`

These thresholds and weights are heuristic choices for this prototype.
They should be calibrated against labelled real-world inspection data
before operational use. A bounding box is not a physical depth
measurement.

------------------------------------------------------------------------

## Tests and utilities

### Run the risk-engine smoke test

From the project root:

``` bash
python tests/test_risk.py
```

It prints the calculated score and risk level for an example bounding
box.

### Other useful scripts

Run scripts from the project root unless the script's own instructions
say otherwise:

-   `detection/detect_image.py` --- image detection runner
-   `detection/detect_video.py` --- video detection runner
-   `detection/validate_model.py` --- model validation
-   `detection/visualize_labels.py` --- dataset label visualization
-   `dataset/validate_dataset.py` --- dataset validation
-   `database/view_database.py` --- inspect stored incidents
-   `genai/test_assistant.py` --- assistant testing

Check each script's arguments and configuration before running it; some
scripts may expect specific file paths or model locations.

------------------------------------------------------------------------

## Troubleshooting

### `ModuleNotFoundError`

Make sure the virtual environment is active and install the missing
package into it:

``` bash
python -m pip install PACKAGE_NAME
```

### API returns an error or the dashboard cannot connect

-   Start the API first: `python -m uvicorn backend.api:app --reload`
-   Confirm `http://127.0.0.1:8000/health` opens.
-   Keep the API terminal running.
-   Check whether another application is using port `8000`.

### YOLO cannot find the model

Open `detection/inference.py` and correct `MODEL_PATH`. Prefer a path
built from `Path(__file__)` instead of a user-specific absolute path.

### Ollama connection or model error

-   Start the Ollama application/service.
-   Run `ollama list` to confirm the model is installed.
-   Ensure `MODEL_NAME` in `genai/llm_assistant.py` exactly matches the
    installed model.
-   If memory is limited, try `llama3.2:1b`.

### No incidents appear

The database may be empty. Start the API to initialize the schema, then
run image inference from the dashboard or a detection script. Check the
database with `python database/view_database.py`.

### PowerShell does not activate the virtual environment

Use Command Prompt and run:

``` cmd
.venv\Scripts\activate.bat
```

------------------------------------------------------------------------

## Limitations and responsible use

-   Risk values represent **visual estimates**, not verified physical
    measurements.
-   Model quality depends on the training data, camera angle, lighting,
    resolution, and inference threshold.
-   The sample project does not establish that every detection is a real
    pothole; false positives and missed detections are possible.
-   GPS coordinates are optional and are not inferred from an image.
-   Generated summaries should be reviewed by a person and should not be
    treated as automatic road-maintenance orders.
-   Before public deployment, validate the model, risk thresholds,
    privacy/security controls, API access, and data-retention policy.

## Contributing

1.  Create a branch for your change.
2.  Keep secrets, virtual environments, local databases, datasets, and
    generated training artifacts out of commits unless they are
    intentionally needed.
3.  Test changes before opening a pull request.
4.  Document new dependencies, configuration values, and run commands.

## License

No license is specified in this project snapshot. Add a `LICENSE` file
before publishing the repository for reuse by others.
