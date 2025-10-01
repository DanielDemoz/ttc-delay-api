# TTC Delay Prediction API

End-to-end FastAPI application for predicting major delays in the Toronto TTC subway system using historical data.

---

## Features
- Predicts major delays (>5 minutes).
- Built with FastAPI, Pandas, and RandomForestClassifier.
- POST `/predict` endpoint for JSON requests.
- Includes trained model and encoders.

---

## Project Structure

ttc_delay_api/
├── main.py # FastAPI application code
├── random_forest_model_new_task.pkl # Trained Random Forest model
├── label_encoders_new_task.pkl # Label encoders
├── requirements.txt # Python dependencies
├── README.md # Project description
└── assets/ # Optional screenshots or plots

yaml
Copy code

---

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ttc-delay-api.git
   cd ttc-delay-api
Install dependencies:

bash
Copy code
py -m pip install -r requirements.txt
Run the API:

bash
Copy code
py -m uvicorn main:app --reload
Access the API in browser:

API root: http://127.0.0.1:8000

Swagger docs: http://127.0.0.1:8000/docs

Example Request
POST /predict

json
Copy code
{
  "Line": "YU",
  "Station": "UNION STATION",
  "Code": "MUIS",
  "DayOfWeek": 0
}
Response

json
Copy code
{
  "prediction": 1
}
0 → No major delay

1 → Major delay (>5 minutes)

Key Project Details
Input features: Line, Station, Code, DayOfWeek

Model: RandomForestClassifier

Preprocessing: Label encoding for categorical variables

Output: Major delay prediction (binary)

yaml
Copy code
