"""
RoadGuard AI - GenAI Data Context

This module collects actual RoadGuard data
from the FastAPI backend.
"""

import requests


API_URL = "http://127.0.0.1:8000"


def get_statistics():
    """
    Get RoadGuard statistics from FastAPI.
    """

    response = requests.get(
        f"{API_URL}/statistics",
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def get_incidents():
    """
    Get all RoadGuard incidents from FastAPI.
    """

    response = requests.get(
        f"{API_URL}/incidents",
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def build_context():
    """
    Build a structured context containing
    actual RoadGuard data.
    """

    statistics = get_statistics()
    incidents_data = get_incidents()

    incidents = incidents_data.get(
        "incidents",
        []
    )

    context = {
        "statistics": statistics,
        "incidents": incidents
    }

    return context


if __name__ == "__main__":

    print()
    print("======================================")
    print("   ROADGUARD GENAI DATA CONTEXT")
    print("======================================")

    context = build_context()

    print()
    print("Statistics:")
    print(context["statistics"])

    print()
    print("Number of incidents:")
    print(len(context["incidents"]))

    print()
    print("======================================")