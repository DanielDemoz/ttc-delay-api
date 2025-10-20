#!/usr/bin/env python3
"""
Simple deployment script for GitHub Pages
This script creates a static version of the web interface
"""

import os
import json
from pathlib import Path

def create_static_deployment():
    """Create static files for GitHub Pages deployment"""
    
    # Create static directory
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # Read the HTML from main.py
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract HTML content
    start_marker = 'return """'
    end_marker = '"""'
    
    start_idx = content.find(start_marker) + len(start_marker)
    end_idx = content.find(end_marker, start_idx)
    
    html_content = content[start_idx:end_idx]
    
    # Create index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Create a simple API mock for static deployment
    api_mock = """
    // Mock API for static deployment
    const API_BASE = 'https://your-api-url.herokuapp.com'; // Replace with actual API URL
    
    // Mock station predictions
    const mockStationPredictions = [
        {"name": "UNION STATION", "line": "YU", "lat": 43.6452, "lng": -79.3806, "delay_probability": 0.25},
        {"name": "BLOOR-YONGE", "line": "YU", "lat": 43.6706, "lng": -79.3856, "delay_probability": 0.18},
        {"name": "ST GEORGE", "line": "YU", "lat": 43.6684, "lng": -79.3997, "delay_probability": 0.22},
        {"name": "SPADINA", "line": "YU", "lat": 43.6674, "lng": -79.4047, "delay_probability": 0.15},
        {"name": "BAY", "line": "YU", "lat": 43.6706, "lng": -79.3856, "delay_probability": 0.12},
        {"name": "SHEPPARD-YONGE", "line": "YU", "lat": 43.7615, "lng": -79.4110, "delay_probability": 0.08},
        {"name": "FINCH", "line": "YU", "lat": 43.7805, "lng": -79.4147, "delay_probability": 0.06},
        {"name": "DOWNSVIEW", "line": "YU", "lat": 43.7225, "lng": -79.4778, "delay_probability": 0.10},
        {"name": "KIPLING", "line": "BD", "lat": 43.6372, "lng": -79.5356, "delay_probability": 0.14},
        {"name": "KENNEDY", "line": "BD", "lat": 43.7322, "lng": -79.2628, "delay_probability": 0.20},
        {"name": "DON MILLS", "line": "BD", "lat": 43.7615, "lng": -79.3328, "delay_probability": 0.16},
        {"name": "SCARBOROUGH CENTRE", "line": "SRT", "lat": 43.7731, "lng": -79.2578, "delay_probability": 0.13}
    ];
    
    // Override fetch for static deployment
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (url.includes('/stations/predictions')) {
            return Promise.resolve({
                json: () => Promise.resolve(mockStationPredictions)
            });
        }
        
        if (url.includes('/predict')) {
            // Mock prediction response
            const mockResponse = {
                "prediction": Math.random() > 0.7 ? 1 : 0,
                "probability": Math.random() * 0.4 + 0.1,
                "input": JSON.parse(options.body)
            };
            return Promise.resolve({
                json: () => Promise.resolve(mockResponse)
            });
        }
        
        if (url.includes('/route/optimize')) {
            // Mock route optimization response
            const mockResponse = {
                "routes": [
                    {
                        "stations": ["UNION STATION", "BLOOR-YONGE"],
                        "total_delay_risk": 0.15,
                        "estimated_time": 8
                    },
                    {
                        "stations": ["UNION STATION", "ST GEORGE", "BLOOR-YONGE"],
                        "total_delay_risk": 0.22,
                        "estimated_time": 12
                    }
                ]
            };
            return Promise.resolve({
                json: () => Promise.resolve(mockResponse)
            });
        }
        
        return originalFetch(url, options);
    };
    """
    
    # Add the mock API to the HTML
    html_with_mock = html_content.replace(
        '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>',
        f'<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>\n        <script>{api_mock}</script>'
    )
    
    # Write the final HTML
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_with_mock)
    
    print("Static deployment files created!")
    print("- index.html: Main web interface")
    print("- Ready for GitHub Pages deployment")

if __name__ == "__main__":
    create_static_deployment()
