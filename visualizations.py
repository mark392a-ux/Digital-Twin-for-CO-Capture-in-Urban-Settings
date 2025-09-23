# visualizations.py
import plotly.graph_objects as go
import folium
import numpy as np
import streamlit as st
import math

def plot_3d_co2(simulation_results, time_step):
    if not simulation_results or 'co2_grid' not in simulation_results:
        return go.Figure().update_layout(title="3D CO2 Concentration")
    try:
        co2_grid = simulation_results['co2_grid'][time_step - 1]
        x, y, z = np.indices(co2_grid.shape)
        fig = go.Figure(data=[
            go.Scatter3d(
                x=x.flatten(), y=y.flatten(), z=z.flatten(),
                mode='markers',
                marker=dict(size=3, color=co2_grid.flatten(), colorscale='Viridis', opacity=0.5)
            )
        ])
        fig.update_layout(
            title=f"3D CO2 Concentration at Time Step {time_step}",
            scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z")
        )
    except Exception as e:
        st.write(f"Debug: 3D plot error: {str(e)}")
        return go.Figure().update_layout(title=f"3D CO2 Concentration at Time Step {time_step} (Error)")
    return fig

def plot_2d_slice(simulation_results, z_height, time_step):
    if not simulation_results or 'co2_grid' not in simulation_results:
        return go.Figure().update_layout(title=f"2D CO2 Slice at Z={z_height}")
    try:
        co2_grid = simulation_results['co2_grid'][time_step - 1]
        z_height = min(max(0, int(z_height)), co2_grid.shape[2] - 1)
        slice_2d = co2_grid[:, :, z_height]
        fig = go.Figure(data=go.Heatmap(z=slice_2d, colorscale='Viridis'))
        fig.update_layout(
            title=f"2D CO2 Slice at Z={z_height}, Time Step {time_step}",
            xaxis_title="X", yaxis_title="Y"
        )
    except Exception as e:
        st.write(f"Debug: 2D slice error: {str(e)}")
        return go.Figure().update_layout(title=f"2D CO2 Slice at Z={z_height} (Error)")
    return fig

def plot_time_series(simulation_results):
    if not simulation_results or 'co2_grid' not in simulation_results:
        return go.Figure().update_layout(title="CO2 Metrics Over Time")
    try:
        co2_grid = simulation_results['co2_grid']
        time_steps = range(1, co2_grid.shape[0] + 1)
        avg_co2 = [np.mean(co2_grid[t]) * 1000 for t in range(co2_grid.shape[0])]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(time_steps), y=avg_co2, mode='lines', name='Avg CO2 (ppm)',
            line=dict(color='#1f77b4')
        ))
        fig.update_layout(
            title="CO2 Metrics Over Time",
            xaxis_title="Time Step (hours)",
            yaxis_title="CO2 (ppm)",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
    except Exception as e:
        st.write(f"Debug: Time series error: {str(e)}")
        return go.Figure().update_layout(title="CO2 Metrics Over Time (Error)")
    return fig

def create_folium_map(simulation_results, time_step, map_style="OpenStreetMap", layer_toggles=None, zoom=13):
    style_dict = {
        "OpenStreetMap": {"tiles": "OpenStreetMap", "attr": "© OpenStreetMap contributors"},
        "Stamen Terrain": {"tiles": "https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg", "attr": "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."},
        "CartoDB Positron": {"tiles": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", "attr": "© OpenStreetMap contributors, © CartoDB"}
    }
    tile_info = style_dict.get(map_style, style_dict["OpenStreetMap"])
    # Determine map center based on weather API or first source
    use_api = st.session_state.get('use_api', False)
    if use_api and 'lat' in st.session_state and 'lon' in st.session_state:
        center_lat = st.session_state.lat
        center_lon = st.session_state.lon
    elif st.session_state.get('sources') and st.session_state.sources[0].get('x') is not None:
        center_lat = st.session_state.sources[0]['x'] * 0.01  # Temporary, will adjust below
        center_lon = st.session_state.sources[0]['y'] * 0.01
    else:
        center_lat, center_lon = 51.505, -0.09  # Default to London

    # Define grid size (e.g., 50 units = 5 km, adjustable)
    grid_size_km = 5.0  # 5 km x 5 km area
    lat_per_km = 1 / 111.0  # Approx 1 degree lat = 111 km
    lon_per_km = 1 / (111.0 * math.cos(math.radians(center_lat)))  # Adjust for longitude at latitude

    def grid_to_geo(x, y):
        dx_km = (x / 50.0) * grid_size_km  # Normalize x (0-50) to 0-5 km
        dy_km = (y / 50.0) * grid_size_km  # Normalize y (0-50) to 0-5 km
        lat = center_lat + (dy_km * lat_per_km)  # North-South offset
        lon = center_lon + (dx_km * lon_per_km)  # East-West offset
        return lat, lon

    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles=tile_info["tiles"], attr=tile_info["attr"])
    layer_toggles = layer_toggles or []

    # Add CO2 heatmap
    if simulation_results and 'co2_grid' in simulation_results and "CO2 Heatmap" in layer_toggles:
        co2_grid = simulation_results['co2_grid'][time_step - 1]
        heatmap_data = []
        for i in range(co2_grid.shape[0]):
            for j in range(co2_grid.shape[1]):
                if co2_grid[i, j, 0] > 0:
                    lat, lon = grid_to_geo(i, j)
                    heatmap_data.append([lat, lon, co2_grid[i, j, 0] * 100])
        try:
            from folium.plugins import HeatMap
            HeatMap(heatmap_data, radius=15).add_to(m)
        except ImportError:
            pass

    # Add Sources
    if "Sources" in layer_toggles:
        for source in st.session_state.get('sources', []):
            lat, lon = grid_to_geo(source['x'], source['y'])
            folium.Marker(
                location=[lat, lon],
                popup=f"Source: {source['type']}, Emission: {source['emission_rate']} kg/h",
                icon=folium.Icon(color="red")
            ).add_to(m)

    # Add Interventions
    if "Interventions" in layer_toggles:
        for intervention in st.session_state.get('interventions', []):
            lat, lon = grid_to_geo(intervention['x'], intervention['y'])
            folium.Marker(
                location=[lat, lon],
                popup=f"Intervention: {intervention['type']}, Efficiency: {intervention['efficiency']}",
                icon=folium.Icon(color="green")
            ).add_to(m)

    # Add Buildings
    if "Buildings" in layer_toggles:
        for building in st.session_state.get('buildings', []):
            lat1, lon1 = grid_to_geo(building['x_min'], building['y_min'])
            lat2, lon2 = grid_to_geo(building['x_max'], building['y_max'])
            folium.Rectangle(
                bounds=[[lat1, lon1], [lat2, lon2]],
                popup=f"Building: {building['material']}",
                color="blue", fill=True, fill_opacity=0.2
            ).add_to(m)

    # Add Sensors
    if "Sensors" in layer_toggles:
        for sensor in st.session_state.get('sensors', []):
            lat, lon = grid_to_geo(sensor['x'], sensor['y'])
            folium.Marker(
                location=[lat, lon],
                popup=f"Sensor at Z={sensor['z']}, CO2: {sensor['co2_reading']} ppm",
                icon=folium.Icon(color="purple")
            ).add_to(m)

    # Add Wind Direction Overlay
    if "Wind Direction" in layer_toggles:
        st.write(f"Debug: Wind Direction block entered, wind_direction = {st.session_state.get('wind_direction', 'Not set')}")
        wind_direction = st.session_state.get('wind_direction', 0)
        source_loc = [center_lat, center_lon] if not st.session_state.get('sources') else grid_to_geo(st.session_state.sources[0]['x'], st.session_state.sources[0]['y'])
        arrow_length = 0.1  # Approx 0.1 degrees (11 km)
        rad = math.radians(wind_direction)
        dx = arrow_length * math.cos(rad)
        dy = arrow_length * math.sin(rad)
        arrow_head_length = 0.03  # Approx 3.3 km
        arrow_head_angle = math.radians(20)
        points = [[source_loc[0], source_loc[1]]]
        tip = [source_loc[0] + dy, source_loc[1] + dx]  # Adjusted for lat/lon order
        points.append(tip)
        points.append([
            tip[0] - arrow_head_length * math.cos(rad - arrow_head_angle),
            tip[1] - arrow_head_length * math.sin(rad - arrow_head_angle)
        ])
        points.append(tip)
        points.append([
            tip[0] - arrow_head_length * math.cos(rad + arrow_head_angle),
            tip[1] - arrow_head_length * math.sin(rad + arrow_head_angle)
        ])
        folium.PolyLine(
            locations=points,
            color="black",
            weight=2,
            opacity=0.8,
            popup=f"Wind Direction: {wind_direction}°"
        ).add_to(m)

    return m
