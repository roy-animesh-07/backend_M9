import uuid
from datetime import datetime, date
from database import (
    insert_patient, insert_encounter, insert_symptom, 
    insert_cough_characteristic, insert_breath_sound, 
    update_smoking_history, update_environmental_exposure,
    insert_or_update_disease_score, get_all_reports
)

def calculate_disease_probability(symptom_data, cough_data, breath_data, smoking_data, exposure_data):
    # Mock Diagnostic Engine
    return {
        "TargetDisease": "Pending Analysis",
        "ProbabilityScore": 0,
        "RiskLevel": "Pending",
        "AlgorithmVersion": "v0.0-pending"
    }

def process_encounter_data(patient, encounter, symptom, cough, breath, smoking, exposure):
    try:
        # Link relations using IDs
        patient_id = patient.get("PatientID", str(uuid.uuid4()))
        patient["PatientID"] = patient_id
        
        encounter_id = encounter.get("EncounterID", str(uuid.uuid4()))
        encounter["EncounterID"] = encounter_id
        encounter["PatientID"] = patient_id
        
        if "EncounterDate" not in encounter:
            encounter["EncounterDate"] = datetime.now()
        elif isinstance(encounter["EncounterDate"], date) and not isinstance(encounter["EncounterDate"], datetime):
            encounter["EncounterDate"] = datetime.combine(encounter["EncounterDate"], datetime.min.time())
            
        symptom["EncounterID"] = encounter_id
        cough["EncounterID"] = encounter_id
        breath["EncounterID"] = encounter_id
        
        smoking["PatientID"] = patient_id
        exposure["PatientID"] = patient_id

        # Save to database
        insert_patient(patient)
        insert_encounter(encounter)
        insert_symptom(symptom)
        insert_cough_characteristic(cough)
        insert_breath_sound(breath)
        update_smoking_history(smoking)
        update_environmental_exposure(exposure)
        
        # Calculate and save diagnostic score
        score_result = calculate_disease_probability(symptom, cough, breath, smoking, exposure)
        
        score_data = {
            "EncounterID": encounter_id,
            "TargetDisease": score_result["TargetDisease"],
            "ProbabilityScore": score_result["ProbabilityScore"],
            "RiskLevel": score_result["RiskLevel"],
            "AlgorithmVersion": score_result["AlgorithmVersion"]
        }
        
        insert_or_update_disease_score(score_data)
        
        return {
            "success": True, 
            "message": "Data processed successfully", 
            "score": score_data
        }

    except Exception as e:
        return {"success": False, "message": str(e)}

def fetch_past_reports():
    try:
        reports = get_all_reports()
        return {"success": True, "data": reports}
    except Exception as e:
        return {"success": False, "message": str(e)}
