import sys
from pathlib import Path
from datetime import datetime

import requests


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# FASTAPI SERVER
# =========================================================

API_URL = "http://127.0.0.1:8000"


# =========================================================
# REPORT DIRECTORY
# =========================================================

REPORT_DIR = PROJECT_ROOT / "reports" / "generated"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# GET INCIDENTS
# =========================================================

def get_incidents():
    """
    Get all incidents from the RoadGuard FastAPI backend.
    """

    response = requests.get(
        f"{API_URL}/incidents",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# GET STATISTICS
# =========================================================

def get_statistics():
    """
    Get overall RoadGuard statistics.
    """

    response = requests.get(
        f"{API_URL}/statistics",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# GET RISK DISTRIBUTION
# =========================================================

def get_risk_distribution():
    """
    Get risk distribution from the RoadGuard API.
    """

    response = requests.get(
        f"{API_URL}/risk-distribution",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# EXTRACT RISK COUNTS
# =========================================================

def extract_risk_counts(risk_distribution):

    low = 0
    medium = 0
    high = 0

    # -----------------------------------------------------
    # FORMAT 1
    #
    # {
    #     "Low": 2,
    #     "Medium": 3,
    #     "High": 1
    # }
    # -----------------------------------------------------

    if isinstance(risk_distribution, dict):

        for level, count in risk_distribution.items():

            level = str(level).lower()

            if level == "low":
                low = count

            elif level == "medium":
                medium = count

            elif level == "high":
                high = count

    # -----------------------------------------------------
    # FORMAT 2
    #
    # [
    #     {
    #         "risk_level": "Low",
    #         "count": 2
    #     }
    # ]
    # -----------------------------------------------------

    elif isinstance(risk_distribution, list):

        for item in risk_distribution:

            if not isinstance(item, dict):
                continue

            level = str(
                item.get("risk_level", "")
            ).lower()

            count = item.get(
                "count",
                0
            )

            if level == "low":
                low = count

            elif level == "medium":
                medium = count

            elif level == "high":
                high = count

    return low, medium, high


# =========================================================
# CREATE REPORT
# =========================================================

def create_report():

    print()
    print("==========================================")
    print("       ROADGUARD AI REPORT GENERATOR")
    print("==========================================")

    # -----------------------------------------------------
    # FETCH DATA
    # -----------------------------------------------------

    print()
    print("Fetching incident data...")

    incidents = get_incidents()

    print("Fetching statistics...")

    statistics = get_statistics()

    print("Fetching risk distribution...")

    risk_distribution = get_risk_distribution()

    # -----------------------------------------------------
    # SAFETY CHECK
    # -----------------------------------------------------

    if not isinstance(incidents, list):

        print()
        print("WARNING:")
        print("Unexpected incident data format.")

        incidents = []

    # -----------------------------------------------------
    # CURRENT TIME
    # -----------------------------------------------------

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # -----------------------------------------------------
    # TOTAL INCIDENTS
    # -----------------------------------------------------

    if isinstance(statistics, dict):

        total_incidents = statistics.get(
            "total_incidents",
            len(incidents)
        )

    else:

        total_incidents = len(incidents)

    # -----------------------------------------------------
    # RISK COUNTS
    # -----------------------------------------------------

    low, medium, high = extract_risk_counts(
        risk_distribution
    )

    # -----------------------------------------------------
    # AVERAGE CONFIDENCE
    # -----------------------------------------------------

    confidence_values = []

    for incident in incidents:

        if not isinstance(incident, dict):
            continue

        confidence = incident.get(
            "confidence"
        )

        try:

            if confidence is not None:

                confidence_values.append(
                    float(confidence)
                )

        except (
            ValueError,
            TypeError
        ):

            pass

    if confidence_values:

        average_confidence = (
            sum(confidence_values)
            / len(confidence_values)
        )

    else:

        average_confidence = 0.0

    # =====================================================
    # REPORT HEADER
    # =====================================================

    report = f"""# RoadGuard AI — Road Inspection Report

## 1. Report Information

**Generated:** {generated_at}

**System:** RoadGuard AI

**Detection Object:** Pothole

---

## 2. Inspection Summary

RoadGuard AI detected a total of **{total_incidents}**
recorded incident(s) in the available inspection data.

The system uses a YOLO-based computer vision model to
detect potholes and a visual risk engine to estimate
the risk level of each detection.

---

## 3. Detection Statistics

| Metric | Value |
|---|---:|
| Total Incidents | {total_incidents} |
| Average Detection Confidence | {average_confidence:.2%} |
| Low Risk Incidents | {low} |
| Medium Risk Incidents | {medium} |
| High Risk Incidents | {high} |

---

## 4. Risk Distribution

### Low Risk

{low} incident(s) were classified as low visual risk.

### Medium Risk

{medium} incident(s) were classified as medium visual risk.

### High Risk

{high} incident(s) were classified as high visual risk.

> **Note:** Risk levels represent AI-estimated visual
> risk based on available image characteristics.
> They do not represent physical pothole depth
> measurements.

---

## 5. Incident Details

"""

    # =====================================================
    # INCIDENT TABLE
    # =====================================================

    if incidents:

        report += """| Incident ID | Timestamp | Confidence | Risk Score | Risk Level |
|---|---|---:|---:|---|
"""

        for incident in incidents:

            if not isinstance(incident, dict):
                continue

            incident_id = incident.get(
                "incident_id",
                "N/A"
            )

            timestamp = incident.get(
                "timestamp",
                "N/A"
            )

            confidence = incident.get(
                "confidence",
                0
            )

            risk_score = incident.get(
                "risk_score",
                0
            )

            risk_level = incident.get(
                "risk_level",
                "N/A"
            )

            # ---------------------------------------------
            # FORMAT CONFIDENCE
            # ---------------------------------------------

            try:

                confidence_text = (
                    f"{float(confidence):.2%}"
                )

            except (
                ValueError,
                TypeError
            ):

                confidence_text = str(
                    confidence
                )

            # ---------------------------------------------
            # FORMAT RISK SCORE
            # ---------------------------------------------

            try:

                risk_score_text = (
                    f"{float(risk_score):.2f}"
                )

            except (
                ValueError,
                TypeError
            ):

                risk_score_text = str(
                    risk_score
                )

            report += (
                f"| {incident_id} "
                f"| {timestamp} "
                f"| {confidence_text} "
                f"| {risk_score_text} "
                f"| {risk_level} |\n"
            )

    else:

        report += (
            "No incidents are currently available "
            "in the database.\n"
        )

    # =====================================================
    # CONCLUSION
    # =====================================================

    report += f"""

---

## 6. Conclusion

The RoadGuard AI inspection system currently contains
**{total_incidents} recorded incident(s)**.

The statistics in this report are generated from the
actual incident records available through the RoadGuard
AI backend.

The report can be used to support road inspection,
monitoring and prioritization activities.

---

## 7. System Information

**Computer Vision:** YOLO-based pothole detection

**Image Processing:** OpenCV

**Risk Assessment:** RoadGuard visual risk engine

**Backend:** FastAPI

**Database:** SQLite

**GenAI:** Local LLM

---

*Report automatically generated by RoadGuard AI.*
"""

    # =====================================================
    # SAVE REPORT
    # =====================================================

    filename = (
        "RoadGuard_Report_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".md"
    )

    output_path = REPORT_DIR / filename

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report)

    # =====================================================
    # SUCCESS MESSAGE
    # =====================================================

    print()
    print("==========================================")
    print("REPORT GENERATED SUCCESSFULLY")
    print("==========================================")

    print()
    print("Report location:")
    print(output_path)

    return output_path


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    try:

        create_report()

    except requests.exceptions.ConnectionError:

        print()
        print("ERROR:")
        print("FastAPI server is not running.")

        print()
        print("Start FastAPI using:")

        print(
            "python -m uvicorn backend.api:app --reload"
        )

    except requests.exceptions.HTTPError as error:

        print()
        print("ERROR:")
        print("FastAPI returned an HTTP error.")

        print(error)

    except Exception as error:

        print()
        print("ERROR GENERATING REPORT:")

        print(error)