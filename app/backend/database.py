import pandas as pd

import numpy as np
import pandas as pd
from datetime import datetime

HISTORICAL_DATA_PATH = "/workspaces/codespaces-models/app/backend/historical_data/"

def get_all_user_list():
    df_user = pd.read_csv(f"{HISTORICAL_DATA_PATH}/user_info.csv", sep=",")

    return list(df_user['name'])

def safe_json_encoder(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    else:
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
    
def get_user_id(name):
    df_user = pd.read_csv(f"{HISTORICAL_DATA_PATH}/user_info.csv", sep=",")
    user_id = df_user[df_user["name"] == name]["id"].iloc[0]

    return user_id


def get_historical_data(data_type, name):
    user_id = get_user_id(name)
    
    data = pd.read_csv(f"{HISTORICAL_DATA_PATH}/{data_type}.csv", sep=",")
    data = data[data["user_id"] == user_id]

    return data.to_json()


def combine_all_user_data(name):
    data_types = ["activity_data", "sleep_data", "stress_data"]

    user_data = {}

    for type in data_types:
        user_data[type] = get_historical_data(type, name)

    return user_data

def write_user(user_info):

    user_data_file_path = f"{HISTORICAL_DATA_PATH}/user_info.csv"

    df_user = pd.read_csv(user_data_file_path, sep=",")
    max_id = df_user["id"].max()

    user_info["id"] = int(max_id) + 1
    df_new_user = pd.DataFrame([user_info])

    df_user = pd.concat([df_user, df_new_user], axis =0)
    df_user.to_csv(user_data_file_path, index=False)
    

def write_activity_sleep_stress_data(name, data_type, new_user_data):
    data_file_path = f"{HISTORICAL_DATA_PATH}/{data_type}_data.csv"

    user_id = get_user_id(name)

    new_user_data["user_id"] = user_id
    data = pd.read_csv(data_file_path, sep=",")
    new_data = pd.DataFrame([new_user_data])

    data = pd.concat([data, new_data], axis = 0)

    data.to_csv(data_file_path, index=False)



def create_historical_data():

    df_activity = pd.DataFrame([user_data1["activity"], user_data2["activity"], user_data3["activity"]])
    df_sleep = pd.DataFrame([user_data1["sleep"], user_data2["sleep"], user_data3["sleep"]])
    df_stress = pd.DataFrame([user_data1["stress"], user_data2["stress"], user_data3["stress"]])
    df_user = pd.DataFrame(user_info)

    df_activity.to_csv(f"{HISTORICAL_DATA_PATH}/activity_data.csv", index=False)
    df_sleep.to_csv(f"{HISTORICAL_DATA_PATH}/sleep_data.csv", index=False)
    df_stress.to_csv(f"{HISTORICAL_DATA_PATH}/stress_data.csv", index=False)
    df_user.to_csv(f"{HISTORICAL_DATA_PATH}/user_info.csv", index=False)


if __name__ == '__main__':
    # historical data
    user_data1 = {
            "activity": {"user_id": 1,"acceleration":  [[2.0, 1.5, -9.8], [1.8, 2.0, -8.5], [2.2, 1.2, -10.1], [1.7, 2.3, -8.9], [2.1, 1.6, -9.7]], "time": "morning", "weight": 70, "duration": 20, "created_at": "2025-04-27 04:22:46.055296"},
            "sleep": {"user_id": 1,"heart_rate": 70, "hrv": 58, "skin_temperature": 36.5, "acceleration": [[0.001, -0.002, 0.998], [0.002, -0.001, 0.997], [0.000,  0.000, 1.000], [-0.001, 0.001, 0.999], [0.001, 0.000, 0.998]], "gsr": 1.2, "time_of_night": "2:30 AM", "created_at": "2025-04-27 04:22:46.055296"},
            "stress": {"user_id": 1,"heart_rate": 85, "skin_temperature": 37.2, "eda": 2.3, "acceleration": [[0.03, -0.02, 0.97], [0.04, -0.01, 0.96], [0.02,  0.00, 0.98], [0.01, -0.02, 0.99], [0.00,  0.01, 1.00]], "created_at": "2025-04-27 04:22:46.055296"},
        }

    user_data2 = {
            "user_id": 2,
            "activity": {"user_id": 2, "acceleration": [[2.0, 1.5, -9.8], [1.2, 2.0, -8.5], [2.2, 1.2, -10.1], [1.5, 2.3, -4.9], [2.1, 2.6, -10.1]], "time": "afternoon", "weight": 80, "duration": 45, "created_at": "2025-04-24 04:42:46.055296"},
            "sleep": {"user_id": 2, "heart_rate": 62, "hrv": 58, "skin_temperature": 36.5, "acceleration": [[0.001, -0.002, 0.998], [0.002, -0.001, 0.997], [0.000,  0.000, 1.000], [-0.001, 0.001, 0.999], [0.001, 0.000, 0.998]], "gsr": 1.2, "time_of_night": "11:30 PM", "created_at": "2025-04-24 04:42:46.055296"},
            "stress": {"user_id": 2, "heart_rate": 85, "skin_temperature": 37.2, "eda": 2.3, "acceleration": [[0.03, -0.02, 0.97], [0.04, -0.01, 0.96], [0.02,  0.00, 0.98], [0.01, -0.02, 0.99], [0.00,  0.01, 1.00]], "created_at": "2025-04-24 04:42:46.055296"},
        }
    user_data3 = {
            "user_id": 3,
            "activity": {"user_id": 3, "acceleration": [[0.05, 0.02, 0.98],  [0.08, -0.03, 1.00],  [4.8, -3.2, 2.0],     [-0.5, 0.4, -8.7],    [0.01, -0.02, 0.99]], "time": "2:20 PM", "weight": 70, "duration": 1, "created_at": "2025-04-25 02:30:50.055296"},
            "sleep": {"user_id": 3,"heart_rate": 70, "hrv": 60, "skin_temperature": 35, "acceleration": [[0.001, -0.002, 0.998], [0.002, -0.001, 0.997], [0.000,  0.000, 1.000], [-0.001, 0.001, 0.999], [0.001, 0.000, 0.998]], "gsr": 0.2, "time_of_night": "12:30 AM", "created_at": "2025-04-25 02:30:50.055296"},
            "stress": {"user_id": 3,"heart_rate": 85, "skin_temperature": 37.2, "eda": 2.3, "acceleration": [[0.03, -0.02, 0.97], [0.04, -0.01, 0.96], [0.02,  0.00, 0.98], [0.01, -0.02, 0.99], [0.00,  0.01, 1.00]], "created_at": "2025-04-25 02:30:50.055296"},
        }

    user_info = [
        {
            "id": 1,
            "name": "Jack",
            "Job":"Software Engineer",
            "age": 32,
            "gender": "male",
            "height": 180,
            "weight": 75,
            "activity_level": "moderate",
            "disease_history": [
                "diabetes",
                "heart_disease"
            ],
            "location": "Taipei"
        },
        {
            "id": 2,
            "name": "Joe",
            "Job": "Hardware Engineer",
            "age": 73,
            "gender": "male",
            "height": 178,
            "weight": 66,
            "activity_level": "low",
            "disease_history": [
                "lung cancer"
            ],
            "location": "Boston"
        },
        {
            "id": 3,
            "name": "Emily",
            "Job": "Data Scientist",
            "age": 45,
            "gender": "female",
            "height": 170,
            "weight": 60,
            "activity_level": "high",
            "disease_history": [
                "hypertension"
            ],
            "location": "London"
        }
    ]

    create_historical_data()