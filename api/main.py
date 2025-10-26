from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import os
import pathlib
import requests

app = FastAPI(title="Endangered Species Risk API")

# Enable CORS for all origins (simple for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = pathlib.Path("data/processed")
PINNED_FILE = pathlib.Path("data/pinned_species.json")
IUCN_TOKEN = os.getenv("IUCN_TOKEN")


def load_pinned():
    """Load the list of pinned endangered species from JSON."""
    if PINNED_FILE.exists():
        with open(PINNED_FILE) as f:
            return json.load(f)
    return []


@app.get("/species")
def species():
    """List species for which we have population data and risk estimates."""
    try:
        df = pd.read_parquet(DATA / "last_rows.parquet")
    except Exception:
        return []
    return df[["species_id", "year", "count", "region_id"]].to_dict(orient="records")


@app.get("/risk/{species_id}")
def risk(species_id: str):
    """Return the risk curve for the specified species identifier."""
    try:
        with open(DATA / "risk_curves.json") as f:
            rc_list = json.load(f)
    except Exception:
        raise HTTPException(status_code=500, detail="Risk data not available")
    # Build a mapping for quick lookup
    rc_map = {r["species_id"]: r["risk_curve"] for r in rc_list}
    if species_id not in rc_map:
        raise HTTPException(status_code=404, detail="Species not found")
    # Get current count
    try:
        df = pd.read_parquet(DATA / "last_rows.parquet")
        row = df[df["species_id"] == species_id]
        current_count = int(row.iloc[0]["count"]) if not row.empty else None
    except Exception:
        current_count = None
    return {"species_id": species_id, "current_count": current_count, "risk_curve": rc_map[species_id]}


@app.get("/pinned")
def pinned():
    """Return the list of pinned endangered species along with any available risk or info."""
    pinned_list = load_pinned()
    results = []
    # Load risk data if present
    try:
        with open(DATA / "risk_curves.json") as f:
            risk_map = {r["species_id"]: r["risk_curve"] for r in json.load(f)}
    except Exception:
        risk_map = {}
    # Load additional species data from IUCN fetch script if present
    species_data = {}
    iucn_path = DATA / "iucn_species_data.json"
    if iucn_path.exists():
        try:
            with open(iucn_path) as f:
                data = json.load(f)
                # data may be list of dicts keyed by 'name'
                for item in data:
                    if isinstance(item, dict) and 'name' in item:
                        species_data[item['name']] = item
        except Exception:
            pass
    for entry in pinned_list:
        # entry may be dict with name or just name string
        name = entry.get("name") if isinstance(entry, dict) else entry
        result = {"name": name}
        if name in risk_map:
            result["risk_curve"] = risk_map[name]
        if name in species_data:
            result["info"] = species_data[name]
        results.append(result)
    return results


@app.get("/search")
def search(q: str = Query(..., description="Species name to search")):
    """Search for species information via the IUCN Red List API.

    Requires the IUCN_TOKEN environment variable to be set. Returns the raw
    response from the API or raises an HTTP error if the API request fails.
    """
    if not IUCN_TOKEN:
        raise HTTPException(status_code=400, detail="IUCN_TOKEN not set in environment")
    url = f"https://apiv3.iucnredlist.org/api/v3/species/{q}"
    response = requests.get(url, params={"token": IUCN_TOKEN})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
