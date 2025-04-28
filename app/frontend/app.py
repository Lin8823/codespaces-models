import streamlit as st
import requests
import traceback
from datetime import datetime
import json

import sys
import os

import app_func

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from database import safe_json_encoder, write_user, write_activity_sleep_stress_data, get_all_user_list

BACKEND_URL = "http://localhost:5001"

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a Page", ("Home", "Health Analysis", "Nutrition"))

if page == "Home":
    st.title("🧘‍♀️ Smart Health Insights")
    st.markdown("This is a Nutrition Health Analysis, please select a sidebar and start to analyze")

elif page == "Health Analysis":
    st.title("🏥 Health Analysis")
    st.markdown("""
    On this page, you can input user sensor data, including activity, sleep, and stress information.
    The system will automatically analyze the user's health status and provide personalized suggestions.
    """)

    default_users = get_all_user_list()
    user_names = default_users + ["New User"]
    selected_default_user_name = st.selectbox("Choose a User Profile:", user_names)

    user_data = {}

    if selected_default_user_name == "New User":
        with st.expander("Enter User Info"):
            st.subheader("Basic User Information")
            user_info = {
                "name": st.text_input("Name"),
                "gender": st.selectbox("Gender", ["Male", "Famale", "Prefer Not to Say"], index=0),
                "age": st.number_input("Age", min_value=1, max_value=110),
                "weight": st.number_input("Weight (kg)", min_value=1, max_value=70),
                "height": st.number_input("Height (cm)", min_value=10, max_value=240),
                "job": st.text_input("Job"),
                "activity_level":st.selectbox("activity_level", ["High", "Moderate", "Low"], index=0),
                "disease_history": st.text_input("disease_history"),
                "location": st.text_input("Location"),
            }
            if st.button("Submit User Info"):
                print("user_info", user_info)
                # create new user data
                write_user(user_info)
                st.success("✅ User info saved successfully!")
            
    with st.expander("Enter Sensor Data"):
        st.subheader("Activity Data")
        user_data["activity"] = {
            "acceleration": st.text_input("Activity Acceleration (e.g., 0.1, 0.1, 0.1)", value='[[2.0, 1.5, -9.8], [1.8, 2.0, -8.5], [2.2, 1.2, -10.1], [1.7, 2.3, -8.9], [2.1, 1.6, -9.7]]'),
            "time": st.selectbox("Activity Time", ["morning", "afternoon", "evening"], index=0),
            "weight": st.number_input("Weight (kg)", min_value=1.0, value=70.0),
            "duration": st.number_input("Activity Duration (minutes)", min_value=1, value=30),
            "created_at": str(datetime.now())
        }
        st.subheader("Sleep Data")
        user_data["sleep"] = {
            "heart_rate": st.number_input("Heart Rate (bpm)", min_value=1, value=60),
            "hrv": st.number_input("HRV (ms)", min_value=1, value=80),
            "skin_temperature": st.number_input("Temperature (°C)", value=36.5),
            "acceleration": st.text_input("Sleep Acceleration (e.g., 0.1, 0.1, 0.1)", value='[[2.0, 1.5, -9.8], [1.8, 2.0, -8.5], [2.2, 1.2, -10.1], [1.7, 2.3, -8.9], [2.1, 1.6, -9.7]]'),
            "gsr": st.number_input("GSR (µS)", value=2.0),
            "time_of_nith": st.selectbox("Sleep Time", ["early night", "late night", "early morning"], index=0),
            "created_at": str(datetime.now())
        }
        st.subheader("Stress Data")
        user_data["stress"] = {
            "heart_rate": st.number_input("Stress HR (bpm)", min_value=1, value=70),
            "skin_temperature": st.number_input("Stress Temp (°C)", value=36.7),
            "eda": st.number_input("EDA (µS)", value=4.0),
            "acceleration": st.text_input("Stress Acceleration (e.g., 0.1, 0.1, 0.1)", value='[[2.0, 1.5, -9.8], [1.8, 2.0, -8.5], [2.2, 1.2, -10.1], [1.7, 2.3, -8.9], [2.1, 1.6, -9.7]]'),
            "created_at": str(datetime.now())
        }
            


    if st.button("Analyze Health Data"):
        if user_data:

            # write new sleep, stress and activity data
            for data_type in ["sleep", "stress", "activity"]:
                print("selected_default_user_name", selected_default_user_name)
                write_activity_sleep_stress_data(name=selected_default_user_name, data_type=data_type, new_user_data=user_data[data_type])

            activity_result = None
            sleep_result = None
            stress_result = None

            with st.spinner("Analyzing Activity Data..."):
                try:
                    json_data = json.loads(json.dumps(user_data.get("activity", {}), default=safe_json_encoder))
                    response = requests.post(
                        f"{BACKEND_URL}/analyze_activity", json=json_data, timeout=60)
                    response.raise_for_status()
                    activity_result = response.json().get("activity_analysis")
                    st.success("Activity Analysis Complete!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error analyzing activity: {e}")
                    st.error(traceback.format_exc())

            with st.spinner("Analyzing Sleep Data..."):
                try:
                    json_data = json.loads(json.dumps(user_data.get("sleep", {}), default=safe_json_encoder))
                    response = requests.post(
                        f"{BACKEND_URL}/analyze_sleep", json=json_data, timeout=60)
                    response.raise_for_status()
                    sleep_result = response.json().get("sleep_analysis")
                    st.success("Sleep Analysis Complete!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error analyzing sleep: {e}")
                    st.error(traceback.format_exc())

            with st.spinner("Analyzing Stress Data..."):
                try:
                    json_data = json.loads(json.dumps(user_data.get("stress", {}), default=safe_json_encoder))
                    response = requests.post(
                        f"{BACKEND_URL}/analyze_stress", json=json_data, timeout=60)
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
                        response = requests.post(
                            f"{BACKEND_URL}/detect_anomaly", json=anomaly_payload, timeout=60)
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
                        "activity_data": json.loads(json.dumps(user_data.get("activity", {}), default=safe_json_encoder)),
                        "sleep_data": json.loads(json.dumps(user_data.get("sleep", {}), default=safe_json_encoder)),
                        "stress_data": json.loads(json.dumps(user_data.get("stress", {}), default=safe_json_encoder))
                    }

                    try:

                        response = requests.post(
                            f"{BACKEND_URL}/group_summary_chat", json=summary_payload, timeout=60)
                        response.raise_for_status()
                        group_summary = response.json().get("results").get("health_summary_result")
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

elif page == "Nutrition":
    st.title("🍎 Nutrition Management")
    st.markdown("""
    Here, you can generate personalized nutrition menus based on your physical condition and goals,
    helping you achieve better health and wellness through tailored dietary plans.
    """)
    if "menu_options" not in st.session_state:
        st.session_state.menu_options = []
    def fetch_menu():
        """
        POST /nutrition_management returns a new menu list.
        """
        try:
            response = requests.post(f"{BACKEND_URL}/nutrition_management", timeout=60)
            response.raise_for_status()
            return response.json().get("results", {})
        except requests.exceptions.RequestException as e:
            st.error(f"Error Fetching Menu: {e}")
            st.error(traceback.format_exc())
            return []

    def render_all_menus():
        """
        渲染所有已保存的菜單
        """
        for idx, menu_options in enumerate(st.session_state.menu_options, start=1):
            app_func.render_menu(menu_options)

    if st.button("Generate New Menu"):
        with st.spinner("Fetching a new menu..."):
            new_menu = fetch_menu()
            app_func.draw_consumption_intake_chart()
            app_func.draw_sleep_chart()
            if new_menu:
                st.session_state.menu_options.append(new_menu)

    render_all_menus()