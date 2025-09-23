# app.py
import streamlit as st
from streamlit_folium import st_folium
from visualizations import plot_3d_co2, plot_2d_slice, plot_time_series, create_folium_map
from data_manager import get_data, save_scenario, load_scenario
from simulation import run_simulation
from utils import validate_inputs
import time
import numpy as np
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def generate_report():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("CO2 Digital Twin Report", styles['Heading1']))
    elements.append(Spacer(1, 12))

    # Simulation Results
    elements.append(Paragraph("Simulation Results", styles['Heading2']))
    sim_results = st.session_state.get("simulation_results", {})
    data = [
        ["Metric", "Value"],
        ["CO2 Reduction", f"{sim_results.get('co2_reduction', 'N/A')}%"],
        ["Avg CO2", f"{sim_results.get('avg_co2', 'N/A')} ppm"],
        ["AQI", str(sim_results.get('aqi', 'N/A'))],
        ["Total Cost", f"${sim_results.get('total_cost', 'N/A')}"],
    ]
    table = Table(data)
    table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
    ])
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Sources
    elements.append(Paragraph("Sources", styles['Heading2']))
    if st.session_state.get("sources"):
        source_data = [["Type", "X", "Y", "Z", "Emission Rate (kg/h)", "Intensity", "Active Hours"]]
        for source in st.session_state.sources:
            source_data.append([
                source["type"],
                str(source["x"]),
                str(source["y"]),
                str(source["z"]),
                str(source["emission_rate"]),
                str(source["intensity"]),
                source["active_hours"]
            ])
        table = Table(source_data)
        table.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
        ])
        elements.append(table)
    else:
        elements.append(Paragraph("No sources added.", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Interventions
    elements.append(Paragraph("Interventions", styles['Heading2']))
    if st.session_state.get("interventions"):
        int_data = [["Type", "X", "Y", "Z", "Efficiency", "Radius", "Cost (USD)", "Capacity (kg/h)"]]
        for intv in st.session_state.interventions:
            int_data.append([
                intv["type"],
                str(intv["x"]),
                str(intv["y"]),
                str(intv["z"]),
                str(intv["efficiency"]),
                str(intv["radius"]),
                str(intv["cost"]),
                str(intv["capacity"])
            ])
        table = Table(int_data)
        table.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
        ])
        elements.append(table)
    else:
        elements.append(Paragraph("No interventions added.", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Buildings
    elements.append(Paragraph("Buildings", styles['Heading2']))
    if st.session_state.get("buildings"):
        bld_data = [["X Min", "X Max", "Y Min", "Y Max", "Z Min", "Z Max", "Material"]]
        for bld in st.session_state.buildings:
            bld_data.append([
                str(bld["x_min"]),
                str(bld["x_max"]),
                str(bld["y_min"]),
                str(bld["y_max"]),
                str(bld["z_min"]),
                str(bld["z_max"]),
                bld["material"]
            ])
        table = Table(bld_data)
        table.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
        ])
        elements.append(table)
    else:
        elements.append(Paragraph("No buildings added.", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Sensors
    elements.append(Paragraph("Sensors", styles['Heading2']))
    if st.session_state.get("sensors"):
        sensor_data = [["X", "Y", "Z", "CO2 Reading (ppm)"]]
        for sensor in st.session_state.sensors:
            sensor_data.append([
                str(sensor["x"]),
                str(sensor["y"]),
                str(sensor["z"]),
                str(sensor["co2_reading"])
            ])
        table = Table(sensor_data)
        table.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
        ])
        elements.append(table)
    else:
        elements.append(Paragraph("No sensors added.", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Map Configuration
    elements.append(Paragraph("Map Configuration", styles['Heading2']))
    map_config = [
        ["Center Latitude", str(st.session_state.get("lat", 51.505))],
        ["Center Longitude", str(st.session_state.get("lon", -0.09))],
        ["Map Style", st.session_state.get("map_style_single", "OpenStreetMap")],
        ["Layers", ", ".join(st.session_state.get("layer_toggles_single", []))],
        ["Zoom", str(st.session_state.get("map_zoom_single", 13))]
    ]
    table = Table(map_config)
    table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
    ])
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)  # Reset buffer position to the beginning
    return buffer

def main():
    st.set_page_config(layout="wide")
    st.title("CO2 Digital Twin for Urban Settings")

    # Initialize session state defaults
    if "map_style_single" not in st.session_state:
        st.session_state.map_style_single = "OpenStreetMap"
    if "layer_toggles_single" not in st.session_state:
        st.session_state.layer_toggles_single = []
    if "map_zoom_single" not in st.session_state:
        st.session_state.map_zoom_single = 13
    if "map_style_compare" not in st.session_state:
        st.session_state.map_style_compare = "OpenStreetMap"
    if "layer_toggles_compare" not in st.session_state:
        st.session_state.layer_toggles_compare = []
    if "map_zoom_compare" not in st.session_state:
        st.session_state.map_zoom_compare = 13
    if "wind_direction" not in st.session_state:
        st.session_state.wind_direction = 0  # Default value
    if "sources" not in st.session_state:
        st.session_state.sources = []
    if "interventions" not in st.session_state:
        st.session_state.interventions = []
    if "buildings" not in st.session_state:
        st.session_state.buildings = []
    if "sensors" not in st.session_state:
        st.session_state.sensors = []
    if "real_time_sensors" not in st.session_state:
        st.session_state.real_time_sensors = False
    if "last_update" not in st.session_state:
        st.session_state.last_update = time.time()

    with st.sidebar:
        st.header("Inputs and Results")
        with st.expander("Add Source", expanded=True):
            source_type = st.selectbox("Type", ["traffic", "industry", "household"], key="source_type")
            source_x = st.slider("X", 0, 50, 25, key="source_x")
            source_y = st.slider("Y", 0, 50, 25, key="source_y")
            source_z = st.slider("Z", 0, 20, 0, key="source_z")
            emission_rate = st.number_input("Emission Rate (kg/hour)", 0.0, 100.0, 10.0, key="emission_rate")
            intensity = st.number_input("Intensity", 0.5, 2.0, 1.0, key="intensity")
            active_hours = st.text_input("Active Hours", "08:00-18:00", key="active_hours")
            if st.button("Add Source", key="add_source"):
                if validate_inputs({"emission_rate": emission_rate, "intensity": intensity, "active_hours": active_hours}):
                    st.session_state.sources.append({
                        "type": source_type, "x": source_x, "y": source_y, "z": source_z,
                        "emission_rate": emission_rate, "intensity": intensity, "active_hours": active_hours
                    })
                else:
                    st.error("Invalid source inputs")

        with st.expander("Add Intervention"):
            intervention_type = st.selectbox("Type", ["vertical_garden", "roadside_unit", "biofilter"], key="intervention_type")
            int_x = st.slider("X", 0, 50, 25, key="int_x")
            int_y = st.slider("Y", 0, 50, 25, key="int_y")
            int_z = st.slider("Z", 0, 20, 0, key="int_z")
            efficiency = st.number_input("Efficiency", 0.0, 1.0, 0.5, key="efficiency")
            radius = st.number_input("Radius", 1, 20, 5, key="radius")
            cost = st.number_input("Cost (USD)", 1000, 100000, 5000, key="cost")
            capacity = st.number_input("Capacity (kg/hour)", 10, 100, 50, key="capacity")
            if st.button("Add Intervention", key="add_intervention"):
                if validate_inputs({"efficiency": efficiency, "radius": radius, "cost": cost, "capacity": capacity}):
                    st.session_state.interventions.append({
                        "type": intervention_type, "x": int_x, "y": int_y, "z": int_z,
                        "efficiency": efficiency, "radius": radius, "cost": cost, "capacity": capacity
                    })
                else:
                    st.error("Invalid intervention inputs")

        with st.expander("Add Building"):
            x_min = st.number_input("X_min", 0, 50, 10, key="x_min")
            x_max = st.number_input("X_max", 0, 50, 20, key="x_max")
            y_min = st.number_input("Y_min", 0, 50, 10, key="y_min")
            y_max = st.number_input("Y_max", 0, 50, 20, key="y_max")
            z_min = st.number_input("Z_min", 0, 20, 0, key="z_min")
            z_max = st.number_input("Z_max", 0, 20, 10, key="z_max")
            material = st.selectbox("Material", ["concrete", "glass"], key="material")
            if st.button("Add Building", key="add_building"):
                if validate_inputs({"x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max, "z_min": z_min, "z_max": z_max}):
                    st.session_state.buildings.append({
                        "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max, "z_min": z_min, "z_max": z_max, "material": material
                    })
                else:
                    st.error("Invalid building coordinates")

        with st.expander("Add Sensor"):
            sensor_x = st.slider("X", 0, 50, 10, key="sensor_x")
            sensor_y = st.slider("Y", 0, 50, 10, key="sensor_y")
            sensor_z = st.slider("Z", 0, 20, 0, key="sensor_z")
            co2_reading = st.number_input("Initial CO2 Reading (ppm)", 0.0, 1000.0, 400.0, key="co2_reading")
            if st.button("Add Sensor", key="add_sensor"):
                if validate_inputs({"co2_reading": co2_reading}):
                    st.session_state.sensors.append({
                        "x": sensor_x, "y": sensor_y, "z": sensor_z, "co2_reading": co2_reading
                    })
                else:
                    st.error("Invalid sensor inputs")

        with st.expander("Scenario Save/Load"):
            scenario_name = st.text_input("Scenario Name", key="scenario_name")
            if st.button("Save Scenario", key="save_scenario"):
                save_scenario(scenario_name, st.session_state.sources, st.session_state.interventions, st.session_state.buildings, st.session_state.sensors)
            scenario_load = st.selectbox("Load Scenario", ["None"] + list(get_data("scenarios").keys()), key="scenario_load")
            if scenario_load != "None":
                sources, interventions, buildings, sensors = load_scenario(scenario_load)
                st.session_state.sources = sources
                st.session_state.interventions = interventions
                st.session_state.buildings = buildings
                st.session_state.sensors = sensors

        with st.expander("Simulation Settings"):
            use_api = st.checkbox("Use OpenWeatherAPI for wind", key="use_api")
            if use_api:
                lat = st.number_input("Latitude", -90.0, 90.0, 51.5074, key="lat")  # Default to London
                lon = st.number_input("Longitude", -180.0, 180.0, -0.1278, key="lon")  # Default to London
                API_KEY = "ec52b92664ef5988db67e0d82924a12a"  # Replace with your API key
                url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    wind_speed = data["wind"]["speed"]  # m/s
                    wind_direction = data["wind"]["deg"]  # degrees
                    st.write(f"Live Weather: Wind Speed = {wind_speed} m/s, Wind Direction = {wind_direction}°")
                else:
                    st.error("Failed to fetch weather data. Using defaults.")
                    wind_speed = 5.0
                    wind_direction = 0
            else:
                wind_speed = st.number_input("Wind Speed (m/s)", 0.0, 50.0, 5.0, key="wind_speed")
                wind_direction = st.number_input("Wind Direction (degrees)", 0, 360, 0, key="wind_direction")
            time_steps = st.number_input("Time Steps", 1, 24, 24, key="time_steps")
            if st.button("Run Simulation", key="run_simulation"):
                if validate_inputs({"wind_speed": wind_speed, "wind_direction": wind_direction, "time_steps": time_steps}):
                    st.session_state.simulation_results = run_simulation(
                        st.session_state.sources, st.session_state.interventions, st.session_state.buildings,
                        wind_speed, wind_direction, time_steps, use_api
                    )
                    st.write("Debug: Simulation results updated:", st.session_state.simulation_results)
                else:
                    st.error("Invalid simulation settings")

        st.header("Simulation Results")
        if "simulation_results" in st.session_state and all(key in st.session_state.simulation_results for key in ["co2_reduction", "avg_co2", "aqi", "total_cost"]):
            st.metric("CO2 Reduction", f"{st.session_state.simulation_results['co2_reduction']}%")
            st.metric("Avg CO2", f"{st.session_state.simulation_results['avg_co2']} ppm")
            st.metric("AQI", st.session_state.simulation_results['aqi'])
            st.metric("Total Cost", f"${st.session_state.simulation_results['total_cost']}")
        else:
            st.write("Debug: No valid simulation results:", st.session_state.get("simulation_results", "Not available"))

        st.header("Real-Time Settings")
        st.session_state.real_time_sensors = st.checkbox("Enable Real-Time Sensor Updates", value=st.session_state.real_time_sensors, key="real_time_toggle")
        if st.session_state.real_time_sensors and time.time() - st.session_state.last_update >= 5:
            if st.session_state.get("sensors"):
                for sensor in st.session_state.sensors:
                    sensor["co2_reading"] = np.random.uniform(350, 600)  # Simulate real-time data
            st.session_state.last_update = time.time()

        st.header("Export")
        if st.button("Download Report", key="download_report"):
            buffer = generate_report()
            st.download_button(
                label="Download PDF Report",
                data=buffer.getvalue(),
                file_name="co2_digital_twin_report.pdf",
                mime="application/pdf"
            )

    tab1, tab2 = st.tabs(["Simulation", "Data"])

    with tab1:
        st.header("Simulation")
        time_steps = st.session_state.get('time_steps', 24)  # Ensure time_steps is defined
        time_step = st.slider("Time Step", 1, time_steps, 1, key="time_step")
        # Convert co2_grid string to NumPy array if it exists
        sim_results = st.session_state.simulation_results
        if isinstance(sim_results.get("co2_grid"), str):
            import ast
            try:
                array_str = sim_results["co2_grid"].split("array(")[1].split(", shape=")[0].strip(")")
                sim_results["co2_grid"] = np.array(ast.literal_eval(array_str))
                st.write("Debug: co2_grid converted successfully:", sim_results["co2_grid"].shape)
            except Exception as e:
                st.write("Debug: co2_grid conversion failed:", str(e))
        st.write("Simulation Results:", sim_results)
        animation_placeholder = st.empty()
        if st.button("Play Animation", key="play_animation"):
            for t in range(1, time_steps + 1):
                with animation_placeholder.container():
                    st.write(f"Animating time step {t}/{time_steps}")
                    st.plotly_chart(plot_3d_co2(sim_results, t), key=f"3d_plot_anim_{t}")
                    st.plotly_chart(plot_2d_slice(sim_results, st.slider("Z Slice", 0, 20, 0, key=f"z_slice_anim_{t}"), t), key=f"2d_slice_anim_{t}")
                    st.plotly_chart(plot_time_series(sim_results), key=f"time_series_anim_{t}")
                    st_folium(create_folium_map(sim_results, t, st.session_state.map_style_single, st.session_state.layer_toggles_single, st.session_state.map_zoom_single), width=700, key=f"folium_map_anim_{t}")
                    time.sleep(0.5)
        compare_run = st.selectbox("Compare Simulation", ["None"] + list(st.session_state.simulations.keys()), key="compare_run")
        if compare_run != "None":
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_3d_co2(sim_results, time_step), key="3d_plot_compare")
                st.plotly_chart(plot_2d_slice(sim_results, st.slider("Z Slice", 0, 20, 0, key="z_slice_compare"), time_step), key="2d_slice_compare")
                st.plotly_chart(plot_time_series(sim_results), key="time_series_compare")
                st_folium(create_folium_map(sim_results, time_step, st.session_state.map_style_compare, st.session_state.layer_toggles_compare, st.session_state.map_zoom_compare), width=700, key="folium_map_compare")
                map_style = st.selectbox("Map Style", ["OpenStreetMap", "Stamen Terrain", "CartoDB Positron"], key="map_style_compare")
                layer_toggles = st.multiselect("Map Layers", ["CO2 Heatmap", "Sources", "Interventions", "Buildings", "Sensors", "Wind Direction"], key="layer_toggles_compare")
                zoom = st.slider("Map Zoom", 10, 18, 13, key="map_zoom_compare")
                st.write("Wind Direction: Arrow overlay")
                st.write(f"Suggested Location: {sim_results.get('optimal_location', 'N/A')}")
            with col2:
                st.write("Comparison plots/maps placeholder")
        else:
            st.plotly_chart(plot_3d_co2(sim_results, time_step), key="3d_plot_single")
            st.plotly_chart(plot_2d_slice(sim_results, st.slider("Z Slice", 0, 20, 0, key="z_slice_single"), time_step), key="2d_slice_single")
            st.plotly_chart(plot_time_series(sim_results), key="time_series_single")
            st_folium(create_folium_map(sim_results, time_step, st.session_state.map_style_single, st.session_state.layer_toggles_single, st.session_state.map_zoom_single), width=700, key="folium_map_single")
            map_style = st.selectbox("Map Style", ["OpenStreetMap", "Stamen Terrain", "CartoDB Positron"], key="map_style_single")
            layer_toggles = st.multiselect("Map Layers", ["CO2 Heatmap", "Sources", "Interventions", "Buildings", "Sensors", "Wind Direction"], key="layer_toggles_single")
            zoom = st.slider("Map Zoom", 10, 18, 13, key="map_zoom_single")
            st.write("Wind Direction: Arrow overlay")
            st.write(f"Suggested Location: {sim_results.get('optimal_location', 'N/A')}")
        if st.button("Reset Simulation", key="reset_simulation"):
            st.session_state.clear()

    with tab2:
        st.header("Data")
        st.subheader("Current Data")
        st.write("Sources:", st.session_state.get("sources", []))
        st.write("Interventions:", st.session_state.get("interventions", []))
        st.write("Buildings:", st.session_state.get("buildings", []))
        st.write("Sensors:", st.session_state.get("sensors", []))
        st.subheader("Saved Scenarios")
        scenarios = get_data("scenarios")
        st.write("Scenarios:", list(scenarios.keys()))
        for scenario_name in scenarios:
            st.write(f"**{scenario_name}:**")
            scenario_data = scenarios[scenario_name]
            st.write("Sources:", scenario_data.get("sources", []))
            st.write("Interventions:", scenario_data.get("interventions", []))
            st.write("Buildings:", scenario_data.get("buildings", []))
            st.write("Sensors:", scenario_data.get("sensors", []))
        st.subheader("Simulation History")
        st.write(get_data("simulations"))

if __name__ == "__main__":
    if "sources" not in st.session_state:
        st.session_state.sources = []
        st.session_state.interventions = []
        st.session_state.buildings = []
        st.session_state.sensors = []
        st.session_state.simulations = {}
        st.session_state.simulation_results = {}
    main()
