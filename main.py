import aiofiles
from fastapi import FastAPI, HTTPException
import json
from typing import List
from pydantic import BaseModel
import os
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# CORS middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this based on your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define data models using Pydantic
class BloodPressure(BaseModel):
    systolic: dict
    diastolic: dict

class DiagnosisHistory(BaseModel):
    month: str
    year: int
    blood_pressure: BloodPressure
    heart_rate: dict
    respiratory_rate: dict
    temperature: dict

class Diagnostic(BaseModel):
    name: str
    description: str
    status: str

class PatientData(BaseModel):
    id: int  # Ensure each patient has a unique ID
    name: str
    gender: str
    age: int
    profile_picture: str
    date_of_birth: str
    phone_number: str
    emergency_contact: str
    insurance_type: str
    diagnosis_history: List[DiagnosisHistory]
    diagnostic_list: List[Diagnostic]
    lab_results: List[str]

# Load patient data from a JSON file asynchronously
async def load_patient_data():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'patients_data.json')
        async with aiofiles.open(file_path, 'r') as file:
            data = await file.read()
            return json.loads(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading patient data: {str(e)}")

# Endpoint to get a list of patients with dynamically assigned IDs
@app.get("/patients", response_model=List[PatientData])
async def get_patients():
    patients = await load_patient_data()
    # Assign IDs to each patient
    for index, patient in enumerate(patients):
        patient["id"] = index + 1  # Assign IDs starting from 1
    return patients

# Endpoint to get detailed data of a specific patient
@app.get("/patient/{patient_id}", response_model=PatientData)
async def get_patient(patient_id: int):
    patients = await load_patient_data()
    # Check for patient by the correct index since patient_id starts at 1
    if patient_id < 1 or patient_id > len(patients):
        raise HTTPException(status_code=404, detail="Patient not found")

    # Assign ID dynamically as well
    patients_with_ids = [{**patient, "id": index + 1} for index, patient in enumerate(patients)]
    
    return patients_with_ids[patient_id - 1]  # Adjust if your JSON is zero-indexed

# Run the app using `uvicorn filename:app --reload`
