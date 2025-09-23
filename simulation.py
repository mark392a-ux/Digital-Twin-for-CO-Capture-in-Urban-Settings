# simulation.py
import numpy as np
import requests
import random

def run_simulation(sources, interventions, buildings, wind_speed, wind_direction, time_steps, use_api):
    # Initialize 3D grid (50x50x20) for CO2 concentrations
    grid_size = (50, 50, 20)
    co2_grid = np.zeros((time_steps, *grid_size))

    # Mock wind data if not using API
    if not use_api:
        wind_speed = wind_speed if wind_speed is not None else 5.0
        wind_direction = wind_direction if wind_direction is not None else 0
    else:
        # Placeholder for OpenWeatherAPI (mock for now)
        wind_speed = random.uniform(3.0, 10.0)
        wind_direction = random.uniform(0, 360)

    # Simulate CO2 dispersion from sources
    for source in sources:
        x, y, z = source['x'], source['y'], source['z']
        emission_rate = source['emission_rate']
        intensity = source['intensity']
        for t in range(time_steps):
            # Simple Gaussian plume model
            sigma = 5.0 + wind_speed * t * 0.1  # Dispersion factor
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    for k in range(grid_size[2]):
                        # Adjust position based on wind
                        x_adj = i - (x + wind_speed * np.cos(np.radians(wind_direction)) * t)
                        y_adj = j - (y + wind_speed * np.sin(np.radians(wind_direction)) * t)
                        z_adj = k - z
                        dist = np.sqrt(x_adj**2 + y_adj**2 + z_adj**2)
                        if dist < 1e-6: dist = 1e-6  # Avoid division by zero
                        co2_grid[t, i, j, k] += emission_rate * intensity * np.exp(-dist**2 / (2 * sigma**2))

    # Apply interventions (reduce CO2 within radius)
    total_cost = 0
    for intervention in interventions:
        x, y, z = intervention['x'], intervention['y'], intervention['z']
        efficiency = intervention['efficiency']
        radius = intervention['radius']
        total_cost += intervention['cost']
        for t in range(time_steps):
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    for k in range(grid_size[2]):
                        dist = np.sqrt((i - x)**2 + (j - y)**2 + (k - z)**2)
                        if dist <= radius:
                            co2_grid[t, i, j, k] *= (1 - efficiency)

    # Apply building effects (block CO2 dispersion)
    for building in buildings:
        x_min, x_max = building['x_min'], building['x_max']
        y_min, y_max = building['y_min'], building['y_max']
        z_min, z_max = building['z_min'], building['z_max']
        for t in range(time_steps):
            for i in range(int(x_min), int(x_max) + 1):
                for j in range(int(y_min), int(y_max) + 1):
                    for k in range(int(z_min), int(z_max) + 1):
                        if 0 <= i < 50 and 0 <= j < 50 and 0 <= k < 20:
                            co2_grid[t, i, j, k] *= 0.5  # Reduce CO2 by 50% in buildings

    # Calculate metrics
    avg_co2 = np.mean(co2_grid) * 1000  # Scale to ppm
    baseline_co2 = np.mean(co2_grid[0]) * 1000 if interventions else avg_co2
    co2_reduction = ((baseline_co2 - avg_co2) / baseline_co2 * 100) if baseline_co2 > 0 else 0
    aqi = min(500, max(0, int(avg_co2 / 2)))  # Mock AQI calculation
    total_cost = total_cost if interventions else 0

    # Find optimal intervention location (max CO2 point in first time step)
    max_co2_idx = np.unravel_index(np.argmax(co2_grid[0]), grid_size)
    optimal_location = {"x": max_co2_idx[0], "y": max_co2_idx[1], "z": max_co2_idx[2]}

    return {
        "co2_grid": co2_grid,
        "co2_reduction": round(co2_reduction, 2),
        "avg_co2": round(avg_co2, 2),
        "aqi": aqi,
        "total_cost": total_cost,
        "optimal_location": optimal_location
    }
