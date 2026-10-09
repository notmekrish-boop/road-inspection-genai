"""
RoadGuard AI - FastAPI Backend

This API provides access to RoadGuard incident data
stored in the SQLite database.
"""

import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database.db import (
    initialize_database,
    get_all_incidents,
    get_incident_by_id,
    get_incident_count,
    get_risk_distribution,
)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="RoadGuard AI API",
    description=(
        "Backend API for the RoadGuard AI "
        "road inspection and pothole detection system."
    ),
    version="1.0.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():
    """
    Initialize the database when the API starts.
    """

    initialize_database()


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    """
    Basic API information.
    """

    return {
        "project": "RoadGuard AI",
        "status": "running",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health_check():
    """
    Check whether the API and database are available.
    """

    try:

        count = get_incident_count()

        return {
            "status": "healthy",
            "database": "connected",
            "incident_count": count
        }

    except Exception as error:

        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(error)
        }


# ============================================================
# GET ALL INCIDENTS
# ============================================================

@app.get("/incidents")
def get_incidents():

    rows = get_all_incidents()

    incidents = []

    for row in rows:

        incident = {}

        for key in row.keys():

            value = row[key]

            # Convert bytes to safe text
            if isinstance(value, bytes):

                value = value.decode(
                    "utf-8",
                    errors="replace"
                )

            incident[key] = value

        incidents.append(incident)

    return {
        "count": len(incidents),
        "incidents": incidents
    }

# ============================================================
# GET SINGLE INCIDENT
# ============================================================

@app.get("/incidents/{incident_id}")
def get_single_incident(incident_id: str):

    row = get_incident_by_id(
        incident_id
    )

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Incident not found."
        )

    incident = {}

    for key in row.keys():

        value = row[key]

        if isinstance(value, bytes):

            value = value.decode(
                "utf-8",
                errors="replace"
            )

        incident[key] = value

    return {
        "incident": incident
    }

# ============================================================
# GET STATISTICS
# ============================================================

@app.get("/statistics")
def get_statistics():
    """
    Return overall RoadGuard statistics.
    """

    total_incidents = get_incident_count()

    distribution_rows = get_risk_distribution()

    distribution = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0
    }

    for row in distribution_rows:

        level = row["risk_level"]

        if level in distribution:
            distribution[level] = row["count"]

    return {
        "total_incidents": total_incidents,

        "risk_distribution": distribution
    }


# ============================================================
# GET RISK DISTRIBUTION
# ============================================================

@app.get("/risk-distribution")
def risk_distribution():
    """
    Return LOW, MEDIUM and HIGH incident counts.
    """

    rows = get_risk_distribution()

    distribution = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0
    }

    for row in rows:

        level = row["risk_level"]

        if level in distribution:
            distribution[level] = row["count"]

    return distribution