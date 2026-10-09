"""
RoadGuard AI - SQLite Database Manager

This module:
1. Creates the RoadGuard SQLite database
2. Creates the incidents table
3. Inserts incidents
4. Retrieves incidents
5. Provides basic database statistics
"""

import sys
from pathlib import Path
import sqlite3


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# DATABASE PATH
# ============================================================

DATABASE_DIR = PROJECT_ROOT / "data"

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_PATH = DATABASE_DIR / "roadguard.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a connection to the RoadGuard database.
    """

    connection = sqlite3.connect(
        str(DATABASE_PATH)
    )

    # Allows rows to behave like dictionaries
    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# CREATE TABLE
# ============================================================

def initialize_database():
    """
    Create the incidents table if it does not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (

            incident_id TEXT PRIMARY KEY,

            timestamp TEXT NOT NULL,

            object_type TEXT NOT NULL,

            confidence REAL NOT NULL,

            x1 REAL NOT NULL,
            y1 REAL NOT NULL,
            x2 REAL NOT NULL,
            y2 REAL NOT NULL,

            risk_score REAL NOT NULL,

            risk_level TEXT NOT NULL,

            image_path TEXT,

            latitude REAL,

            longitude REAL,

            source TEXT NOT NULL

        )
        """
    )

    connection.commit()

    connection.close()


# ============================================================
# INSERT INCIDENT
# ============================================================

def insert_incident(incident):
    """
    Insert a RoadGuard Incident object into SQLite.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO incidents (
            incident_id,
            timestamp,
            object_type,
            confidence,
            x1,
            y1,
            x2,
            y2,
            risk_score,
            risk_level,
            image_path,
            latitude,
            longitude,
            source
        )

        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """,
        (
            incident.incident_id,
            incident.timestamp,
            incident.object_type,
            incident.confidence,

            incident.x1,
            incident.y1,
            incident.x2,
            incident.y2,

            incident.risk_score,
            incident.risk_level,

            incident.image_path,

            incident.latitude,
            incident.longitude,

            incident.source
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# GET ALL INCIDENTS
# ============================================================

def get_all_incidents():
    """
    Return all stored incidents.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM incidents
        ORDER BY timestamp DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows

def get_incident_by_id(incident_id):
    """
    Return one incident using its incident ID.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM incidents
        WHERE incident_id = ?
        """,
        (incident_id,)
    )

    row = cursor.fetchone()

    connection.close()

    return row
# ============================================================
# GET INCIDENT COUNT
# ============================================================

def get_incident_count():
    """
    Return total number of incidents.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM incidents
        """
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ============================================================
# GET RISK DISTRIBUTION
# ============================================================

def get_risk_distribution():
    """
    Return the number of LOW, MEDIUM and HIGH incidents.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            risk_level,
            COUNT(*) AS count
        FROM incidents
        GROUP BY risk_level
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# TEST DATABASE
# ============================================================

if __name__ == "__main__":

    print()
    print("==============================================")
    print("       ROADGUARD DATABASE INITIALIZATION")
    print("==============================================")

    initialize_database()

    print()
    print("Database initialized successfully.")

    print()
    print("Database location:")
    print(DATABASE_PATH)

    print()
    print("Current incident count:")
    print(get_incident_count())

    print()
    print("==============================================")