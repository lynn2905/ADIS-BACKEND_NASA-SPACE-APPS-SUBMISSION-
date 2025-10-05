# backend/api.py
from flask import Flask, jsonify
import pandas as pd
import json
import os
import backend.config as config


app = Flask(__name__)

@app.route("/api/data")
def get_data():
    """Return fused anomaly + signature dataset."""
    if not os.path.exists(config.DATA_PATH):
        return jsonify({"error": "Fused data not found"}), 404
    with open(config.DATA_PATH, "r") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/predict")
def predict():
    """Placeholder for plume prediction (calls plume.py later)."""
    from plume import simulate_plume
    results = simulate_plume()
    return jsonify(results)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=True)
