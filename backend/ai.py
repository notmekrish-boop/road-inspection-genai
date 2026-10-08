"""GenAI layer.

Golden rule: the database produces the facts, the LLM only phrases them.
Every answer function first queries MySQL, then hands the real numbers to
the LLM. If Ollama is not running, a plain-text fallback is returned so the
API keeps working.
"""
import os

from dotenv import load_dotenv

import queries

load_dotenv()

MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

_llm = None


def get_llm():
    """Create the Ollama client lazily so importing this file never fails."""
    global _llm
    if _llm is None:
        from langchain_ollama import ChatOllama

        _llm = ChatOllama(model=MODEL_NAME, temperature=0)
    return _llm


def ask_llm(prompt, fallback):
    """Call the LLM; return `fallback` text if the model is unavailable."""
    try:
        return get_llm().invoke(prompt).content.strip()
    except Exception as exc:  # Ollama not running, model missing, etc.
        print(f"[ai] LLM unavailable ({exc}); using fallback answer")
        return fallback


SYSTEM_RULES = (
    "You are a road inspection assistant. Use ONLY the data provided. "
    "Never invent numbers, routes or incidents. Be concise."
)


# ---------------------------------------------------------------- summaries
def generate_summary(data, title="road inspection"):
    fallback = (
        f"{title.capitalize()}: {data['total']} potholes detected — "
        f"{data['high_risk']} high risk, {data['medium_risk']} medium, "
        f"{data['low_risk']} low."
    )
    prompt = f"""{SYSTEM_RULES}

Total potholes: {data['total']}
High risk: {data['high_risk']}
Medium risk: {data['medium_risk']}
Low risk: {data['low_risk']}

Write a concise {title} summary."""
    return ask_llm(prompt, fallback)


# ---------------------------------------------------------- the 5 questions
def answer_high_risk():
    count = queries.get_high_risk_count()
    fallback = f"{count} high-risk potholes were detected."
    prompt = f"""{SYSTEM_RULES}

Fact: {count} high-risk potholes were detected.
Answer the question: "How many high-risk potholes were detected?" """
    return ask_llm(prompt, fallback)


def answer_dangerous_route():
    routes = queries.get_route_summary()
    if not routes:
        return "No pothole data is available yet."
    top = routes[0]
    fallback = (
        f"{top['route']} has the most high-risk potholes ({top['high_risk']} "
        f"of {top['total']}) and should be prioritized for inspection."
    )
    table = "\n".join(
        f"- {r['route']}: total {r['total']}, high {r['high_risk']}, "
        f"medium {r['medium_risk']}, low {r['low_risk']}"
        for r in routes
    )
    prompt = f"""{SYSTEM_RULES}

Routes (already sorted, most dangerous first):
{table}

Which route has the most dangerous potholes? Answer in 1-2 sentences."""
    return ask_llm(prompt, fallback)


def answer_daily_summary():
    data = queries.get_daily_summary()
    if not data or not data["total"]:
        return "No potholes were detected today."
    return generate_summary(data, title="today's inspection")


def answer_priority():
    incidents = queries.get_priority_incidents(5)
    if not incidents:
        return "No incidents recorded yet."
    # Ranking comes from SQL; the LLM only explains it.
    table = "\n".join(
        f"{i+1}. Incident {r['id']} on {r['route']} — severity "
        f"{r['severity_score']}, confidence {r['confidence']}, "
        f"risk {r['risk_level']}"
        for i, r in enumerate(incidents)
    )
    fallback = "Inspect in this order:\n" + table
    prompt = f"""{SYSTEM_RULES}

Ranked incidents (do NOT change the order):
{table}

Which incidents should be inspected first? Explain the ranking briefly."""
    return ask_llm(prompt, fallback)


def answer_route_condition(route):
    data = queries.get_route_condition(route)
    if not data or not data["total"]:
        return f"No data found for {route}."
    fallback = (
        f"{route}: {data['total']} potholes — {data['high_risk']} high, "
        f"{data['medium_risk']} medium, {data['low_risk']} low."
    )
    prompt = f"""{SYSTEM_RULES}

Route: {route}
Total potholes: {data['total']}
High risk: {data['high_risk']}
Medium risk: {data['medium_risk']}
Low risk: {data['low_risk']}

Describe the road condition of {route} in 1-2 sentences."""
    return ask_llm(prompt, fallback)


# ------------------------------------------------------------------ routing
def answer_question(question):
    """Keyword router (Step 17). Reliable, no tool-calling support needed."""
    q = question.lower()

    for route in queries.get_known_routes():
        if route.lower() in q:
            return answer_route_condition(route)

    if any(w in q for w in ("inspected first", "priority", "prioritize", "first")):
        return answer_priority()
    if any(w in q for w in ("summar", "today", "report")):
        return answer_daily_summary()
    if "route" in q and any(w in q for w in ("dangerous", "worst", "most", "risk")):
        return answer_dangerous_route()
    if any(w in q for w in ("high-risk", "high risk", "how many")):
        return answer_high_risk()

    return (
        "I don't understand the question yet. Try: 'How many high-risk "
        "potholes were detected?', 'Which route is most dangerous?', "
        "'Summarize today's inspection', 'Which incidents should be "
        "inspected first?' or 'Show me the road condition of Route A.'"
    )


# ------------------------------------------------- LLM tool calling (Step 18)
def answer_with_tools(question):
    """LLM decides which DB tool to call, then writes the final answer.

    Falls back to the keyword router if the model/tool calling fails.
    """
    try:
        from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
        from langchain_core.tools import tool

        @tool
        def high_risk_count() -> int:
            """Number of high-risk potholes detected."""
            return queries.get_high_risk_count()

        @tool
        def route_summary() -> list:
            """Pothole counts per route, most dangerous route first."""
            return queries.get_route_summary()

        @tool
        def daily_summary() -> dict:
            """Pothole counts detected today."""
            return queries.get_daily_summary()

        @tool
        def priority_incidents() -> list:
            """Top incidents ranked by severity score (inspect first)."""
            return queries.get_priority_incidents(5)

        @tool
        def route_condition(route: str) -> dict:
            """Pothole counts for one route, e.g. 'Route A'."""
            return queries.get_route_condition(route)

        tools = {
            t.name: t
            for t in (high_risk_count, route_summary, daily_summary,
                      priority_incidents, route_condition)
        }
        llm = get_llm().bind_tools(list(tools.values()))

        messages = [SystemMessage(content=SYSTEM_RULES), HumanMessage(content=question)]
        response = llm.invoke(messages)

        if not response.tool_calls:
            return answer_question(question)

        messages.append(response)
        for call in response.tool_calls:
            result = tools[call["name"]].invoke(call["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

        return get_llm().invoke(messages).content.strip()
    except Exception as exc:
        print(f"[ai] tool calling failed ({exc}); using keyword router")
        return answer_question(question)


if __name__ == "__main__":
    print(ask_llm(
        "Explain what a high-risk pothole means in one sentence.",
        "LLM not reachable — is Ollama running?",
    ))
