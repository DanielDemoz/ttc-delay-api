#!/usr/bin/env python3
"""
Simple model training script for TTC Delay Prediction
This script creates a basic model when the full training data is not available
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import os

def create_sample_data():
    """Create sample training data based on TTC patterns"""
    
    # Sample stations and lines
    stations = [
        "UNION STATION", "BLOOR-YONGE", "ST GEORGE", "SPADINA", "BAY",
        "SHEPPARD-YONGE", "FINCH", "DOWNSVIEW", "KIPLING", "KENNEDY",
        "DON MILLS", "SCARBOROUGH CENTRE"
    ]
    
    lines = ["YU", "BD", "SRT"]
    
    codes = ["MUIS", "SEC", "SIG", "PAS", "TRA", "OPE", "MED", "INV"]
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    
    data = []
    for _ in range(n_samples):
        station = np.random.choice(stations)
        line = np.random.choice(lines)
        code = np.random.choice(codes)
        day_of_week = np.random.randint(0, 7)
        
        # Create realistic delay patterns
        base_delay_prob = 0.1
        
        # Higher delays for certain stations
        if station in ["UNION STATION", "BLOOR-YONGE", "ST GEORGE"]:
            base_delay_prob += 0.1
            
        # Higher delays for certain codes
        if code in ["MUIS", "SIG", "TRA"]:
            base_delay_prob += 0.15
            
        # Higher delays on weekdays
        if day_of_week < 5:
            base_delay_prob += 0.05
            
        # Generate delay outcome
        major_delay = np.random.random() < base_delay_prob
        
        data.append({
            'Line': line,
            'Station': station,
            'Code': code,
            'DayOfWeek': day_of_week,
            'MajorDelay': int(major_delay)
        })
    
    return pd.DataFrame(data)

def train_model():
    """Train the Random Forest model"""
    
    print("Creating sample training data...")
    df = create_sample_data()
    
    print("Preparing features...")
    # Select features
    features = ['Line', 'Station', 'Code', 'DayOfWeek']
    X = df[features].copy()
    y = df['MajorDelay']
    
    # Encode categorical variables
    encoders = {}
    for col in ['Line', 'Station', 'Code']:
        encoders[col] = LabelEncoder()
        X[col] = encoders[col].fit_transform(X[col].astype(str))
    
    print("Training Random Forest model...")
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    print("Saving model and encoders...")
    # Save model
    with open("random_forest_model_new_task.pkl", "wb") as f:
        pickle.dump(model, f)
    
    # Save encoders
    with open("label_encoders_new_task.pkl", "wb") as f:
        pickle.dump(encoders, f)
    
    print("Model training complete!")
    print(f"Model saved to: random_forest_model_new_task.pkl")
    print(f"Encoders saved to: label_encoders_new_task.pkl")
    
    # Print some statistics
    print(f"\nTraining data shape: {X.shape}")
    print(f"Major delay rate: {y.mean():.2%}")
    print(f"Feature importance:")
    for feature, importance in zip(features, model.feature_importances_):
        print(f"  {feature}: {importance:.3f}")

if __name__ == "__main__":
    train_model()
