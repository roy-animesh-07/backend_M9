import streamlit as st
import pandas as pd
from backend_service import process_encounter_data, fetch_past_reports
import uuid
from datetime import date

st.set_page_config(page_title="Respiratory Symptom Diagnosis", layout="wide")

st.title("🫁 Respiratory Symptom Diagnosis Portal")

page = st.sidebar.radio("Navigation", ["New Diagnosis", "Past Reports"])

if page == "New Diagnosis":
    st.markdown("Enter patient and clinical encounter details below to calculate the Disease Probability Score.")

    # Organize layout with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Patient & Encounter", "Symptoms & Cough", "Breath Sounds", "History & Exposure"])

    with tab1:
        st.header("Patient Information")
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("Name")
            patient_dob = st.date_input(
                "Date of Birth",
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
        with col2:
            patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
        st.header("Clinical Encounter")
        encounter_type = st.selectbox("Encounter Type", ["Initial Visit", "Follow-up", "Emergency"])
        encounter_date = st.date_input("Encounter Date")

    with tab2:
        st.header("Respiratory Symptoms")
        symptom_type = st.text_input("Symptom Type (e.g., Shortness of breath, Chest pain)")
        
        st.header("Cough Characteristics")
        cough_type = st.selectbox("Cough Type", ["None", "Dry", "Productive", "Chronic", "Barking"])

    with tab3:
        st.header("Breath Sounds Assessment")
        col1, col2 = st.columns(2)
        with col1:
            sound_location = st.text_input("Location (e.g., Left lower lobe)")
            sound_type = st.selectbox("Sound Type", ["Normal", "Wheeze", "Crackle", "Stridor", "Rhonchi"])
        with col2:
            intensity = st.selectbox("Intensity", ["Normal", "Decreased", "Absent"])
            pitch = st.selectbox("Pitch", ["Low", "Medium", "High"])

    with tab4:
        st.header("Smoking History")
        col1, col2 = st.columns(2)
        with col1:
            smoking_status = st.selectbox("Smoking Status", ["Never", "Current", "Former"])
            packs_per_day = st.number_input("Packs per Day", min_value=0.0, step=0.5)
        with col2:
            years_smoked = st.number_input("Years Smoked", min_value=0.0, step=1.0)
            quit_date = st.date_input("Quit Date (if applicable)", value=None)
            
        st.header("Environmental Exposure")
        col3, col4 = st.columns(2)
        with col3:
            exposure_type = st.text_input("Exposure Type (e.g., Dust, Chemicals, None)")
            setting = st.text_input("Setting (e.g., Workplace, Home)")
        with col4:
            duration = st.text_input("Duration (e.g., 5 years, 2 months)")

    st.divider()

    if st.button("Submit Encounter & Calculate Score", type="primary"):
        with st.spinner("Processing Data and Running Diagnostic Engine..."):
            # Compile data dictionaries
            patient_data = {
                "PatientID": str(uuid.uuid4()), # Generate mock ID for simplicty on UI side
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
            
            # Call Backend Service
            result = process_encounter_data(
                patient_data, encounter_data, symptom_data, 
                cough_data, breath_data, smoking_data, exposure_data
            )
            
            if result["success"]:
                st.success("Encounter processed successfully! Data saved to Database.")
                
                st.subheader("📊 Diagnostic Engine Results")
                score_data = result["score"]
                
                col_rs1, col_rs2, col_rs3 = st.columns(3)
                col_rs1.metric("Target Disease", score_data["TargetDisease"])
                col_rs2.metric("Probability Score", f"{score_data['ProbabilityScore']}%")
                col_rs3.metric("Risk Level", score_data["RiskLevel"])
                
                st.info(f"Algorithm Version: {score_data['AlgorithmVersion']}")
            else:
                st.error(f"Error processing encounter: {result['message']}")

elif page == "Past Reports":
    st.header("Past Diagnostic Reports")
    
    with st.spinner("Fetching past reports..."):
        response = fetch_past_reports()
        
    if response["success"]:
        reports = response["data"]
        
        if not reports:
            st.info("No past reports found in the database. Add a new diagnosis first!")
        else:
            df = pd.DataFrame(reports)
            
            # Format display
            if 'EncounterDate' in df.columns:
                df['EncounterDate'] = pd.to_datetime(df['EncounterDate']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Show summary table
            st.subheader("Summary Table")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("Detailed View")
            
            for report in reports:
                date_str = report.get('EncounterDate', 'Unknown Date')
                # If date_str is datetime object, we format it
                if hasattr(date_str, 'strftime'):
                    date_str = date_str.strftime('%Y-%m-%d %H:%M')
                    
                patient_name = report.get('PatientName', 'Unknown Patient')
                risk = report.get('RiskLevel', 'Unknown')
                disease = report.get('TargetDisease', 'Unknown')
                score = report.get('ProbabilityScore', 0)
                
                with st.expander(f"{patient_name} - {date_str} (Risk: {risk})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Patient Name:** {patient_name}")
                        st.markdown(f"**Patient ID:** `{report.get('PatientID', 'N/A')}`")
                        st.markdown(f"**Encounter ID:** `{report.get('EncounterID', 'N/A')}`")
                        st.markdown(f"**Date:** {date_str}")
                    with col2:
                        st.markdown(f"**Target Disease:** {disease}")
                        st.markdown(f"**Probability Score:** {score}%")
                        st.markdown(f"**Risk Level:** {risk}")
                        st.markdown(f"**Algorithm Version:** {report.get('AlgorithmVersion', 'N/A')}")
    else:
        st.error(f"Failed to fetch reports: {response['message']}")
