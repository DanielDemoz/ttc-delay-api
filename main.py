from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
import pickle
import os
import json
from typing import List, Dict, Optional
import numpy as np

# Initialize FastAPI app
app = FastAPI(title="TTC Delay Prediction API", description="Predict TTC subway delays with map visualization and route optimization")

# Load trained model + encoders with error handling
model = None
encoders = None

try:
    if os.path.exists("random_forest_model_new_task.pkl"):
        with open("random_forest_model_new_task.pkl", "rb") as f:
            model = pickle.load(f)
    else:
        print("Warning: Model file not found. Please train the model first.")
        
    if os.path.exists("label_encoders_new_task.pkl"):
        with open("label_encoders_new_task.pkl", "rb") as f:
            encoders = pickle.load(f)
    else:
        print("Warning: Encoders file not found. Please train the model first.")
except Exception as e:
    print(f"Error loading model files: {e}")

# TTC Station coordinates (sample data - in production, use complete dataset)
TTC_STATIONS = {
    "UNION STATION": {"lat": 43.6452, "lng": -79.3806, "line": "YU"},
    "BLOOR-YONGE": {"lat": 43.6706, "lng": -79.3856, "line": "YU"},
    "ST GEORGE": {"lat": 43.6684, "lng": -79.3997, "line": "YU"},
    "SPADINA": {"lat": 43.6674, "lng": -79.4047, "line": "YU"},
    "BAY": {"lat": 43.6706, "lng": -79.3856, "line": "YU"},
    "SHEPPARD-YONGE": {"lat": 43.7615, "lng": -79.4110, "line": "YU"},
    "FINCH": {"lat": 43.7805, "lng": -79.4147, "line": "YU"},
    "DOWNSVIEW": {"lat": 43.7225, "lng": -79.4778, "line": "YU"},
    "KIPLING": {"lat": 43.6372, "lng": -79.5356, "line": "BD"},
    "KENNEDY": {"lat": 43.7322, "lng": -79.2628, "line": "BD"},
    "DON MILLS": {"lat": 43.7615, "lng": -79.3328, "line": "BD"},
    "SCARBOROUGH CENTRE": {"lat": 43.7731, "lng": -79.2578, "line": "SRT"}
}

# Input format
class DelayRequest(BaseModel):
    Line: str
    Station: str
    Code: str
    DayOfWeek: int  # 0=Monday … 6=Sunday

class RouteRequest(BaseModel):
    start_station: str
    end_station: str
    day_of_week: int
    time_preference: str = "any"  # "rush_hour", "off_peak", "any"

class StationInfo(BaseModel):
    name: str
    line: str
    lat: float
    lng: float
    delay_probability: float

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main web interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TTC Delay Prediction & Route Optimization</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #d52b1e; margin: 0; }
            .header p { color: #666; margin: 10px 0; }
            .tabs { display: flex; margin-bottom: 20px; border-bottom: 2px solid #eee; }
            .tab { padding: 10px 20px; cursor: pointer; border: none; background: none; font-size: 16px; }
            .tab.active { border-bottom: 2px solid #d52b1e; color: #d52b1e; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-group select, .form-group input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            .btn { background: #d52b1e; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            .btn:hover { background: #b8241a; }
            .result { margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 4px; }
            .map-container { height: 400px; margin-top: 20px; border: 1px solid #ddd; border-radius: 4px; }
            .prediction-high { color: #d52b1e; font-weight: bold; }
            .prediction-low { color: #28a745; font-weight: bold; }
            .route-option { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            .route-option.best { border-color: #28a745; background: #f8fff8; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚇 TTC Delay Prediction & Route Optimization</h1>
                <p>Predict delays and find the best routes using machine learning</p>
            </div>
            
            <div class="tabs">
                <button class="tab active" onclick="showTab('predict')">Delay Prediction</button>
                <button class="tab" onclick="showTab('route')">Route Optimization</button>
                <button class="tab" onclick="showTab('map')">Station Map</button>
            </div>
            
            <div id="predict" class="tab-content active">
                <h3>Predict Delay Probability</h3>
                <form id="predictForm">
                    <div class="form-group">
                        <label>Line:</label>
                        <select id="line" required>
                            <option value="">Select Line</option>
                            <option value="YU">Yonge-University</option>
                            <option value="BD">Bloor-Danforth</option>
                            <option value="SRT">Scarborough RT</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Station:</label>
                        <select id="station" required>
                            <option value="">Select Station</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Delay Code:</label>
                        <select id="code" required>
                            <option value="">Select Code</option>
                            <option value="MUIS">Mechanical Issue</option>
                            <option value="SEC">Security</option>
                            <option value="SIG">Signal Problem</option>
                            <option value="PAS">Passenger Issue</option>
                            <option value="TRA">Track Problem</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Day of Week:</label>
                        <select id="dayOfWeek" required>
                            <option value="0">Monday</option>
                            <option value="1">Tuesday</option>
                            <option value="2">Wednesday</option>
                            <option value="3">Thursday</option>
                            <option value="4">Friday</option>
                            <option value="5">Saturday</option>
                            <option value="6">Sunday</option>
                        </select>
                    </div>
                    <button type="submit" class="btn">Predict Delay</button>
                </form>
                <div id="predictResult" class="result" style="display: none;"></div>
            </div>
            
            <div id="route" class="tab-content">
                <h3>Route Optimization</h3>
                <form id="routeForm">
                    <div class="form-group">
                        <label>Start Station:</label>
                        <select id="startStation" required>
                            <option value="">Select Start Station</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>End Station:</label>
                        <select id="endStation" required>
                            <option value="">Select End Station</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Day of Week:</label>
                        <select id="routeDayOfWeek" required>
                            <option value="0">Monday</option>
                            <option value="1">Tuesday</option>
                            <option value="2">Wednesday</option>
                            <option value="3">Thursday</option>
                            <option value="4">Friday</option>
                            <option value="5">Saturday</option>
                            <option value="6">Sunday</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Time Preference:</label>
                        <select id="timePreference">
                            <option value="any">Any Time</option>
                            <option value="rush_hour">Rush Hour (7-9 AM, 5-7 PM)</option>
                            <option value="off_peak">Off Peak</option>
                        </select>
                    </div>
                    <button type="submit" class="btn">Find Best Route</button>
                </form>
                <div id="routeResult" class="result" style="display: none;"></div>
            </div>
            
            <div id="map" class="tab-content">
                <h3>Station Map with Delay Predictions</h3>
                <div id="map" class="map-container"></div>
            </div>
        </div>
        
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            let map;
            let stationMarkers = {};
            
            // Initialize map
            function initMap() {
                map = L.map('map').setView([43.6532, -79.3832], 11);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
                loadStationPredictions();
            }
            
            // Load station predictions and display on map
            async function loadStationPredictions() {
                try {
                    const response = await fetch('/stations/predictions');
                    const stations = await response.json();
                    
                    stations.forEach(station => {
                        const color = station.delay_probability > 0.3 ? 'red' : 
                                    station.delay_probability > 0.1 ? 'orange' : 'green';
                        
                        const marker = L.circleMarker([station.lat, station.lng], {
                            color: color,
                            fillColor: color,
                            fillOpacity: 0.7,
                            radius: 8
                        }).addTo(map);
                        
                        marker.bindPopup(`
                            <b>${station.name}</b><br>
                            Line: ${station.line}<br>
                            Delay Probability: ${(station.delay_probability * 100).toFixed(1)}%
                        `);
                        
                        stationMarkers[station.name] = marker;
                    });
                } catch (error) {
                    console.error('Error loading station predictions:', error);
                }
            }
            
            // Tab switching
            function showTab(tabName) {
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                
                event.target.classList.add('active');
                document.getElementById(tabName).classList.add('active');
                
                if (tabName === 'map' && !map) {
                    setTimeout(initMap, 100);
                }
            }
            
            // Populate station dropdowns
            function populateStations() {
                const stations = Object.keys(TTC_STATIONS);
                const stationSelects = ['station', 'startStation', 'endStation'];
                
                stationSelects.forEach(selectId => {
                    const select = document.getElementById(selectId);
                    select.innerHTML = '<option value="">Select Station</option>';
                    stations.forEach(station => {
                        const option = document.createElement('option');
                        option.value = station;
                        option.textContent = station;
                        select.appendChild(option);
                    });
                });
            }
            
            // Update station dropdown based on line selection
            document.getElementById('line').addEventListener('change', function() {
                const line = this.value;
                const stationSelect = document.getElementById('station');
                stationSelect.innerHTML = '<option value="">Select Station</option>';
                
                Object.entries(TTC_STATIONS).forEach(([name, info]) => {
                    if (line === '' || info.line === line) {
                        const option = document.createElement('option');
                        option.value = name;
                        option.textContent = name;
                        stationSelect.appendChild(option);
                    }
                });
            });
            
            // Handle prediction form
            document.getElementById('predictForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = {
                    Line: document.getElementById('line').value,
                    Station: document.getElementById('station').value,
                    Code: document.getElementById('code').value,
                    DayOfWeek: parseInt(document.getElementById('dayOfWeek').value)
                };
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });
                    
                    const result = await response.json();
                    displayPredictionResult(result);
                } catch (error) {
                    console.error('Error:', error);
                }
            });
            
            // Handle route form
            document.getElementById('routeForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = {
                    start_station: document.getElementById('startStation').value,
                    end_station: document.getElementById('endStation').value,
                    day_of_week: parseInt(document.getElementById('routeDayOfWeek').value),
                    time_preference: document.getElementById('timePreference').value
                };
                
                try {
                    const response = await fetch('/route/optimize', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });
                    
                    const result = await response.json();
                    displayRouteResult(result);
                } catch (error) {
                    console.error('Error:', error);
                }
            });
            
            // Display prediction result
            function displayPredictionResult(result) {
                const resultDiv = document.getElementById('predictResult');
                const prediction = result.prediction;
                const probability = result.probability || 0;
                
                resultDiv.innerHTML = `
                    <h4>Prediction Result</h4>
                    <p><strong>Station:</strong> ${result.input.Station}</p>
                    <p><strong>Line:</strong> ${result.input.Line}</p>
                    <p><strong>Delay Code:</strong> ${result.input.Code}</p>
                    <p><strong>Day:</strong> ${getDayName(result.input.DayOfWeek)}</p>
                    <p><strong>Prediction:</strong> 
                        <span class="${prediction === 1 ? 'prediction-high' : 'prediction-low'}">
                            ${prediction === 1 ? 'HIGH DELAY RISK' : 'LOW DELAY RISK'}
                        </span>
                    </p>
                    <p><strong>Probability:</strong> ${(probability * 100).toFixed(1)}%</p>
                `;
                resultDiv.style.display = 'block';
            }
            
            // Display route result
            function displayRouteResult(result) {
                const resultDiv = document.getElementById('routeResult');
                let html = `<h4>Route Options</h4>`;
                
                result.routes.forEach((route, index) => {
                    const isBest = index === 0;
                    html += `
                        <div class="route-option ${isBest ? 'best' : ''}">
                            <h5>${isBest ? '🏆 Best Route' : `Route ${index + 1}`}</h5>
                            <p><strong>Total Delay Risk:</strong> ${(route.total_delay_risk * 100).toFixed(1)}%</p>
                            <p><strong>Stations:</strong> ${route.stations.join(' → ')}</p>
                            <p><strong>Estimated Travel Time:</strong> ${route.estimated_time} minutes</p>
                        </div>
                    `;
                });
                
                resultDiv.innerHTML = html;
                resultDiv.style.display = 'block';
            }
            
            // Helper function to get day name
            function getDayName(dayOfWeek) {
                const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
                return days[dayOfWeek];
            }
            
            // Initialize page
            document.addEventListener('DOMContentLoaded', function() {
                populateStations();
            });
            
            // TTC Stations data (same as backend)
            const TTC_STATIONS = {
                "UNION STATION": {"lat": 43.6452, "lng": -79.3806, "line": "YU"},
                "BLOOR-YONGE": {"lat": 43.6706, "lng": -79.3856, "line": "YU"},
                "ST GEORGE": {"lat": 43.6684, "lng": -79.3997, "line": "YU"},
                "SPADINA": {"lat": 43.6674, "lng": -79.4047, "line": "YU"},
                "BAY": {"lat": 43.6706, "lng": -79.3856, "line": "YU"},
                "SHEPPARD-YONGE": {"lat": 43.7615, "lng": -79.4110, "line": "YU"},
                "FINCH": {"lat": 43.7805, "lng": -79.4147, "line": "YU"},
                "DOWNSVIEW": {"lat": 43.7225, "lng": -79.4778, "line": "YU"},
                "KIPLING": {"lat": 43.6372, "lng": -79.5356, "line": "BD"},
                "KENNEDY": {"lat": 43.7322, "lng": -79.2628, "line": "BD"},
                "DON MILLS": {"lat": 43.7615, "lng": -79.3328, "line": "BD"},
                "SCARBOROUGH CENTRE": {"lat": 43.7731, "lng": -79.2578, "line": "SRT"}
            };
        </script>
    </body>
    </html>
    """

@app.post("/predict")
def predict_delay(request: DelayRequest):
    """Predict delay probability for a given station and conditions"""
    if model is None or encoders is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")
    
    data = request.dict()

    try:
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
        probability = model.predict_proba(X)[0][1]  # Probability of major delay

        return {
            "prediction": int(prediction),  # 0 = no major delay, 1 = major delay
            "probability": float(probability),
            "input": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.get("/stations/predictions")
def get_station_predictions():
    """Get delay predictions for all stations"""
    if model is None or encoders is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")
    
    stations = []
    
    for station_name, station_info in TTC_STATIONS.items():
        try:
            # Use a default delay code for general prediction
            line_encoded = encoders['Line'].transform([station_info['line']])[0]
            station_encoded = encoders['Station'].transform([station_name])[0]
            code_encoded = encoders['Code'].transform(['MUIS'])[0]  # Default to mechanical issue
            
            # Predict for Monday (typical weekday)
            X = pd.DataFrame([{
                "Line": line_encoded,
                "Station": station_encoded,
                "Code": code_encoded,
                "DayOfWeek": 0
            }])
            
            probability = model.predict_proba(X)[0][1]
            
            stations.append(StationInfo(
                name=station_name,
                line=station_info['line'],
                lat=station_info['lat'],
                lng=station_info['lng'],
                delay_probability=float(probability)
            ))
        except Exception as e:
            # If station not in training data, use average probability
            stations.append(StationInfo(
                name=station_name,
                line=station_info['line'],
                lat=station_info['lat'],
                lng=station_info['lng'],
                delay_probability=0.15  # Default probability
            ))
    
    return stations

@app.post("/route/optimize")
def optimize_route(request: RouteRequest):
    """Find the best route between two stations considering delay probabilities"""
    if model is None or encoders is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")
    
    start_station = request.start_station
    end_station = request.end_station
    day_of_week = request.day_of_week
    time_preference = request.time_preference
    
    # Simple route optimization algorithm
    routes = []
    
    # Get station coordinates
    if start_station not in TTC_STATIONS or end_station not in TTC_STATIONS:
        raise HTTPException(status_code=400, detail="Invalid station names")
    
    start_info = TTC_STATIONS[start_station]
    end_info = TTC_STATIONS[end_station]
    
    # Calculate direct route
    direct_route = calculate_route_risk([start_station, end_station], day_of_week, time_preference)
    routes.append(direct_route)
    
    # Calculate alternative routes with transfers
    if start_info['line'] != end_info['line']:
        # Find transfer stations
        transfer_stations = find_transfer_stations(start_info['line'], end_info['line'])
        
        for transfer in transfer_stations:
            route_stations = [start_station, transfer, end_station]
            route_risk = calculate_route_risk(route_stations, day_of_week, time_preference)
            routes.append(route_risk)
    
    # Sort routes by total delay risk (ascending)
    routes.sort(key=lambda x: x['total_delay_risk'])
    
    return {"routes": routes}

def calculate_route_risk(stations: List[str], day_of_week: int, time_preference: str) -> Dict:
    """Calculate total delay risk for a route"""
    total_risk = 0
    estimated_time = 0
    
    for i, station in enumerate(stations):
        try:
            station_info = TTC_STATIONS[station]
            line_encoded = encoders['Line'].transform([station_info['line']])[0]
            station_encoded = encoders['Station'].transform([station])[0]
            code_encoded = encoders['Code'].transform(['MUIS'])[0]
            
            X = pd.DataFrame([{
                "Line": line_encoded,
                "Station": station_encoded,
                "Code": code_encoded,
                "DayOfWeek": day_of_week
            }])
            
            probability = model.predict_proba(X)[0][1]
            total_risk += probability
            
            # Add time multiplier for transfers
            if i > 0 and i < len(stations) - 1:
                estimated_time += 5  # Transfer time
            else:
                estimated_time += 3  # Station time
                
        except Exception:
            # Default values if station not in training data
            total_risk += 0.15
            estimated_time += 3
    
    # Apply time preference multiplier
    if time_preference == "rush_hour":
        total_risk *= 1.5
        estimated_time *= 1.3
    elif time_preference == "off_peak":
        total_risk *= 0.8
        estimated_time *= 0.9
    
    return {
        "stations": stations,
        "total_delay_risk": total_risk / len(stations),  # Average risk
        "estimated_time": int(estimated_time)
    }

def find_transfer_stations(line1: str, line2: str) -> List[str]:
    """Find transfer stations between two lines"""
    transfer_map = {
        ("YU", "BD"): ["BLOOR-YONGE", "ST GEORGE"],
        ("BD", "YU"): ["BLOOR-YONGE", "ST GEORGE"],
        ("YU", "SRT"): ["KENNEDY"],
        ("SRT", "YU"): ["KENNEDY"],
        ("BD", "SRT"): ["KENNEDY"],
        ("SRT", "BD"): ["KENNEDY"]
    }
    
    return transfer_map.get((line1, line2), [])

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "encoders_loaded": encoders is not None
    }

@app.get("/stations")
def get_stations():
    """Get all available stations"""
    return {"stations": list(TTC_STATIONS.keys())}

@app.get("/lines")
def get_lines():
    """Get all available lines"""
    lines = list(set(station['line'] for station in TTC_STATIONS.values()))
    return {"lines": lines}
