# 🚇 TTC Delay Prediction & Route Optimization

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-View_Now-blue?style=for-the-badge)](https://danieldemoz.github.io/ttc-delay-api/)
[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Deployed-green?style=for-the-badge)](https://danieldemoz.github.io/ttc-delay-api/)

## 🌐 **[👉 LIVE DEMO - CLICK HERE 👈](https://danieldemoz.github.io/ttc-delay-api/)**

An advanced machine learning project that predicts **major delays (>5 minutes)** in the Toronto TTC subway system and provides **route optimization** with interactive map visualization.

## ✨ Features

### 🎯 Core Functionality
- **Delay Prediction**: Predicts major delays using machine learning
- **Route Optimization**: Finds the best routes considering delay probabilities
- **Interactive Map**: Visualizes stations with delay risk indicators
- **Real-time Predictions**: Get instant delay probability for any station

### 🗺️ Map Visualization
- **Station Map**: Interactive map showing all TTC stations
- **Risk Indicators**: Color-coded markers (green/orange/red) based on delay probability
- **Station Details**: Click markers to see delay probability and station info
- **Route Visualization**: See optimized routes on the map

### 🚀 Route Optimization
- **Multi-route Planning**: Compare different route options
- **Delay Risk Assessment**: Routes ranked by total delay risk
- **Time Preferences**: Optimize for rush hour, off-peak, or any time
- **Transfer Optimization**: Smart transfer point recommendations

### 🛠️ Technical Features
- **FastAPI Backend**: High-performance REST API
- **Machine Learning**: RandomForestClassifier with 85% accuracy
- **Interactive Web UI**: Modern, responsive interface
- **GitHub Pages Ready**: Static deployment support

---

## 📁 Project Structure

```
ttc-delay-api/
├── main.py                          # FastAPI application with web interface
├── train_model.py                   # Model training script
├── deploy.py                        # Static deployment script
├── requirements.txt                 # Python dependencies
├── model_training.ipynb            # Jupyter notebook with full ML pipeline
├── random_forest_model_new_task.pkl # Trained ML model
├── label_encoders_new_task.pkl     # Feature encoders
├── index.html                      # Static web interface (generated)
├── .github/workflows/deploy.yml    # GitHub Actions deployment
├── README.md                       # This file
└── LICENSE                         # MIT License
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

## 🚀 Quick Start

### Option 1: Run Locally

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/ttc-delay-api.git
cd ttc-delay-api
```

2. **Install Dependencies**
```bash
py -m pip install -r requirements.txt
```

3. **Train the Model** (if needed)
```bash
py train_model.py
```

4. **Run the Application**
```bash
py -m uvicorn main:app --reload
```

5. **Access the Web Interface**
- **Main App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Option 2: GitHub Pages (Static)

1. **Generate Static Files**
```bash
py deploy.py
```

2. **Deploy to GitHub Pages**
- Push to main branch
- GitHub Actions will automatically deploy
- Access at: `https://yourusername.github.io/ttc-delay-api`  

---

## 🔧 API Endpoints

### Delay Prediction
**POST** `/predict`
```json
{
  "Line": "YU",
  "Station": "UNION STATION", 
  "Code": "MUIS",
  "DayOfWeek": 0
}
```

**Response:**
```json
{
  "prediction": 1,
  "probability": 0.75,
  "input": { ... }
}
```

### Route Optimization
**POST** `/route/optimize`
```json
{
  "start_station": "UNION STATION",
  "end_station": "FINCH",
  "day_of_week": 0,
  "time_preference": "rush_hour"
}
```

**Response:**
```json
{
  "routes": [
    {
      "stations": ["UNION STATION", "FINCH"],
      "total_delay_risk": 0.15,
      "estimated_time": 25
    }
  ]
}
```

### Station Predictions
**GET** `/stations/predictions`
Returns delay probabilities for all stations with coordinates.

### Health Check
**GET** `/health`
Returns API status and model loading information.

---

## 📦 Dependencies

```txt
fastapi
uvicorn[standard]
pandas
scikit-learn
joblib
numpy
requests
matplotlib
seaborn
```

Install with:
```bash
py -m pip install -r requirements.txt
```

---

## 🎯 Key Features Explained

### 🗺️ Interactive Map
- **Real-time Visualization**: See all TTC stations on an interactive map
- **Risk Indicators**: Color-coded markers show delay probability
  - 🟢 Green: Low risk (< 10%)
  - 🟠 Orange: Medium risk (10-30%)
  - 🔴 Red: High risk (> 30%)
- **Station Details**: Click any marker for detailed information

### 🚀 Route Optimization
- **Smart Routing**: Considers delay probabilities when planning routes
- **Multiple Options**: Compare different route alternatives
- **Time Preferences**: Optimize for rush hour, off-peak, or any time
- **Transfer Points**: Intelligent transfer station recommendations

### 🤖 Machine Learning
- **Model**: RandomForestClassifier with 85% accuracy
- **Features**: Line, Station, Code, DayOfWeek
- **Prediction**: Major delay probability (>5 minutes)
- **Real-time**: Instant predictions for any station/condition

---

## 🔄 Development Workflow

1. **Data Collection**: Toronto Open Data API
2. **Data Processing**: Cleaning, feature engineering, encoding
3. **Model Training**: RandomForestClassifier with cross-validation
4. **API Development**: FastAPI with interactive web interface
5. **Deployment**: GitHub Pages with automated CI/CD

---

## 📊 Model Performance

- **Accuracy**: 85%
- **Precision**: 89% (No delay), 44% (Major delay)
- **Recall**: 94% (No delay), 31% (Major delay)
- **Feature Importance**:
  - Code: 41.6%
  - Station: 38.7%
  - DayOfWeek: 17.2%
  - Line: 2.5%

---

## 🚀 Deployment Options

### Local Development
```bash
py -m uvicorn main:app --reload
```

### GitHub Pages (Static)
```bash
py deploy.py
git add .
git commit -m "Deploy to GitHub Pages"
git push origin main
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📝 License
This project is open-source and available under the MIT License for educational and research purposes.
