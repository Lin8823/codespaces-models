import streamlit as st
import requests
import traceback
import time

BACKEND_URL = "http://localhost:5001"

st.set_page_config(layout="wide")
st.title("🧘‍♀️ Smart Health Insights")
st.markdown("Select a user profile or enter your sensor data for analysis.")

user_roles = ["Software Engineer (Taipei)", "Hardware Engineer (Boston)", "Data Scientist (London)", "Custom Input"]
selected_role = st.selectbox("Choose a User Profile:", user_roles)

user_data = {}

if selected_role == "Software Engineer (Taipei)":
    user_data = {
        "activity": {"acceleration": [1.2, 0.5, -0.8], "time": "morning", "weight": 70, "duration": 20},
        "sleep": {"HR": 60, "HRV": 75, "TEMP": 36.5, "ACCELERATION": [0.1, 0.1, 0.1], "GSR": 2, "TIME": "early night"},
        "stress": {"HR": 75, "TEMP": 36.8, "EDA": 5, "ACCEL": [0.2, 0.2, 0.2]}
    }
elif selected_role == "Hardware Engineer (Boston)":
    user_data = {
        "activity": {"acceleration": [0.3, 0.2, 0.1], "time": "afternoon", "weight": 80, "duration": 45},
        "sleep": {"HR": 55, "HRV": 85, "TEMP": 36.3, "ACCELERATION": [0.05, 0.05, 0.05], "GSR": 1.5, "TIME": "late night"},
        "stress": {"HR": 65, "TEMP": 36.6, "EDA": 3, "ACCEL": [0.1, 0.1, 0.1]}
    }
elif selected_role == "Data Scientist (London)":
    user_data = {
        "activity": {"acceleration": [0.8, 0.6, -0.2], "time": "morning", "weight": 65, "duration": 30},
        "sleep": {"HR": 62, "HRV": 80, "TEMP": 36.4, "ACCELERATION": [0.08, 0.08, 0.08], "GSR": 1.8, "TIME": "early night"},
        "stress": {"HR": 70, "TEMP": 36.7, "EDA": 4, "ACCEL": [0.15, 0.15, 0.15]}
    }
elif selected_role == "Custom Input":
    with st.expander("Enter Custom Sensor Data"):
        user_data["activity"] = {
            "acceleration": [float(x.strip()) for x in st.text_input("Acceleration (e.g., 1.2, 0.5, -0.8)", value="1.2, 0.5, -0.8").split(',')],
            "time": st.selectbox("Activity Time", ["morning", "afternoon", "evening"], index=0),
            "weight": st.number_input("Weight (kg)", min_value=1.0, value=70.0),
            "duration": st.number_input("Activity Duration (minutes)", min_value=1, value=30)
        }
        user_data["sleep"] = {
            "HR": st.number_input("Heart Rate (bpm)", min_value=1, value=60),
            "HRV": st.number_input("HRV (ms)", min_value=1, value=80),
            "TEMP": st.number_input("Temperature (°C)", value=36.5),
            "ACCELERATION": [float(x.strip()) for x in st.text_input("Sleep Acceleration (e.g., 0.1, 0.1, 0.1)", value="0.1, 0.1, 0.1").split(',')],
            "GSR": st.number_input("GSR (µS)", value=2.0),
            "TIME": st.selectbox("Sleep Time", ["early night", "late night", "early morning"], index=0)
        }
        user_data["stress"] = {
            "HR": st.number_input("Stress HR (bpm)", min_value=1, value=70),
            "TEMP": st.number_input("Stress Temp (°C)", value=36.7),
            "EDA": st.number_input("EDA (µS)", value=4.0),
            "ACCEL": [float(x.strip()) for x in st.text_input("Stress Acceleration (e.g., 0.15, 0.15, 0.15)", value="0.15, 0.15, 0.15").split(',')]
        }


if st.button("Analyze Health Data"):
    if user_data:
        activity_result = None
        sleep_result = None
        stress_result = None

        with st.spinner("Analyzing Activity Data..."):
            try:
                response = requests.post(f"{BACKEND_URL}/analyze_activity", json=user_data.get("activity", {}), timeout=60)
                response.raise_for_status()
                activity_result = response.json().get("activity_analysis")
                st.success("Activity Analysis Complete!")
            except requests.exceptions.RequestException as e:
                st.error(f"Error analyzing activity: {e}")
                st.error(traceback.format_exc())

        with st.spinner("Analyzing Sleep Data..."):
            try:
                response = requests.post(f"{BACKEND_URL}/analyze_sleep", json=user_data.get("sleep", {}), timeout=60)
                response.raise_for_status()
                sleep_result = response.json().get("sleep_analysis")
                st.success("Sleep Analysis Complete!")
            except requests.exceptions.RequestException as e:
                st.error(f"Error analyzing sleep: {e}")
                st.error(traceback.format_exc())

        with st.spinner("Analyzing Stress Data..."):
            try:
                response = requests.post(f"{BACKEND_URL}/analyze_stress", json=user_data.get("stress", {}), timeout=60)
                response.raise_for_status()
                stress_result = response.json().get("stress_analysis")
                st.success("Stress Analysis Complete!")
            except requests.exceptions.RequestException as e:
                st.error(f"Error analyzing stress: {e}")
                st.error(traceback.format_exc())

        if activity_result and sleep_result and stress_result:
            with st.spinner("Detecting Anomalies..."):
                anomaly_payload = {
                    "stress_result": stress_result,
                    "sleep_result": sleep_result,
                    "activity_result": activity_result
                }
                try:
                    response = requests.post(f"{BACKEND_URL}/detect_anomaly", json=anomaly_payload, timeout=60)
                    response.raise_for_status()
                    anomaly_analysis = response.json().get("anomaly_analysis")
                    st.subheader("Anomaly Detection:")
                    st.markdown(anomaly_analysis)
                    st.success("Anomaly Detection Complete!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error detecting anomalies: {e}")
                    st.error(traceback.format_exc())

            with st.spinner("Generating Health Summary..."):
                summary_payload = {
                    "activity": user_data.get("activity", {}),
                    "sleep": user_data.get("sleep", {}),
                    "stress": user_data.get("stress", {})
                }
                try:
                    response = requests.post(f"{BACKEND_URL}/group_summary", json=summary_payload, timeout=60)
                    response.raise_for_status()
                    group_summary = response.json().get("group_health_summary")
                    st.subheader("Overall Health Summary & Recommendation:")
                    st.markdown(group_summary)
                    st.success("Health Summary Generated!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error generating health summary: {e}")
                    st.error(traceback.format_exc())

        if activity_result:
            st.subheader("Activity Analysis Result:")
            st.markdown(activity_result)
        if sleep_result:
            st.subheader("Sleep Analysis Result:")
            st.markdown(sleep_result)
        if stress_result:
            st.subheader("Stress Analysis Result:")
            st.markdown(stress_result)