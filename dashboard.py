from app import run_diagnosis_app
import streamlit as st
import pandas as pd
import uuid
from datetime import date
import requests
from dotenv import load_dotenv
import os

load_dotenv()


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:10000")
# API_BASE_URL = "http://127.0.0.1:8000"
st.set_page_config(
    page_title="Respiratory Symptom Diagnosis Dashboard",
    layout="wide"
)

# ---------- HEADER ----------
st.title("🫁 Respiratory Symptom Diagnosis System")
st.caption("Respiratory condition database")

st.markdown("---")

# ---------- TABS ----------
tabs = st.tabs([
    "🏠 Home",
    "🔗 ER Diagram",
    "⚙ Backend Flow",
    "🩺 Diagnose",
    "📊 Database Collections",
    "📝 MongoDb Pipeline"
])

# ---------- HOME ----------
with tabs[0]:

    st.subheader("Database Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Input Entities")
        st.info("""
        1️⃣ Patient Form  
        2️⃣ Insurance Details  
        3️⃣ Emergency Contact
        """)

    with col2:
        st.markdown("### Output Entities")
        st.success("""
        1️⃣ Patient Record  
        2️⃣ Admission Summary  
        3️⃣ Patient ID
        """)

    st.markdown("---")

    st.write("This dashboard allows navigation through the respiratory diagnosis database system.")

# ---------- ER DIAGRAM ----------
with tabs[1]:

    st.subheader("ER Diagram")

    st.write("Database Entity Relationship Diagram")

    st.image(
        "ER.png",
        use_container_width=True
    )

# ---------- BACKEND FLOW ----------
with tabs[2]:

    st.subheader("Backend Architecture Flow")

    st.write("System backend workflow")

    st.image(
        "data_flow-1.jpg",
        use_container_width=True
    )

# ---------- DIAGNOSE PAGE ----------
with tabs[3]:

    st.subheader("Diagnosis Portal")

    st.info("Click below to open diagnosis page")

    run_diagnosis_app()

with tabs[4]:

    st.subheader("Database Collections")
    st.write("Raw data from all MongoDB collections via API")

    collections = [
        "Patients",
        "Encounters",
        "Symptoms",
        "Cough Data",
        "Breath Sounds",
        "Smoking History",
        "Exposures",
        "Probability Scores"
    ]

    tabs_inner = st.tabs(collections)
    try:
        res = requests.get(f"{API_BASE_URL}/tables", timeout=10)
        response = res.json()
    except Exception as e:
        response = {"success": False, "message": str(e)}

    if response.get("success"):
        all_data = response["data"]

        for i, title in enumerate(collections):
            with tabs_inner[i]:

                st.markdown(f"### `{title}`")

                data = all_data.get(title, [])

                if data:
                    df = pd.DataFrame(data)

                    # shorten IDs for UI
                    for col in df.columns:
                        if 'ID' in col or col.endswith('Id'):
                            df[col] = df[col].apply(
                                lambda x: f"{str(x)[:8]}..." if pd.notnull(x) and len(str(x)) > 12 else x
                            )

                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total Records: {len(data)}")

                else:
                    st.info("No records found.")

    else:
        st.error(response.get("message", "Failed to fetch data"))

with tabs[5]:

    st.header("Database Queries (Aggregation Pipeline)")
    st.info("Since this system utilizes NoSQL MongoDB, standard SQL `JOIN` operations are replaced by **Aggregation Pipelines**. Below is the actual core query script from `database.py` used to generate the output reports tab.")
    
    st.markdown("**Core `$lookup` Aggregation (Equivalent to SQL Multi-JOIN):**")
    st.code('''
pipeline = [
    {
        "$lookup": {
            "from": "clinical_encounters",
            "localField": "EncounterID",
            "foreignField": "EncounterID",
            "as": "encounter"
        }
    },
    { "$unwind": { "path": "$encounter", "preserveNullAndEmptyArrays": True } },
    {
        "$lookup": {
            "from": "patients",
            "localField": "encounter.PatientID",
            "foreignField": "PatientID",
            "as": "patient"
        }
    },
    { "$unwind": { "path": "$patient", "preserveNullAndEmptyArrays": True } },
    {
        "$project": {
            "_id": 0,
            "TargetDisease": 1,
            "ProbabilityScore": 1,
            "RiskLevel": 1,
            "EncounterDate": "$encounter.EncounterDate",
            "PatientName": "$patient.Name"
        }
    },
    { "$sort": {"EncounterDate": -1} }
]
db.disease_probability_scores.aggregate(pipeline)
''', language="python") 