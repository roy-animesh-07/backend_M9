import streamlit as st
import pandas as pd
from backend_service import process_encounter_data, fetch_past_reports
import uuid
from datetime import date


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
                    "EncounterDate": encounter_date,
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

                result = process_encounter_data(
                    patient_data,
                    encounter_data,
                    symptom_data,
                    cough_data,
                    breath_data,
                    smoking_data,
                    exposure_data
                )

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

        response = fetch_past_reports()

        if response["success"]:

            df = pd.DataFrame(response["data"])

            st.dataframe(df, use_container_width=True)

        else:

            st.error(response["message"])