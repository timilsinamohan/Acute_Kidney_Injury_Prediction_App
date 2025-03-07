from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# Load the trained model and default values
model = joblib.load('Model/aki_prediction_model.pkl')
default_values = joblib.load('Model/default_values.pkl')

# Extract feature names from the trained model
feature_names = model.feature_names_in_

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    #  Get the data from the POST request
    user_input = request.form.to_dict()
    print("\Received user input:", user_input)  # Debugging step

    #  Standardize input feature names
    standardized_input = {}
    for key, value in user_input.items():
        formatted_key = key.upper().replace("_", " ")  # Convert to uppercase & replace underscores
        standardized_input[formatted_key] = float(value)  # Convert value to float

    print(" Standardized input keys:", standardized_input.keys())

    #  **Create a full feature dictionary with default values**
    input_data = default_values.copy()  # Start with default values
    input_data.update(standardized_input)  # Override with user-provided values

    # Ensure all expected features exist (avoid KeyError)
    missing_cols = set(feature_names) - set(input_data.keys())
    if missing_cols:
        print(f"Adding missing columns from default values: {missing_cols}")
        for col in missing_cols:
            input_data[col] = default_values.get(col, 0)  # Set to 0 if missing

    # Convert to DataFrame
    input_df = pd.DataFrame([input_data])

    #  **Ensure correct feature order** before passing to the model
    input_df = input_df[feature_names]
    print("Final input DataFrame columns:", input_df.columns.tolist())

    #  Apply the same preprocessing steps used during training
    input_processed = model.named_steps['preprocessor'].transform(input_df)

    #  **Make prediction**
    prediction = model.named_steps['classifier'].predict(input_processed)
    probability = model.named_steps['classifier'].predict_proba(input_processed)[0][1]  # AKI probability

    print(f"\n Prediction: {prediction[0]} | Probability: {probability:.2%}")  # Debugging output

    # **Return JSON response**
    return jsonify({
        'prediction': int(prediction[0]),
        'probability': round(probability * 100, 2)  # Convert probability to percentage
    })

if __name__ == '__main__':
    # Use the PORT environment variable if available, else default to 5000
    port = int(os.environ.get("PORT", 5001))
    
    # Disable debug mode inside Docker (prevents permission error)
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"

    app.run(host="0.0.0.0", port=port, debug=debug_mode)