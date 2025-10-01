from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import pickle

# Load trained model + encoders
with open("random_forest_model_new_task.pkl", "rb") as f:
    model = pickle.load(f)

with open("label_encoders_new_task.pkl", "rb") as f:
    encoders = pickle.load(f)

# Create FastAPI app
app = FastAPI(title="TTC Delay Prediction API")

# Input format
class DelayRequest(BaseModel):
    Line: str
    Station: str
    Code: str
    DayOfWeek: int  # 0=Monday … 6=Sunday

@app.post("/predict")
def predict_delay(request: DelayRequest):
    data = request.dict()

    # Encode categories
    line_encoded = encoders['Line'].transform([data['Line']])[0]
    station_encoded = encoders['Station'].transform([data['Station']])[0]
    code_encoded = encoders['Code'].transform([data['Code']])[0]

    # Build dataframe
    X = pd.DataFrame([{
        "Line": line_encoded,
        "Station": station_encoded,
        "Code": code_encoded,
        "DayOfWeek": data['DayOfWeek']
    }])

    prediction = model.predict(X)[0]

    return {
        "prediction": int(prediction),  # 0 = no major delay, 1 = major delay
        "input": data
    }
