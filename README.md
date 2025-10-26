# Endangered Species Population & Extinction Predictor

This project simulates population data for endangered species, trains a model to estimate extinction risk, exposes predictions via a FastAPI backend, and visualizes the results in a Streamlit dashboard.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r env/requirements.txt
bash infra/scripts/run_pipeline.sh
uvicorn api.main:app --reload
streamlit run app/streamlit_app.py
```

The pipeline scripts generate synthetic data. To adapt to real data, replace `etl/make_demo_data.py` with a script that downloads time series from a live API, and extend `features/make_features.py` to compute environmental and threat features. Pinned endangered animals and search functionality should be added to the Streamlit dashboard.
