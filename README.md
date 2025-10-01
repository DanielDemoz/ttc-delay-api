# TTC Delay Prediction API

An end-to-end machine learning project using **FastAPI** to serve a model that predicts **major delays (>5 minutes)** in the Toronto TTC subway system based on historical data.  

---

## Features
- Predicts whether a subway delay will be major or not.
- REST API built with **FastAPI**.
- Model trained with **RandomForestClassifier**.
- Handles categorical features using **Label Encoding**.
- Interactive API documentation with **Swagger UI** at `/docs`.

---

## Project Structure

```
ttc_delay_api/
├── main.py                          # FastAPI application (API code)
├── random_forest_model_new_task.pkl # Trained Random Forest model
├── label_encoders_new_task.pkl      # Encoders for categorical features
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── .gitignore                       # Ignored files for GitHub
└── assets/                          # Optional: visualizations, plots, screenshots
```

---

## Data & Model
- **Dataset**: Toronto Open Data – TTC Subway Delay Data  
- **Target variable**: `MajorDelay`  
  - `0` = No major delay (≤5 minutes)  
  - `1` = Major delay (>5 minutes)  
- **Input features**:
  - `Line` – Subway line (e.g., YU, BD)
  - `Station` – Station name
  - `Code` – Delay cause code
  - `DayOfWeek` – Numeric day of week (0 = Monday, 6 = Sunday)

- **Model used**: RandomForestClassifier  
- **Feature importance (sample result)**:
  - `Code` – 41.5%  
  - `Station` – 38.6%  
  - `DayOfWeek` – 17.2%  
  - `Line` – 2.5%  

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ttc-delay-api.git
cd ttc-delay-api
```

### 2. Install Dependencies
```bash
py -m pip install -r requirements.txt
```

### 3. Run the API
```bash
py -m uvicorn main:app --reload
```

### 4. Access the API
- Root: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
- Interactive Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  

---

## Example Request

### Endpoint
**POST** `/predict`

### Request Body
```json
{
  "Line": "YU",
  "Station": "UNION STATION",
  "Code": "MUIS",
  "DayOfWeek": 0
}
```

### Response
```json
{
  "prediction": 1
}
```

- `0` → No major delay  
- `1` → Major delay (>5 minutes)

---

## Requirements

Main dependencies listed in `requirements.txt`:
```
fastapi
uvicorn
pandas
scikit-learn
joblib
```

Install with:
```bash
py -m pip install -r requirements.txt
```

---

## Key Files
- **main.py** – FastAPI app with `/predict` endpoint.  
- **random_forest_model_new_task.pkl** – Trained Random Forest model.  
- **label_encoders_new_task.pkl** – Encoders for categorical variables.  
- **requirements.txt** – List of dependencies for setup.  
- **README.md** – Project description and usage guide.  
- **.gitignore** – Excludes unnecessary files (cache, logs, models).  

---

## Example Workflow
1. Data loaded from Toronto Open Data API.  
2. Cleaned and processed (`Date`, `Time`, missing values handled).  
3. Features engineered (`Line`, `Station`, `Code`, `DayOfWeek`).  
4. Encoded categorical variables with LabelEncoder.  
5. Model trained with RandomForestClassifier.  
6. Model and encoders saved as `.pkl` files.  
7. FastAPI app created to serve predictions.  

---

## License
This project is open-source and available for educational and research purposes.
