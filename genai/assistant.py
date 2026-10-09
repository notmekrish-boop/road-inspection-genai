"""
RoadGuard AI - Grounded GenAI Assistant

This module answers natural-language questions
using actual RoadGuard incident data.

The first implementation uses deterministic
grounded responses so that the system never
invents statistics.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from genai.data_context import build_context


def percentage(part, total):
    """
    Calculate percentage safely.
    """

    if total == 0:
        return 0

    return round((part / total) * 100, 2)


def generate_summary(context):
    """
    Generate a natural-language inspection summary
    using only actual RoadGuard data.
    """

    statistics = context["statistics"]

    total = statistics.get(
        "total_incidents",
        0
    )

    distribution = statistics.get(
        "risk_distribution",
        {}
    )

    low = distribution.get("LOW", 0)
    medium = distribution.get("MEDIUM", 0)
    high = distribution.get("HIGH", 0)

    if total == 0:

        return (
            "No road incidents have been detected yet. "
            "The RoadGuard database currently contains "
            "no inspection incidents."
        )

    high_percentage = percentage(
        high,
        total
    )

    medium_percentage = percentage(
        medium,
        total
    )

    low_percentage = percentage(
        low,
        total
    )

    summary = (
        f"RoadGuard AI has detected {total} road incidents. "
        f"{high} ({high_percentage}%) are classified as "
        f"HIGH visual risk, "
        f"{medium} ({medium_percentage}%) as MEDIUM visual risk, "
        f"and {low} ({low_percentage}%) as LOW visual risk. "
    )

    if high > 0:

        summary += (
            "High-risk incidents should be prioritized "
            "for human verification and road maintenance."
        )

    else:

        summary += (
            "No high-risk incidents are currently present "
            "in the database."
        )

    return summary


def answer_question(question, context):
    """
    Answer a natural-language question using
    actual RoadGuard data.
    """

    question = question.lower().strip()

    statistics = context["statistics"]

    total = statistics.get(
        "total_incidents",
        0
    )

    distribution = statistics.get(
        "risk_distribution",
        {}
    )

    low = distribution.get("LOW", 0)
    medium = distribution.get("MEDIUM", 0)
    high = distribution.get("HIGH", 0)

    # ---------------------------------------
    # Total incident questions
    # ---------------------------------------

    if (
        "how many" in question
        and (
            "incident" in question
            or "pothole" in question
        )
    ):

        return (
            f"RoadGuard AI has detected "
            f"{total} road incident(s)."
        )

    # ---------------------------------------
    # High-risk questions
    # ---------------------------------------

    if (
        "high risk" in question
        or "high-risk" in question
    ):

        return (
            f"There are {high} high-risk incidents "
            f"currently stored in the RoadGuard database."
        )

    # ---------------------------------------
    # Medium-risk questions
    # ---------------------------------------

    if (
        "medium risk" in question
        or "medium-risk" in question
    ):

        return (
            f"There are {medium} medium-risk incidents "
            f"currently stored in the RoadGuard database."
        )

    # ---------------------------------------
    # Low-risk questions
    # ---------------------------------------

    if (
        "low risk" in question
        or "low-risk" in question
    ):

        return (
            f"There are {low} low-risk incidents "
            f"currently stored in the RoadGuard database."
        )

    # ---------------------------------------
    # Risk distribution
    # ---------------------------------------

    if (
        "distribution" in question
        or "breakdown" in question
        or "categories" in question
    ):

        return (
            f"Risk distribution: "
            f"HIGH = {high}, "
            f"MEDIUM = {medium}, "
            f"LOW = {low}."
        )

    # ---------------------------------------
    # Priority questions
    # ---------------------------------------

    if (
        "priority" in question
        or "attention" in question
        or "urgent" in question
    ):

        if high > 0:

            return (
                f"High-risk incidents should receive "
                f"the highest priority. "
                f"There are currently {high} high-risk "
                f"incidents."
            )

        if medium > 0:

            return (
                "There are no high-risk incidents. "
                f"The next priority category is MEDIUM "
                f"with {medium} incident(s)."
            )

        return (
            "There are currently no medium- or high-risk "
            "incidents requiring priority attention."
        )

    # ---------------------------------------
    # Summary
    # ---------------------------------------

    if (
        "summary" in question
        or "report" in question
        or "overview" in question
    ):

        return generate_summary(context)

    # ---------------------------------------
    # Help
    # ---------------------------------------

    if (
        "help" in question
        or question == ""
    ):

        return (
            "You can ask questions such as:\n"
            "- How many potholes were detected?\n"
            "- How many high-risk incidents are there?\n"
            "- Show the risk distribution.\n"
            "- Which incidents need priority attention?\n"
            "- Give me a road inspection summary."
        )

    # ---------------------------------------
    # Unknown question
    # ---------------------------------------

    return (
        "I could not answer that question using "
        "the currently available RoadGuard data. "
        "Try asking about incidents, risk levels, "
        "risk distribution, priority, or a summary."
    )


def main():

    print()
    print("==============================================")
    print("        ROADGUARD AI GENAI ASSISTANT")
    print("==============================================")

    try:

        context = build_context()

    except Exception as error:

        print()
        print("ERROR: Could not retrieve RoadGuard data.")
        print(error)
        return

    print()
    print("RoadGuard data loaded successfully.")

    print()
    print("Type your question.")
    print("Type 'exit' to stop.")
    print()

    while True:

        question = input("You: ")

        if question.lower().strip() == "exit":

            print()
            print("RoadGuard AI Assistant stopped.")
            break

        answer = answer_question(
            question,
            context
        )

        print()
        print("RoadGuard AI:", answer)
        print()


if __name__ == "__main__":
    main()