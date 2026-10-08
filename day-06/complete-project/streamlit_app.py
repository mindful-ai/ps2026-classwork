import logging

import requests
import streamlit as st


logging.basicConfig(
    filename="frontend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


st.title("❤️ Heart Disease Prediction")
st.caption("FastAPI + Streamlit")


# Input fields
age = st.number_input("Age", min_value=20, max_value=100, value=50)
sex = st.selectbox("Sex (1=Male, 0=Female)", [0, 1])
cp = st.selectbox(
    "Chest Pain Type",
    [0, 1, 2, 3],
    help="0=typical, 1=asymptomatic, 2=nonanginal, 3=nontypical"
)
trestbps = st.number_input(
    "Resting Blood Pressure", min_value=80, max_value=200, value=120
)
chol = st.number_input(
    "Serum Cholesterol (mg/dl)", min_value=100, max_value=400, value=200
)
fbs = st.selectbox(
    "Fasting Blood Sugar > 120 mg/dl (1=True, 0=False)",
    [0, 1]
)
restecg = st.selectbox("Resting ECG", [0, 1, 2])
thalach = st.number_input(
    "Max Heart Rate Achieved", min_value=60, max_value=220, value=150
)
exang = st.selectbox("Exercise Induced Angina (1=Yes, 0=No)", [0, 1])
oldpeak = st.number_input(
    "ST Depression", min_value=0.0, max_value=10.0, value=1.0
)

# IMPORTANT: Dataset uses 1, 2, 3 for Slope
slope = st.selectbox(
    "Slope of ST Segment",
    [1, 2, 3],
    help="The training dataset uses values 1, 2, and 3."
)

ca = st.selectbox("Number of Major Vessels (0-3)", [0, 1, 2, 3])
thal = st.selectbox(
    "Thalassemia",
    [1, 2, 3],
    help="1=Normal, 2=Fixed, 3=Reversible"
)


if st.button("Predict", type="primary"):
    input_data = {
        "age": age,
        "sex": sex,
        "cp": cp,
        "trestbps": trestbps,
        "chol": chol,
        "fbs": fbs,
        "restecg": restecg,
        "thalach": thalach,
        "exang": exang,
        "oldpeak": oldpeak,
        "slope": slope,
        "ca": ca,
        "thal": thal
    }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/predict",
            json=input_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            prediction_text = (
                "Heart Disease Detected"
                if result["prediction"] == 1
                else "No Heart Disease"
            )

            st.success(
                f"{prediction_text} "
                f"(probability = {result['probability']:.2%})"
            )

            logging.info(
                "User input: %s -> Result: %s",
                input_data,
                result
            )

        else:
            st.error(f"API error ({response.status_code}): {response.text}")
            logging.error(
                "API Error %s: %s",
                response.status_code,
                response.text
            )

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to FastAPI server: {e}")
        logging.error("Request Error", exc_info=True)

    except Exception as e:
        st.error(f"Error: {e}")
        logging.error("Frontend Error", exc_info=True)
