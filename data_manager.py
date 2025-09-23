# data_manager.py
import json
import os
import streamlit as st

def get_data(key):
    data = {}
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            data = json.load(f)
    # Fallback to st.session_state if key is not found in data.json
    if key in ["sources", "interventions", "buildings", "sensors"]:
        return st.session_state.get(key, [])
    return data.get(key, {})

def save_scenario(name, sources, interventions, buildings, sensors):
    data = get_data("")
    data["scenarios"] = data.get("scenarios", {})
    data["scenarios"][name] = {
        "sources": sources,
        "interventions": interventions,
        "buildings": buildings,
        "sensors": sensors
    }
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

def load_scenario(name):
    data = get_data("scenarios")
    scenario = data.get(name, {})
    return (
        scenario.get("sources", []),
        scenario.get("interventions", []),
        scenario.get("buildings", []),
        scenario.get("sensors", [])
    )
