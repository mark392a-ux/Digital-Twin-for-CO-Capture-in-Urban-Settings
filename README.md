# Digital Twin for CO2 Capture in Urban Settings

An interactive Streamlit application for simulating and visualizing CO2 dispersion in a 3D urban environment, then evaluating intervention strategies such as vertical gardens, roadside units, and biofilters.

## Overview

This project models CO2 behavior across a `50 x 50 x 20` grid over time. You can:

- Add emission sources (traffic, industry, household)
- Add interventions with efficiency/cost/capacity settings
- Add buildings and sensors
- Configure wind manually or with OpenWeather data
- Run time-step simulations
- Visualize results in 3D, 2D slice, time series, and geospatial map views
- Save/load scenarios
- Export a PDF summary report

## Features

- Streamlit UI with sidebar inputs and multi-tab output views
- Time-based CO2 simulation with wind-influenced dispersion
- Intervention impact simulation and cost aggregation
- Building-aware CO2 attenuation zones
- Plotly-based charts: 3D CO2 scatter, 2D Z-slice heatmap, and CO2 time series
- Folium map overlays: CO2 heatmap, sources, interventions, buildings, sensors, and wind direction
- Scenario persistence via `data.json`
- PDF report export using ReportLab

## Tech Stack

- Python
- Streamlit
- Plotly
- Folium
- streamlit-folium
- NumPy
- Requests
- ReportLab

## Project Structure

```text
.
|-- app.py                 # Streamlit app entrypoint and UI logic
|-- simulation.py          # Core CO2 simulation engine
|-- visualizations.py      # Plotly/Folium visual outputs
|-- data_manager.py        # Save/load scenario data in JSON
|-- utils.py               # Input validation helpers
|-- data.json              # Scenario data store
|-- schema.sql             # Optional SQL schema draft
|-- simulation_logic.txt   # High-level simulation notes
|-- ui_wireframe.txt       # UI planning notes
|-- requirements.txt       # Python dependencies
|-- .env.example           # Environment variable template
|-- .env                   # Local environment variables
|-- .gitignore
```

## Prerequisites

- Python 3.9+ recommended
- `pip`

## Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd Digital-Twin-for-CO-Capture-in-Urban-Settings-main
```

2. Create and activate a virtual environment:

```bash
python -m venv dtwin_env
```

Windows PowerShell:

```bash
.\dtwin_env\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source dtwin_env/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the App

```bash
streamlit run app.py
```

Then open the local URL printed by Streamlit (usually `http://localhost:8501`).

## How to Use

1. In the sidebar, add sources, interventions, buildings, and sensors.
2. Set wind/time-step simulation parameters.
3. Run the simulation.
4. Explore outputs in the `Simulation` tab: 3D concentration plot, 2D slice view, time-series trend, and interactive map layers.
5. Use the `Data` tab to inspect current objects and saved scenarios.
6. Export a PDF report from the sidebar.

## Data and Persistence

- Scenarios are saved to and loaded from [`data.json`](./data.json).
- `schema.sql` provides a draft relational schema if you later migrate to SQLite/PostgreSQL.

## Environment Variables

Copy `.env.example` to `.env` and set your key:

```env
OPENWEATHER_API_KEY=your_api_key_here
```

The app loads this variable at runtime using `python-dotenv`.

## Current Limitations

- Simulation uses a simplified Gaussian-style dispersion approach.
- Some planned logic in `simulation_logic.txt` (for example advanced intervention optimization) is not fully implemented.

## Future Improvements

- Add a `pyproject.toml` with locked dependency versions
- Add automated tests for simulation and validation modules
- Introduce database-backed persistence for simulation history
