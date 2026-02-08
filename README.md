# 🌊 Project Blue Nexus

**An AI-powered oceanographic research workstation** — satellite data pipelines, environmental monitoring, and scientific visualization for the Great Lakes and beyond.

<p align="center">
  <img src="01_lake_erie_sst/output/lake_erie_sst_peak_2023.png" width="700" alt="Lake Erie Peak SST — August 4, 2023">
</p>

---

## What Is Blue Nexus?

Blue Nexus is a growing collection of oceanographic analysis projects, each exploring a different dimension of aquatic environmental science. The workstation combines satellite remote sensing data from NOAA with Python-based scientific computing to build reproducible, publication-quality analyses.

All projects share a common data cache and Python environment, and each one builds on the insights of those before it.

---

## 📂 Projects

| # | Project | Description | Status |
|---|---------|-------------|--------|
| 01 | [**Lake Erie SST Analysis**](01_lake_erie_sst/) | Surface temperature pipeline, seasonal dynamics, multi-year comparison, basin-scale physics, and SST–chlorophyll bloom correlation | ✅ Complete |
| 02 | **Lake Erie HAB Deep-Dive** | Harmful algal bloom prediction, nutrient loading analysis, bloom severity index | 🔜 Planned |
| 03 | **Real-Time Monitoring Dashboard** | Automated data fetching, live visualization, alert thresholds | 🔜 Planned |
| 04 | **CTD Profile Analysis** | Vertical water column profiles, T-S diagrams, stratification detection | 🔜 Planned |
| 05 | **Great Lakes Current Visualization** | OSCAR/GlobCurrent vector fields, transport pathways | 🔜 Planned |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Internet connection (for initial data downloads from NOAA)

### Installation

```bash
# Clone the repository
git clone https://github.com/rynjon1993/BlueNexus.git
cd BlueNexus

# Create and activate virtual environment
python -m venv ocean_env
# Windows:
ocean_env\Scripts\activate
# macOS/Linux:
source ocean_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running a Project

Each project lives in its own folder with a Jupyter notebook. Navigate to the project folder and launch:

```bash
cd 01_lake_erie_sst
jupyter notebook 01_Lake_Erie_SST_Analysis.ipynb
```

Run all cells with **Kernel → Restart & Run All**. Data downloads are cached automatically — the first run takes 3–5 minutes, subsequent runs are instant.

---

## 🗂️ Repository Structure

```
BlueNexus/
├── README.md                           ← You are here
├── requirements.txt                    ← Shared Python dependencies
├── LICENSE                             ← MIT License
├── .gitignore
│
├── data/                               ← Shared data cache (gitignored — auto-downloaded)
│   ├── lake_erie_sst_2023_*.nc
│   ├── lake_erie_sst_20XX_jul_aug.nc
│   └── lake_erie_chl_2023_aug15.nc
│
├── 01_lake_erie_sst/                   ← Project 01: SST Analysis
│   ├── README.md
│   ├── 01_Lake_Erie_SST_Analysis.ipynb
│   └── output/                         ← Generated visualizations
│       ├── lake_erie_sst_peak_2023.png
│       └── ...
│
├── 02_lake_erie_hab/                   ← Project 02 (future)
├── 03_realtime_monitor/                ← Project 03 (future)
└── ...
```

---

## 🛠️ Technical Stack

| Tool | Role |
|------|------|
| **Python 3.10** | Core language |
| **xarray** | Multidimensional labeled arrays for NetCDF data |
| **cartopy** | Cartographic projections and geographic features |
| **matplotlib** | Publication-quality scientific figures |
| **pandas / NumPy** | Tabular statistics and numerical computation |
| **Jupyter Notebook** | Interactive analysis and narrative documentation |
| **NOAA ERDDAP** | REST API for satellite oceanographic data |

---

## 📡 Data Sources

| Dataset | Provider | ID | Use |
|---------|----------|----|-----|
| [GLSEA](https://apps.glerl.noaa.gov/erddap/griddap/GLSEA_GCS.html) | NOAA GLERL | `GLSEA_GCS` | Sea Surface Temperature (~1.4 km daily) |
| [VIIRS Chlorophyll](https://apps.glerl.noaa.gov/erddap/griddap/LE_CHL_VIIRS_SQ.html) | NOAA GLERL | `LE_CHL_VIIRS_SQ` | Chlorophyll-a concentration (~0.6 km) |

All data is in the public domain, provided by [NOAA Great Lakes Environmental Research Laboratory](https://www.glerl.noaa.gov/).

---

## 🔭 Roadmap

- [x] **Phase 1:** Environment setup, SST data pipeline, core visualizations
- [x] **Phase 2:** Multi-year comparison, basin dynamics, temperature anomaly analysis
- [x] **Phase 3:** Chlorophyll-a integration, SST–bloom spatial correlation
- [x] **Phase 4:** Portfolio polish, GitHub publication, scalable repo structure
- [ ] **Phase 5:** Real-time monitoring dashboard, automated data fetching
- [ ] **Phase 6:** CTD profile analysis, ocean current visualization
- [ ] **Phase 7:** AI-assisted report generation, RAG pipeline for research papers

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Ryan Jones** — Software engineer based near Lake Erie, building satellite oceanography tools from scratch. Learning by doing.

