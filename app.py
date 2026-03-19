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


def run_diagnosis_app():

    page = st.radio("Navigation", ["New Diagnosis", "Past Reports"])

    if page == "New Diagnosis":

        st.markdown("Enter patient and clinical encounter details below to calculate the Disease Probability Score.")

        tab1, tab2, tab3, tab4 = st.tabs([
            "Patient & Encounter",
            "Symptoms & Cough",
            "Breath Sounds",
            "History & Exposure"
        ])

        with tab1:
            st.header("Patient Information")

            col1, col2 = st.columns(2)

            with col1:
                patient_name = st.text_input("Name")
                patient_dob = st.date_input(
                    "Date of Birth",
                    min_value=date(1900,1,1),
                    max_value=date.today()
                )

            with col2:
                patient_gender = st.selectbox("Gender",["Male","Female","Other"])

            st.header("Clinical Encounter")

            encounter_type = st.selectbox(
                "Encounter Type",
                ["Initial Visit","Follow-up","Emergency"]
            )

            encounter_date = st.date_input("Encounter Date")

        with tab2:
            st.header("Respiratory Symptoms")
            symptom_type = st.text_input(
                "Symptom Type (e.g., Shortness of breath, Chest pain)"
            )

            st.header("Cough Characteristics")

            cough_type = st.selectbox(
                "Cough Type",
                ["None","Dry","Productive","Chronic","Barking"]
            )

        with tab3:
            st.header("Breath Sounds Assessment")

            col1,col2 = st.columns(2)

            with col1:
                sound_location = st.text_input("Location")
                sound_type = st.selectbox(
                    "Sound Type",
                    ["Normal","Wheeze","Crackle","Stridor","Rhonchi"]
                )

            with col2:
                intensity = st.selectbox(
                    "Intensity",
                    ["Normal","Decreased","Absent"]
                )

                pitch = st.selectbox(
                    "Pitch",
                    ["Low","Medium","High"]
                )

        with tab4:
            st.header("Smoking History")

            col1,col2 = st.columns(2)

            with col1:
                smoking_status = st.selectbox(
                    "Smoking Status",
                    ["Never","Current","Former"]
                )

                packs_per_day = st.number_input(
                    "Packs per Day",
                    min_value=0.0,
                    step=0.5
                )

            with col2:
                years_smoked = st.number_input(
                    "Years Smoked",
                    min_value=0.0,
                    step=1.0
                )

                quit_date = st.date_input(
                    "Quit Date (if applicable)",
                    value=None
                )

            st.header("Environmental Exposure")

            col3, col4 = st.columns(2)

            with col3:
                exposure_type = st.text_input("Exposure Type")
                setting = st.text_input("Setting")

            with col4:
                duration = st.text_input("Duration")

        if st.button("Submit Encounter & Calculate Score"):

            with st.spinner("Processing Data..."):

                patient_data = {
                    "PatientID": str(uuid.uuid4()),
                    "Name": patient_name,
                    "DOB": str(patient_dob),
                    "Gender": patient_gender
                }

                encounter_data = {
                    "EncounterID": str(uuid.uuid4()),
                    "PatientID": patient_data["PatientID"],
                    "EncounterDate": str(encounter_date),
                    "EncounterType": encounter_type
                }

                symptom_data = {
                    "EncounterID": encounter_data["EncounterID"],
                    "SymptomType": symptom_type
                }

                cough_data = {
                    "EncounterID": encounter_data["EncounterID"],
                    "CoughType": cough_type
                }

                breath_data = {
                    "EncounterID": encounter_data["EncounterID"],
                    "Location": sound_location,
                    "SoundType": sound_type,
                    "Intensity": intensity,
                    "Pitch": pitch
                }

                smoking_data = {
                    "PatientID": patient_data["PatientID"],
                    "SmokingStatus": smoking_status,
                    "PacksPerDay": float(packs_per_day),
                    "YearsSmoked": float(years_smoked),
                    "QuitDate": str(quit_date) if quit_date else None
                }

                exposure_data = {
                    "PatientID": patient_data["PatientID"],
                    "ExposureType": exposure_type,
                    "Duration": duration,
                    "Setting": setting
                }

                payload = {
                    "patient": patient_data,
                    "encounter": encounter_data,
                    "symptom": symptom_data,
                    "cough": cough_data,
                    "breath": breath_data,
                    "smoking": smoking_data,
                    "exposure": exposure_data
                }

                try:
                    res = requests.post(f"{API_BASE_URL}/process", json=payload)
                    result = res.json()
                except Exception as e:
                    result = {"success": False, "message": str(e)}

                if result["success"]:
                    st.success("Encounter processed successfully")

                    score_data = result["score"]

                    col1, col2, col3 = st.columns(3)

                    col1.metric("Target Disease", score_data["TargetDisease"])
                    col2.metric("Probability Score", f"{score_data['ProbabilityScore']}%")
                    col3.metric("Risk Level", score_data["RiskLevel"])

                else:
                    st.error(result["message"])

    elif page == "Past Reports":

        st.header("Past Diagnostic Reports")

        try:
            res = requests.get(f"{API_BASE_URL}/reports")
            response = res.json()
        except Exception as e:
            response = {"success": False, "message": str(e)}

        if response["success"]:

            df = pd.DataFrame(response["data"])

            if not df.empty:

                df_display = df.copy()

                for col in df_display.columns:
                    if 'ID' in col or col.endswith('Id'):
                        df_display[col] = df_display[col].apply(
                            lambda x: f"{str(x)[:8]}..." if pd.notnull(x) and len(str(x)) > 12 else x
                        )

                st.dataframe(df_display, use_container_width=True)

                st.markdown("---")
                st.subheader("🔍 View Detailed Report")

                # Select report
                selected_idx = st.selectbox(
                    "Select a report",
                    options=range(len(df)),
                    format_func=lambda x: f"{df.iloc[x]['PatientName']} | {df.iloc[x]['TargetDisease']} | {df.iloc[x]['EncounterDate']}"
                )

                selected = df.iloc[selected_idx]

                st.markdown("### 🧾 Report Details")

                col1, col2 = st.columns(2)

                with col1:
                    st.info(f"""
                    **Patient Name:** {selected.get('PatientName')}  
                    **Patient ID:** {selected.get('PatientID')}  
                    **Encounter ID:** {selected.get('EncounterID')}  
                    **Date:** {selected.get('EncounterDate')}
                    """)

                with col2:
                    st.success(f"""
                    **Disease:** {selected.get('TargetDisease')}  
                    **Risk Level:** {selected.get('RiskLevel')}  
                    **Probability Score:** {selected.get('ProbabilityScore')}%  
                    """)
                st.progress(int(selected.get("ProbabilityScore", 0)))

            else:
                st.info("No reports available.")

        else:
            st.error(response["message"])