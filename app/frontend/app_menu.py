from datetime import datetime
import json
import os
import sys
import traceback
import requests
import streamlit as st

import app_func

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from database import safe_json_encoder, write_user, write_activity_sleep_stress_data, get_all_user_list

BACKEND_URL = "http://localhost:5001"

st.set_page_config(layout="wide")
st.title("🧘‍♀️ Smart Health Insights")
st.markdown("Select a user profile or enter your sensor data for analysis.")

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