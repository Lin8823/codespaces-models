# backend/app.py

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from backend.agents import setup_agents
from backend.group_summary_chat import run_group_health_chat
from core.activity_agent import run_activity_agent
from core.sleep_agent import run_sleep_agent
from agents_CHIA import run_nutrition_agents, run_atvacc_agent
# Load environment variables
load_dotenv()

# Define OpenAI / AutoGen LLM config
llm_config = {
    "config_list": [{
        "model": os.getenv("OPENAI_API_MODEL", "gpt-4o"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        "api_type": "openai"
    }],
    "timeout": 120,
    "max_tokens": 2000
}

# Set up Flask app
app = Flask(__name__)

# Setup agents once at launch
agents = setup_agents(llm_config)


@app.route('/analyze_activity', methods=['POST'])
def analyze_activity_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    try:
        result = agents["activity_agent"](data, agents["user_proxy"], agents["activity_llm"])
        return jsonify({"activity_analysis": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze_sleep', methods=['POST'])
def analyze_sleep_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    try:
        result = agents["sleep_agent"](data, agents["user_proxy"], agents["sleep_llm"])
        print({"sleep_analysis": result})
        return jsonify({"sleep_analysis": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze_stress', methods=['POST'])
def analyze_stress_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    try:
        result = agents["stress_agent"](data, agents["user_proxy"], agents["stress_llm"])
        return jsonify({"stress_analysis": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/detect_anomaly', methods=['POST'])
def detect_anomaly_route():
    data = request.get_json()
    required_keys = ["stress_result", "sleep_result", "activity_result"]
    if not all(k in data for k in required_keys):
        return jsonify({"error": f"Missing one or more required fields: {required_keys}"}), 400
    try:
        result = agents["abnormaly_detection_agent"](
            data["stress_result"],
            data["sleep_result"],
            data["activity_result"],
            agents["user_proxy"],
            agents["abnormaly_detection_llm"]
        )
        return jsonify({"anomaly_analysis": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze_nutrition', methods=['POST'])
def analyze_nutrition_route():
    try:
        data = request.get_json()
        result = agents["nutrition_agent"](data, agents["user_proxy"], agents["nutrition_llm"])
        return jsonify({"nutrition_analysis": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# backend/app.py (只列出 group_summary 部分)

@app.route('/group_summary_chat', methods=['POST'])
def group_health_chat():
    try:
        data = request.get_json()

        # 取出 activity, sleep, stress data
        activity_data = data.get('activity_data')
        sleep_data = data.get('sleep_data')
        stress_data = data.get('stress_data')

        # 執行 Group Health Chat
        results = run_group_health_chat(
            activity_data=activity_data,
            sleep_data=sleep_data,
            stress_data=stress_data,
            llm_config=llm_config
        )

        return jsonify({
            "status": "success",
            "results": results
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/nutrition_management', methods=['POST'])
def nutrition_agent():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_nutrition_agents()) 
        return jsonify({
            "status": "success",
            "results": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/activity_accessment', methods=['POST'])
def atv_agent():
    try:
        data = request.get_json()
        if not data or "selected_meal" not in data:
            return jsonify({"error": "Missing 'selected_meal' in request"}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_atvacc_agent(data)) 
        return jsonify({
            "status": "success",
            "results": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# Main server startup
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
