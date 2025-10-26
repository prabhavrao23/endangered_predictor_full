import pandas as pd
import pathlib
from sklearn.ensemble import GradientBoostingRegressor
import joblib


def main():
    """Train a baseline regression model to predict log growth rates.

    This script loads the training dataset produced by the feature engineering
    stage, fits a GradientBoostingRegressor on the environmental and lagged
    population features to predict the log change in population. It saves
    the trained model to models/baseline.pkl and stores the last observed
    record for each species (per species-year) to data/processed/last_rows.parquet
    for downstream simulation.
    """
    p = pathlib.Path("data/processed")
    df = pd.read_parquet(p / "training.parquet")

    # Extract features and target
    X = df[["count_lag", "forest_loss_pct", "temp_anom", "prot_cov"]].values
    y = df["dlogN"].values

    # Train Gradient Boosting Regressor
    model = GradientBoostingRegressor(random_state=0)
    model.fit(X, y)

    # Persist the model
    models_dir = pathlib.Path("models")
    models_dir.mkdir(exist_ok=True)
    joblib.dump({"reg": model}, models_dir / "baseline.pkl")

    # Save the most recent row for each species (for simulation later)
    last = df.sort_values(["species_id", "year"]).groupby("species_id").tail(1)
    last.to_parquet(p / "last_rows.parquet", index=False)

    print("\u2705 Model trained and saved to models/baseline.pkl")


if __name__ == "__main__":
    main()
