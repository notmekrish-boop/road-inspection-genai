"""
RoadGuard AI - Streamlit Dashboard

This dashboard:
1. Displays RoadGuard inspection statistics
2. Displays detected incidents
3. Provides a GenAI assistant
4. Uses actual RoadGuard data as context
5. Connects to the local Ollama LLM
"""

import sys
from pathlib import Path
import uuid
import cv2
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import requests
import pandas as pd
import streamlit as st

from genai.data_context import build_context
from genai.llm_assistant import ask_llm
from detection.inference import detect_image


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000"


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="RoadGuard AI",
    page_icon="🚧",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("🚧 RoadGuard AI")

st.subheader(
    "AI-Powered Road Inspection & Pothole Monitoring"
)

st.markdown(
    """
    RoadGuard AI uses computer vision to detect road defects,
    estimate visual risk, store incidents and provide
    AI-powered inspection insights.
    """
)


# =========================================================
# REFRESH BUTTON
# =========================================================

if st.button("🔄 Refresh Dashboard"):

    st.rerun()


# =========================================================
# API FUNCTION
# =========================================================

def get_api_data(endpoint):

    try:

        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=5
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException:

        st.error(
            "Unable to connect to the RoadGuard API."
        )

        st.info(
            "Make sure FastAPI is running with:"
        )

        st.code(
            "python -m uvicorn backend.api:app --reload"
        )

        return None


# =========================================================
# GET STATISTICS
# =========================================================

statistics = get_api_data(
    "/statistics"
)

if statistics is None:

    st.stop()


total_incidents = statistics.get(
    "total_incidents",
    0
)

risk_distribution = statistics.get(
    "risk_distribution",
    {}
)

low_count = risk_distribution.get(
    "LOW",
    0
)

medium_count = risk_distribution.get(
    "MEDIUM",
    0
)

high_count = risk_distribution.get(
    "HIGH",
    0
)


# =========================================================
# OVERVIEW
# =========================================================

st.markdown("---")

st.header(
    "📊 Road Inspection Overview"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="Total Incidents",
        value=total_incidents
    )


with col2:

    st.metric(
        label="🔴 High Risk",
        value=high_count
    )


with col3:

    st.metric(
        label="🟠 Medium Risk",
        value=medium_count
    )


with col4:

    st.metric(
        label="🟢 Low Risk",
        value=low_count
    )

# =========================================================
# IMAGE UPLOAD AND DETECTION
# =========================================================

st.markdown("---")

st.header(
    "📷 Upload Road Image"
)

st.write(
    """
    Upload a road image and RoadGuard AI will automatically
    detect potholes, estimate visual risk and store the
    resulting incidents in the database.
    """
)


uploaded_file = st.file_uploader(
    "Choose a road image",
    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)


if uploaded_file is not None:

    # -----------------------------------------------------
    # Display uploaded image
    # -----------------------------------------------------

    uploaded_image = Image.open(
        uploaded_file
    )

    st.image(
        uploaded_image,
        caption="Uploaded Road Image",
        use_container_width=True
    )


    # -----------------------------------------------------
    # Detection button
    # -----------------------------------------------------

    if st.button(
        "🔍 Detect Potholes",
        type="primary"
    ):

        with st.spinner(
            "RoadGuard AI is analyzing the image..."
        ):

            try:

                # -----------------------------------------
                # Create upload directories
                # -----------------------------------------

                input_directory = (
                    PROJECT_ROOT
                    / "demo"
                    / "input"
                    / "uploads"
                )

                output_directory = (
                    PROJECT_ROOT
                    / "demo"
                    / "output"
                    / "uploads"
                )


                input_directory.mkdir(
                    parents=True,
                    exist_ok=True
                )

                output_directory.mkdir(
                    parents=True,
                    exist_ok=True
                )


                # -----------------------------------------
                # Generate unique filename
                # -----------------------------------------

                unique_id = uuid.uuid4().hex[:8]

                input_filename = (
                    f"{unique_id}_{uploaded_file.name}"
                )

                output_filename = (
                    f"detected_{unique_id}_"
                    f"{uploaded_file.name}"
                )


                input_path = (
                    input_directory
                    / input_filename
                )

                output_path = (
                    output_directory
                    / output_filename
                )


                # -----------------------------------------
                # Save uploaded image
                # -----------------------------------------

                with open(
                    input_path,
                    "wb"
                ) as file:

                    file.write(
                        uploaded_file.getbuffer()
                    )


                # -----------------------------------------
                # Run RoadGuard detection
                # -----------------------------------------

                result = detect_image(
                    image_path=input_path,
                    output_path=output_path
                )


                # -----------------------------------------
                # Display result
                # -----------------------------------------

                st.success(
                    "Image analysis completed successfully."
                )


                detection_count = result[
                    "detection_count"
                ]


                if detection_count == 0:

                    st.info(
                        "No potholes were detected in this image."
                    )

                else:

                    st.success(
                        f"{detection_count} pothole(s) detected."
                    )


                # -----------------------------------------
                # Display annotated image
                # -----------------------------------------

                st.subheader(
                    "🎯 Detection Result"
                )

                st.image(
                    str(output_path),
                    caption="RoadGuard Detection Result",
                    use_container_width=True
                )


                # -----------------------------------------
                # Detection details
                # -----------------------------------------

                st.subheader(
                    "📋 Detection Details"
                )


                if result["detections"]:

                    detection_dataframe = pd.DataFrame(
                        result["detections"]
                    )


                    detection_dataframe[
                        "confidence"
                    ] = (
                        detection_dataframe[
                            "confidence"
                        ] * 100
                    ).round(2)


                    detection_dataframe = (
                        detection_dataframe.rename(
                            columns={
                                "incident_id":
                                    "Incident ID",

                                "object_type":
                                    "Object",

                                "confidence":
                                    "Confidence (%)",

                                "risk_score":
                                    "Risk Score",

                                "risk_level":
                                    "Risk Level"
                            }
                        )
                    )


                    st.dataframe(
                        detection_dataframe[
                            [
                                "Incident ID",
                                "Object",
                                "Confidence (%)",
                                "Risk Score",
                                "Risk Level"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )


            except Exception as error:

                st.error(
                    "Image detection failed."
                )

                st.exception(
                    error
                )

# =========================================================
# RISK DISTRIBUTION
# =========================================================

st.markdown("---")

st.header(
    "⚠️ Risk Distribution"
)


risk_data = pd.DataFrame(
    {
        "Risk Level": [
            "LOW",
            "MEDIUM",
            "HIGH"
        ],

        "Incidents": [
            low_count,
            medium_count,
            high_count
        ]
    }
)


chart_col1, chart_col2 = st.columns(2)


with chart_col1:

    st.bar_chart(
        risk_data.set_index(
            "Risk Level"
        )
    )


with chart_col2:

    st.dataframe(
        risk_data,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# INCIDENTS
# =========================================================

st.markdown("---")

st.header(
    "🚨 Road Incidents"
)


incident_data = get_api_data(
    "/incidents"
)


if incident_data is not None:

    incidents = incident_data.get(
        "incidents",
        []
    )

    if len(incidents) == 0:

        st.info(
            "No road incidents have been detected yet."
        )

    else:

        dataframe = pd.DataFrame(
            incidents
        )

        display_columns = [
            "incident_id",
            "timestamp",
            "object_type",
            "confidence",
            "risk_score",
            "risk_level",
            "source"
        ]

        available_columns = [
            column
            for column in display_columns
            if column in dataframe.columns
        ]

        display_dataframe = dataframe[
            available_columns
        ].copy()


        if "confidence" in display_dataframe.columns:

            display_dataframe["confidence"] = (
                display_dataframe["confidence"] * 100
            ).round(2)


        display_dataframe = display_dataframe.rename(
            columns={
                "incident_id": "Incident ID",
                "timestamp": "Timestamp",
                "object_type": "Object",
                "confidence": "Confidence (%)",
                "risk_score": "Risk Score",
                "risk_level": "Risk Level",
                "source": "Source"
            }
        )


        st.dataframe(
            display_dataframe,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# GENAI ASSISTANT
# =========================================================

st.markdown("---")

st.header(
    "🤖 RoadGuard AI Assistant"
)

st.write(
    """
    Ask questions about the actual road inspection data.
    The assistant uses the latest RoadGuard database information
    and the local Llama 3.2 model.
    """
)


question = st.text_input(
    "Ask RoadGuard AI:",
    placeholder=(
        "Example: Which risk category needs "
        "the most attention?"
    )
)


if st.button(
    "🤖 Ask RoadGuard AI",
    type="primary"
):

    if question.strip() == "":

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "RoadGuard AI is analyzing the inspection data..."
        ):

            try:

                # -----------------------------------------
                # IMPORTANT:
                # Get FRESH data every time the user asks
                # a question.
                # -----------------------------------------

                context = build_context()


                # -----------------------------------------
                # Send the grounded context to the LLM
                # -----------------------------------------

                answer = ask_llm(
                    question,
                    context
                )


                # -----------------------------------------
                # Display answer
                # -----------------------------------------

                st.markdown(
                    "### 🧠 RoadGuard AI"
                )

                st.info(
                    answer
                )


            except Exception as error:

                st.error(
                    "Unable to communicate with the "
                    "local LLM."
                )

                st.code(
                    str(error)
                )

                st.info(
                    """
                    Make sure Ollama is running and the
                    RoadGuard model is available.

                    Try:

                    ollama list

                    and verify that llama3.2:3b
                    is installed.
                    """
                )


# =========================================================
# SUGGESTED QUESTIONS
# =========================================================

st.markdown(
    "### 💡 Try asking"
)

suggestion_col1, suggestion_col2 = st.columns(2)


with suggestion_col1:

    st.markdown(
        """
        - How many potholes were detected?
        - How many high-risk incidents are there?
        - Show the risk distribution.
        """
    )


with suggestion_col2:

    st.markdown(
        """
        - Which incidents need priority attention?
        - Give me an inspection summary.
        - Explain the results to a municipal officer.
        """
    )


# =========================================================
# INCIDENT MAP
# =========================================================

st.markdown("---")

st.header(
    "🗺️ Incident Map"
)

st.info(
    """
    GPS coordinates are not currently available for the
    image-based detection pipeline.

    The map will become active when RoadGuard receives
    latitude/longitude information from GPS-enabled
    video or field devices.
    """
)


# =========================================================
# SYSTEM INFORMATION
# =========================================================

st.markdown("---")

st.header(
    "ℹ️ System Information"
)


info_col1, info_col2, info_col3, info_col4 = st.columns(4)


with info_col1:

    st.write(
        "**Detection Model**"
    )

    st.write(
        "YOLO11n"
    )


with info_col2:

    st.write(
        "**Detection Type**"
    )

    st.write(
        "Pothole Detection"
    )


with info_col3:

    st.write(
        "**Backend**"
    )

    st.write(
        "FastAPI + SQLite"
    )


with info_col4:

    st.write(
        "**GenAI Model**"
    )

    st.write(
        "Llama 3.2 3B"
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "RoadGuard AI — AI-Powered Road Inspection System"
)