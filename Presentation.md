# 🫁 Respiratory Symptom Diagnosis Portal
**Contributors**: [Your Name/Team]
**Course**: DBMS Project

---

# 🚀 Project Overview

**Objective**: 
A robust application to collect patient clinical encounters, respiratory symptoms, and relevant medical history to generate a theoretical disease probability score.

**Key Features**:
- **Patient Registration**: Capture demographics.
- **Encounter Processing**: Track symptoms, cough characteristics, breath sounds, and environmental exposures.
- **Diagnostic Engine**: Calculates probability score and risk level.
- **Past Reports Querying**: Aggregates stored diagnoses for review.

---

# 🏗️ System Architecture

- **Frontend Interface (UI)**: Built with **Streamlit** (Python).
- **Backend Service**: Serves as the middleware (`backend_service.py`), generating UUIDs, orchestrating data linkage, and running the diagnostic engine logic.
- **Database**: **MongoDB** (`database.py`) using `pymongo`. A NoSQL document-based structure tailored for fast, decoupled medical records.

---

# 🗄️ Database Schema & Collections

The data is normalized logically but stored in MongoDB as interconnected collections:

1. **`patients`**
   - `PatientID` (Primary Key), `Name`, `DOB`, `Gender`
2. **`clinical_encounters`**
   - `EncounterID` (PK), `PatientID` (FK), `EncounterDate`, `EncounterType`
3. **`respiratory_symptoms`**
   - `SymptomID` (PK), `EncounterID` (FK), `SymptomType`
4. **`cough_characteristics`**
   - `CharacteristicID` (PK), `EncounterID` (FK), `CoughType`
5. **`breath_sounds`**
   - `SoundID` (PK), `EncounterID` (FK), `Location`, `SoundType`, `Intensity`, `Pitch`
6. **`smoking_histories`** (Upsert behavior per patient)
   - `HistoryID` (PK), `PatientID` (FK), `SmokingStatus`, `PacksPerDay`, `YearsSmoked`, `QuitDate`
7. **`environmental_exposures`** (Upsert behavior per patient)
   - `PatientID` (PK/FK), `ExposureType`, `Duration`, `Setting`
8. **`disease_probability_scores`**
   - `ScoreID` (PK), `EncounterID` (FK), `TargetDisease`, `ProbabilityScore`, `RiskLevel`, `AlgorithmVersion`

---

# 🔗 Entity Relationship (How Tables Connect)

The database utilizes clear structural links through ID mapping:

**1. The Core Anchor: `patients` Table**
- Acts as the main anchor for all records. 
- **Primary Key**: `PatientID`

**2. The Event Hub: `clinical_encounters` Table**
- Links to the Patient. Every time someone visits, a new Encounter is born.
- **Primary Key**: `EncounterID`
- **Foreign Key**: `PatientID` (Links back to patients table).

**3. Encounter Details: The 1-to-Many Tables**
- Symptoms, Coughs, and Breath sounds are measured *per visit*. 
- They do not map to the patient directly, they map to the specific encounter.
- **Foreign Key**: `EncounterID` (Links back to clinical_encounters).

**4. Patient History: The 1-to-1 Tables**
- Smoking History & Environmental Exposures are unique to the *person*, not the visit. 
- **Foreign Key**: `PatientID` (Links back to patients).

**5. The Output: `disease_probability_scores` Table**
- The diagnostic engine's result.
- **Foreign Key**: `EncounterID` (Links back to clinical_encounters).

---

# 🔄 ER Diagram Summary

![Database Entity Relationship Diagram](/home/animesh-roy/.gemini/antigravity/brain/80e38f32-13c1-4422-a492-7f33317034eb/er_diagram_strict_attributes_1773750929812.png)

---

# 🔄 Workflow: New Diagnosis

1. **User Input (`app.py`)**: User enters details in Streams tabs (Patient Info, Symptoms, Breath Sounds, History).
2. **Data Orchestration (`backend_service.py`)**:
   - Assigns unique `UUIDs` (`PatientID`, `EncounterID`).
   - Propagates these foreign keys to related dataset dictionaries (e.g., Encounter ID sent to `symptom`, `cough`, and `breath` data).
3. **Database Insertion (`database.py`)**:
   - `insert_patient()` (Upserts via PatientID to prevent duplication)
   - `insert_encounter()`, `insert_symptom()`, etc.
   - Updates one-to-one records like smoking history & exposures.
4. **Diagnostic Engine Call**: `calculate_disease_probability()` processes all details.
5. **Result Storage**: Engine result is pushed to `disease_probability_scores`.
6. **UI Update**: Probability score and risk levels are dynamically shown to the User.

---

# 📊 Workflow: Querying Past Reports

Fetching history relies heavily on **MongoDB Aggregation Pipelines**.

1. **User Request**: Navigates to "Past Reports" page in the UI.
2. **Backend Execution (`get_all_reports()`)**:
   - Hits `disease_probability_scores` collection.
   - `$lookup` against `clinical_encounters` using `EncounterID`.
   - `$unwind` encounter array to flatten documents.
   - `$lookup` against `patients` using `PatientID` (found in the unwound encounter).
   - `$unwind` patient array.
   - `$project` key data elements (Score, Disease, Date, Patient Name).
   - `$sort` by date descending.
3. **Display**: Converted to a Pandas DataFrame and rendered as a tabular breakdown and Detailed Expanders in Streamlit.
