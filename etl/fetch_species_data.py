import json
import os
import requests
import pathlib


def fetch_species():
    """
    Fetch data for pinned endangered species from the IUCN Red List API.

    This function reads a list of species names from data/pinned_species.json,
    sends requests to the IUCN API for each species, and saves the responses
    to data/processed/iucn_species_data.json. An API token must be provided
    via the IUCN_TOKEN environment variable.
    """
    token = os.getenv("IUCN_TOKEN")
    if not token:
        raise RuntimeError("IUCN_TOKEN environment variable not set. Please provide your IUCN API token in the environment.")

    # Determine repository root relative to this file (etl directory)
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    pinned_file = repo_root / "data" / "pinned_species.json"
    processed_dir = repo_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Load pinned species list
    with open(pinned_file) as f:
        species_list = json.load(f)

    results = []
    for name in species_list:
        url = f"https://apiv3.iucnredlist.org/api/v3/species/{name}"
        params = {"token": token}
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                results.append(resp.json())
            else:
                results.append({"name": name, "error": f"status code {resp.status_code}"})
        except Exception as e:
            # Record any network or parsing errors
            results.append({"name": name, "error": str(e)})

    # Save results to JSON in processed directory
    out_path = processed_dir / "iucn_species_data.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved species data to {out_path}")


if __name__ == "__main__":
    fetch_species()
