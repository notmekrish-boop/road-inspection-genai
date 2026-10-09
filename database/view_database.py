import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from database.db import (
    get_all_incidents,
    get_incident_count,
    get_risk_distribution
)


def main():

    print()
    print("==============================================")
    print("          ROADGUARD DATABASE VIEWER")
    print("==============================================")

    # --------------------------------------------------------
    # Total incidents
    # --------------------------------------------------------

    total = get_incident_count()

    print()
    print("Total incidents:", total)

    # --------------------------------------------------------
    # Incident records
    # --------------------------------------------------------

    incidents = get_all_incidents()

    print()
    print("Stored incidents")
    print("----------------------------------------------")

    for incident in incidents:

        print()
        print("Incident ID :", incident["incident_id"])
        print("Timestamp   :", incident["timestamp"])
        print("Object      :", incident["object_type"])
        print(
            "Confidence  :",
            f'{incident["confidence"] * 100:.2f}%'
        )
        print(
            "Risk Score  :",
            incident["risk_score"]
        )
        print(
            "Risk Level  :",
            incident["risk_level"]
        )
        print(
            "Source      :",
            incident["source"]
        )

    # --------------------------------------------------------
    # Risk distribution
    # --------------------------------------------------------

    distribution = get_risk_distribution()

    print()
    print("Risk Distribution")
    print("----------------------------------------------")

    for row in distribution:

        print(
            f'{row["risk_level"]}: '
            f'{row["count"]}'
        )

    print()
    print("==============================================")


if __name__ == "__main__":
    main()