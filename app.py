import streamlit as st
import pandas as pd
from backend_service import process_encounter_data, fetch_past_reports
import uuid
from datetime import date

st.set_page_config(page_title="Respiratory Symptom Diagnosis", layout="wide")

st.title("Respiratory Symptom Diagnosis Database")
st.markdown("##### Respiratory condition database")

# CSS to make radio buttons horizontal exactly as shown
st.markdown("""
<style>
div.row-widget.stRadio > div{flex-direction:row;align-items:center}
</style>
""", unsafe_allow_html=True)

page = st.radio(
    "Navigation", 
    ["🏠 Home", "📝 Form", "🔗 ER Diagram", "📋 Tables", "🔍 SQL Query", "⚡ Triggers", "📄 Output"],
    horizontal=True,
    index=0,
    label_visibility="collapsed"
)

st.divider()

if page == "🏠 Home":
    st.header("Module Dashboard: Architecture & Flow")
    
    st.subheader("🔄 Data Flow Engine")
    st.markdown("""
    1. **Data Collection (`app.py`)**: Data is captured via the frontend Streamlit interface and structured into medical dictionaries. 
    2. **Orchestration (`service.py`)**: The system assigns primary keys (UUIDs) and propagates foreign keys across related datasets.
    3. **Persistence (`db.py`)**: Data is safely stored across 8 decoupled MongoDB collections using `pymongo`.
    4. **Diagnostic Computation**: The logical inference engine processes the data and determines a `ProbabilityScore` and `RiskLevel`.
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠️ Technical Stack")
        st.markdown("""
        - **Frontend**: Streamlit (Python)
        - **Backend Logic**: Python Context Controllers
        - **Database**: MongoDB (NoSQL Document Store)
        - **Integrations**: `pymongo`, `pandas`
        - **Data Format**: JSON / BSON
        """)
    with col2:
        st.subheader("✨ Key Features")
        st.markdown("""
        - 🩺 **Decoupled Architecture**: Encounters are tracked independently of patient demographics.
        - ⚡ **UUID Linking**: Foreign keys map complex symptom data instantaneously.
        - 📈 **Longitudinal Tracking**: Ability to track historical patient encounters dynamically.
        - 🛡️ **Upsert Logic**: Intelligent data writes prevent duplicate patient/history records.
        """)
        
    st.divider()
    
    st.subheader("📖 Quick User Guide")
    st.info("""
    **How to use this system:**
    1. Navigate to the **📝 Form** tab.
    2. Fill out all 4 sub-tabs containing Patient Data, Symptoms, Breath Sounds, and History.
    3. Click *'Submit Encounter'* at the bottom of the form. 
    4. Review the generated `Target Disease` and `Risk Level` immediately.
    5. Check the **📄 Output** tab to see your historical data aggregations alongside all past queries!
    """)

elif page == "📝 Form":
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

elif page == "🔗 ER Diagram":
    st.button("⬅ Back to Modules")
    st.header("Entity Relationship Diagram")
    
    try:
        st.image("er_diagram.png")
    except Exception as e:
        st.error("ER Diagram image not found. Ensure 'er_diagram.png' is in the root directory.")
    
    st.divider()
    
    st.subheader("Key Database Collections")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Core & Encounters**")
        st.code("- patients\n- clinical_encounters\n- disease_probability_scores")
        st.markdown("**Diagnostics Details**")
        st.code("- respiratory_symptoms\n- cough_characteristics\n- breath_sounds")
    with col2:
        st.markdown("**Long-term History**")
        st.code("- smoking_histories\n- environmental_exposures")

elif page == "📋 Tables":
    st.header("Database Tables (Collections)")
    st.markdown("Below are the raw data tables currently stored within the MongoDB Database.")
    
    # We will fetch directly from the database connection here for demonstration of raw tables
    from database import get_db
    db = get_db()
    
    collections_to_show = {
        "Patients": "patients",
        "Encounters": "clinical_encounters",
        "Symptoms": "respiratory_symptoms",
        "Cough Data": "cough_characteristics",
        "Breath Sounds": "breath_sounds",
        "Smoking History": "smoking_histories",
        "Exposures": "environmental_exposures",
        "Probability Scores": "disease_probability_scores"
    }

    tab_titles = list(collections_to_show.keys())
    tabs = st.tabs(tab_titles)
    
    for i, (title, collection_name) in enumerate(collections_to_show.items()):
        with tabs[i]:
            st.subheader(f"Collection: `{collection_name}`")
            with st.spinner(f"Loading {collection_name}..."):
                # Fetch all records, discard the MongoDB _id object for clean pandas rendering
                cursor = db[collection_name].find({}, {"_id": 0})
                data = list(cursor)
                
                if data:
                    df = pd.DataFrame(data)
                    
                    # Shorten all ID fields for better UI display (e.g. 550e8400...)
                    for col in df.columns:
                        if 'ID' in col or col.endswith('Id'):
                            df[col] = df[col].apply(lambda x: f"{str(x)[:8]}..." if pd.notnull(x) and len(str(x)) > 12 else x)
                            
                    st.dataframe(df, width="stretch", hide_index=True)
                    st.caption(f"Total Records: {len(data)}")
                else:
                    st.info(f"No records found in `{collection_name}`.")

elif page == "🔍 SQL Query":
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

elif page == "⚡ Triggers":
    st.header("Database Triggers & Atomicity")
    st.info("In relational databases, Triggers are often used to conditionally handle duplicates and linked history updates. In our MongoDB architecture, this is natively handled using atomic **Upsert Actions**.")
    
    st.markdown("**The `$set` + `upsert` Approach:**")
    st.markdown("For 1-to-1 relationships like Smoking History, when data is passed to the database, our logic uses an upsert to guarantee we natively prevent duplication while keeping history records current without needing separate database-level trigger scripts.")
    
    st.code('''
# From database.py -> update_smoking_history()

db.smoking_histories.update_one(
    {"HistoryID": smoking_data.get("HistoryID")},
    {"$set": smoking_data},
    upsert=True
)
''', language="python")

elif page == "📄 Output":
    st.header("Diagnostic Output Reports")
    with st.spinner("Fetching results..."):
        response = fetch_past_reports()
    
    if response["success"] and response["data"]:
        for report in response["data"]:
            date_str = report.get('EncounterDate', 'Unknown Date')
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
        st.info("No outputs generated yet.")
