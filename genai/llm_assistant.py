"""
RoadGuard AI - Local LLM Assistant

Uses Ollama to generate natural-language responses
from actual RoadGuard inspection data.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import ollama

from genai.data_context import build_context


MODEL_NAME = "llama3.2:3b"


def build_roadguard_context(context):
    """
    Convert actual RoadGuard data into a text context
    that can be given to the LLM.
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

    incidents = context.get(
        "incidents",
        []
    )

    context_text = f"""
ROADGUARD AI INSPECTION DATA

Total incidents:
{total}

Risk distribution:
HIGH: {high}
MEDIUM: {medium}
LOW: {low}

Individual incidents:
"""

    for incident in incidents:

        incident_id = incident.get(
            "incident_id",
            "Unknown"
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
            "Unknown"
        )

        object_type = incident.get(
            "object_type",
            "Unknown"
        )

        context_text += f"""
Incident ID: {incident_id}
Object: {object_type}
Detection confidence: {confidence * 100:.2f}%
Visual risk score: {risk_score}
Visual risk level: {risk_level}
"""

    return context_text


def ask_llm(question, context):
    """
    Send a grounded RoadGuard question to the local LLM.
    """

    roadguard_context = build_roadguard_context(
        context
    )

    system_prompt = """
You are RoadGuard AI, an intelligent road inspection assistant.

Your job is to explain and summarize road inspection
information using ONLY the RoadGuard data provided
in the context.

Important rules:

1. Never invent incident counts.
2. Never invent risk levels.
3. Never invent GPS coordinates.
4. Never invent road locations.
5. Never claim physical pothole depth was measured.
6. Risk levels are VISUAL RISK estimates.
7. If the requested information is not present
   in the context, clearly say that the information
   is not available.
8. Give concise but useful answers.
9. Use simple language suitable for road authorities
   and non-technical users.
"""

    user_prompt = f"""
ROADGUARD DATA:
{roadguard_context}

USER QUESTION:
{question}

Answer the user's question using the RoadGuard data above.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response["message"]["content"]


def main():

    print()
    print("==============================================")
    print("       ROADGUARD AI - LOCAL LLM")
    print("==============================================")

    print()
    print("Loading RoadGuard data...")

    try:

        context = build_context()

    except Exception as error:

        print()
        print("ERROR: Could not load RoadGuard data.")
        print(error)
        return

    print("RoadGuard data loaded successfully.")

    print()
    print("Model:", MODEL_NAME)

    print()
    print("Ask a question about the road inspection.")
    print("Type 'exit' to stop.")

    print()

    while True:

        question = input("You: ").strip()

        if question.lower() == "exit":

            print()
            print("RoadGuard AI stopped.")
            break

        if question == "":
            continue

        try:

            answer = ask_llm(
                question,
                context
            )

            print()
            print("RoadGuard AI:")
            print(answer)
            print()

        except Exception as error:

            print()
            print("ERROR: LLM request failed.")
            print(error)
            print()


if __name__ == "__main__":
    main()