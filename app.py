# app.py
import streamlit as st
from visualizations import plot_3d_co2, plot_2d_slice, plot_time_series, create_folium_map
from data_manager import get_data, save_scenario, load_scenario
from simulation import run_simulation
from utils import validate_inputs

def main():
    st.set_page_config(layout="wide")  # Wide layout for tablet responsiveness
    st.title("CO2 Digital Twin for Urban Settings")

    # Sidebar
    with st.sidebar:
        st.header("Inputs and Results")
        # Add Source
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

        # Add Intervention
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

        # Add Building
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

        # Scenario Save/Load
        with st.expander("Scenario Save/Load"):
            scenario_name = st.text_input("Scenario Name", key="scenario_name")
            if st.button("Save Scenario", key="save_scenario"):
                save_scenario(scenario_name, st.session_state.sources, st.session_state.interventions, st.session_state.buildings)
            scenario_load = st.selectbox("Load Scenario", ["None"] + list(get_data("scenarios").keys()), key="scenario_load")
            if scenario_load != "None":
                sources, interventions, buildings = load_scenario(scenario_load)
                st.session_state.sources = sources
                st.session_state.interventions = interventions
                st.session_state.buildings = buildings

        # Simulation Settings
        with st.expander("Simulation Settings"):
            use_api = st.checkbox("Use OpenWeatherAPI for wind", key="use_api")
            wind_speed = st.number_input("Wind Speed (m/s)", 0.0, 50.0, 5.0, key="wind_speed") if not use_api else None
            wind_direction = st.number_input("Wind Direction (degrees)", 0, 360, 0, key="wind_direction") if not use_api else None
            time_steps = st.number_input("Time Steps", 1, 24, 24, key="time_steps")
            if st.button("Run Simulation", key="run_simulation"):
                if validate_inputs({"wind_speed": wind_speed, "wind_direction": wind_direction, "time_steps": time_steps}):
                    st.session_state.simulation_results = run_simulation(
                        st.session_state.sources, st.session_state.interventions, st.session_state.buildings,
                        wind_speed, wind_direction, time_steps, use_api
                    )
                else:
                    st.error("Invalid simulation settings")

        # Simulation Results
        st.header("Simulation Results")
        if "simulation_results" in st.session_state and all(key in st.session_state.simulation_results for key in ["co2_reduction", "avg_co2", "aqi", "total_cost"]):
            st.metric("CO2 Reduction", f"{st.session_state.simulation_results['co2_reduction']}%")
            st.metric("Avg CO2", f"{st.session_state.simulation_results['avg_co2']} ppm")
            st.metric("AQI", st.session_state.simulation_results['aqi'])
            st.metric("Total Cost", f"${st.session_state.simulation_results['total_cost']}")
        else:
            st.write("No simulation results available. Run a simulation to see metrics.")

        # Export
        st.header("Export")
        if st.button("Download Report", key="download_report"):
            st.write("Report generation placeholder")

    # Main Area
    tab1, tab2 = st.tabs(["Simulation", "Data"])

    with tab1:
        st.header("Simulation")
        time_step = st.slider("Time Step", 1, time_steps, 1, key="time_step")
        if st.button("Play Animation", key="play_animation"):
            st.write("Animation placeholder")
        compare_run = st.selectbox("Compare Simulation", ["None"] + list(st.session_state.simulations.keys()), key="compare_run")
        if compare_run != "None":
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_3d_co2(st.session_state.simulation_results, time_step), key="3d_plot_compare")
                st.plotly_chart(plot_2d_slice(st.session_state.simulation_results, st.slider("Z Slice", 0, 20, 0, key="z_slice_compare"), time_step), key="2d_slice_compare")
                st.plotly_chart(plot_time_series(st.session_state.simulation_results), key="time_series_compare")
                st.write(create_folium_map(st.session_state.simulation_results, time_step))
                map_style = st.selectbox("Map Style", ["OpenStreetMap", "Stamen Terrain", "CartoDB Positron"], key="map_style_compare")
                layer_toggles = st.multiselect("Map Layers", ["CO2 Heatmap", "Sources", "Interventions", "Buildings", "Sensors"], key="layer_toggles_compare")
                st.slider("Map Zoom", 10, 18, 13, key="map_zoom_compare")
                st.write("Wind Direction: Arrow overlay placeholder")
                st.write(f"Suggested Location: {st.session_state.simulation_results.get('optimal_location', 'N/A')}")
            with col2:
                st.write("Comparison plots/maps placeholder")
        else:
            st.plotly_chart(plot_3d_co2(st.session_state.simulation_results, time_step), key="3d_plot_single")
            st.plotly_chart(plot_2d_slice(st.session_state.simulation_results, st.slider("Z Slice", 0, 20, 0, key="z_slice_single"), time_step), key="2d_slice_single")
            st.plotly_chart(plot_time_series(st.session_state.simulation_results), key="time_series_single")
            st.write(create_folium_map(st.session_state.simulation_results, time_step))
            map_style = st.selectbox("Map Style", ["OpenStreetMap", "Stamen Terrain", "CartoDB Positron"], key="map_style_single")
            layer_toggles = st.multiselect("Map Layers", ["CO2 Heatmap", "Sources", "Interventions", "Buildings", "Sensors"], key="layer_toggles_single")
            st.slider("Map Zoom", 10, 18, 13, key="map_zoom_single")
            st.write("Wind Direction: Arrow overlay placeholder")
            st.write(f"Suggested Location: {st.session_state.simulation_results.get('optimal_location', 'N/A')}")
        if st.button("Reset Simulation", key="reset_simulation"):
            st.session_state.clear()

    with tab2:
        st.header("Data")
        st.write("Sources", get_data("sources"))
        st.write("Interventions", get_data("interventions"))
        st.write("Buildings", get_data("buildings"))
        st.write("Sensors", get_data("sensors"))
        st.subheader("Simulation History")
        st.write(get_data("simulations"))
        if st.button("View Details", key="view_details"):
            st.write("Details placeholder")

if __name__ == "__main__":
    if "sources" not in st.session_state:
        st.session_state.sources = []
        st.session_state.interventions = []
        st.session_state.buildings = []
        st.session_state.simulations = {}
        st.session_state.simulation_results = {}
    main()
