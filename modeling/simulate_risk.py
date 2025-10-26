import numpy as np
import pandas as pd
import pathlib
import joblib
import json


def main():
    """Simulate extinction risk over the next 5 years for each species.

    This script loads the trained baseline model and the most recent
    observations per species. It then performs Monte Carlo simulations
    of population growth over a five-year horizon, estimating the probability
    that population size falls below a quasi-extinction threshold (e.g., 50
    individuals). Results are written to data/processed/risk_curves.json.
    """
    p = pathlib.Path("data/processed")
    # Load model
    model = joblib.load("models/baseline.pkl")["reg"]
    # Load last observed rows
    last = pd.read_parquet(p / "last_rows.parquet")
    records = []
    for _, row in last.iterrows():
        species_id = row["species_id"]
        curr_year = int(row["year"])
        count = row["count"]
        # Feature vector for prediction (using last known covariates)
        X = [[row["count_lag"], row["forest_loss_pct"], row["temp_anom"], row["prot_cov"]]]
        mu = model.predict(X)[0]
        risk_curve = []
        for i in range(1, 6):
            # Simulate 400 draws of growth, assume normal error
            growths = np.random.normal(mu, 0.25, 400)
            N = count * np.exp(growths)
            prob = float(np.mean(N < 50))
            risk_curve.append({"year": curr_year + i, "p": prob})
        records.append({"species_id": species_id, "risk_curve": risk_curve})

    # Save to JSON
    out_path = p / "risk_curves.json"
    with open(out_path, "w") as f:
        json.dump(records, f, indent=2)
    print("\u2705 Risk simulation complete. Results saved to data/processed/risk_curves.json")


if __name__ == "__main__":
    main()
