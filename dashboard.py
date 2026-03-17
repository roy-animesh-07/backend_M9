import streamlit as st
from app import run_diagnosis_app

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
    "🩺 Diagnose"
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
        "er_diagram-2.jpg",
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