# Digital Twin for CO₂ Capture in Urban Settings

> An interactive simulation platform for modeling, visualizing, and optimizing CO₂ dispersion in urban environments — built with Python and Streamlit.


This project implements a digital twin of a CO₂ capture system in a smart city context. It models a `50 × 50 × 20` 3D grid over time, simulates wind-influenced dispersion, evaluates intervention strategies (vertical gardens, roadside units, biofilters), and presents results through interactive charts, maps, and exportable reports.

🔗 **Live Demo: [digitaltwinco.streamlit.app](https://digitaltwinco.streamlit.app/)**

---

## Screenshots

| Dashboard & Simulation Controls | 3D CO₂ Concentration |
|:---:|:---:|
| ![Dashboard](https://raw.githubusercontent.com/mark392a-ux/Digital-Twin-for-CO-Capture-in-Urban-Settings/main/docs/screenshots/dashboard.png) | ![3D View](https://raw.githubusercontent.com/mark392a-ux/Digital-Twin-for-CO-Capture-in-Urban-Settings/main/docs/screenshots/3d_concentration.png) |

| 2D Z-Slice Heatmap | CO₂ Time Series |
|:---:|:---:|
| ![2D Slice](https://raw.githubusercontent.com/mark392a-ux/Digital-Twin-for-CO-Capture-in-Urban-Settings/main/docs/screenshots/2d_slice.png) | ![Time Series](https://raw.githubusercontent.com/mark392a-ux/Digital-Twin-for-CO-Capture-in-Urban-Settings/main/docs/screenshots/time_series.png) |

| Geospatial Map | CO₂ Heatmap Overlay |
|:---:|:---:|
| ![Map](https://raw.githubusercontent.com/mark392a-ux/Digital-Twin-for-CO-Capture-in-Urban-Settings/main/docs/screenshots/map.png) | ![Heatmap](https://raw.githubusercontent.com/mark392a-ux/Digital-Twin-for-CO-Capture-in-Urban-Settings/main/docs/screenshots/heatmap.png) |

---

## Features

- **3D CO₂ simulation** — time-step dispersion across a voxel grid with wind influence and building-aware attenuation
- **Emission sources** — model traffic, industrial, and household emitters
- **Intervention strategies** — add vertical gardens, biofilters, roadside units; compare efficiency, cost, and capacity
- **Live weather integration** — pull wind data from OpenWeatherMap or configure manually
- **Multi-view visualizations** — 3D scatter plot, 2D Z-slice heatmap, CO₂ time series, and Folium geospatial map with layered overlays
- **Scenario persistence** — save and reload full scenarios via `data.json`
- **PDF report export** — generate summary reports with ReportLab

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit, streamlit-folium |
| Visualization | Plotly, Folium |
| Simulation & Data | Python, NumPy, Pandas |
| Reports | ReportLab |
| Weather API | OpenWeatherMap |
| Persistence | JSON (`data.json`), SQLite schema draft |
| Environment | python-dotenv |

---

## Project Structure

```text
Digital-Twin-for-CO-Capture-in-Urban-Settings/
├── app.py                  # Streamlit entrypoint and UI logic
├── simulation.py           # Core CO₂ simulation engine
├── visualizations.py       # Plotly and Folium visual outputs
├── data_manager.py         # Save/load scenario data (JSON)
├── utils.py                # Input validation helpers
├── data.json               # Scenario data store
├── schema.sql              # Optional SQL schema draft
├── simulation_logic.txt    # High-level simulation design notes
├── ui_wireframe.txt        # UI planning notes
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .env                    # Local environment variables (git-ignored)
└── .gitignore
```

---

## Installation

### Prerequisites
- Python 3.9+
- `pip`

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/mark392a-ux/Digital-Twin-for-CO-Capture-in-Urban-Settings.git
cd Digital-Twin-for-CO-Capture-in-Urban-Settings
```

**2. Create and activate a virtual environment**

```bash
python -m venv dtwin_env
```

Windows PowerShell:
```powershell
.\dtwin_env\Scripts\Activate.ps1
```

macOS / Linux:
```bash
source dtwin_env/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

```bash
cp .env.example .env
```

Open `.env` and set your OpenWeatherMap API key:

```env
OPENWEATHER_API_KEY=your_api_key_here
```

---

## Running the App

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit — usually `http://localhost:8501`.

---

## Usage

1. **Add objects** in the sidebar — emission sources, interventions, buildings, sensors
2. **Configure simulation** — set wind parameters (manual or from OpenWeather), time steps, and grid resolution
3. **Run the simulation** — click Run to execute dispersion calculations
4. **Explore outputs** in the `Simulation` tab:
   - 3D CO₂ concentration scatter
   - 2D horizontal Z-slice heatmap
   - CO₂ time series trend
   - Interactive Folium map with toggleable layers (sources, interventions, buildings, sensors, wind direction, CO₂ heatmap)
5. **Inspect data** in the `Data` tab — view and manage saved scenario objects
6. **Export** a PDF summary report from the sidebar

---

## Current Limitations

- Dispersion uses a simplified Gaussian-style approach — not a full CFD solver
- Some advanced intervention optimization logic (noted in `simulation_logic.txt`) is not yet fully implemented
- Scenario persistence is file-based JSON only (single-node)

---

## Roadmap

- [ ] Locked dependency versions via `pyproject.toml`
- [ ] Automated tests for simulation and validation modules
- [ ] Database-backed persistence for simulation history (SQLite / PostgreSQL)
- [ ] Real-time IoT sensor data integration
- [ ] ML-based predictive maintenance and capture optimization
- [ ] Multi-scenario side-by-side comparison tools

---

## What I Learned

- Building simulation models for real-world environmental systems
- Data analysis and visualization with Python's scientific stack
- CO₂ capture technologies and urban sustainability challenges
- Designing interactive digital twin interfaces with Streamlit

---

## License

MIT License — see [LICENSE](./LICENSE) for details.

---

## Contact

For questions, feedback, or collaboration, reach out via GitHub Issues or open a pull request.
