CREATE TABLE sources (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, x REAL, y REAL, z REAL, emission_rate REAL); 
CREATE TABLE interventions (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, x REAL, y REAL, z REAL, efficiency REAL, radius REAL); 
CREATE TABLE buildings (id INTEGER PRIMARY KEY AUTOINCREMENT, x_min REAL, x_max REAL, y_min REAL, y_max REAL, z_min REAL, z_max REAL); 
