CREATE TABLE sources (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, x REAL, y REAL, z REAL, emission_rate REAL, intensity REAL, active_hours TEXT); 
CREATE TABLE interventions (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, x REAL, y REAL, z REAL, efficiency REAL, radius REAL, cost REAL, capacity REAL); 
CREATE TABLE buildings (id INTEGER PRIMARY KEY AUTOINCREMENT, x_min REAL, x_max REAL, y_min REAL, y_max REAL, z_min REAL, z_max REAL, material TEXT); 
CREATE TABLE simulations (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, co2_grid TEXT, total_co2_initial REAL, total_co2_final REAL, reduction_percent REAL, avg_ppm REAL, aqi_category TEXT, wind_speed REAL, wind_direction REAL); 
CREATE TABLE sensors (id INTEGER PRIMARY KEY AUTOINCREMENT, x REAL, y REAL, z REAL, co2_ppm REAL, timestamp DATETIME); 
