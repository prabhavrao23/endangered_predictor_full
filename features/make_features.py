import numpy as np
import pandas as pd
import pathlib


def main():
    """Generate features for population data and save training dataset.

    This script reads population_panel.parquet produced by the ETL stage and
    computes synthetic environmental and protection features for each region-year.
    It then merges the features with the population counts, computes lagged counts
    and log differences (growth), and writes the result to training.parquet.
    """
    p = pathlib.Path("data/processed")
    # Load the population panel
    df = pd.read_parquet(p / "population_panel.parquet")

    # Initialize RNG for reproducibility
    rng = np.random.default_rng(7)

    feat_rows = []
    # Compute feature values for each region and year
    for (region, year), _ in df.groupby(["region_id", "year"]):
        # Synthetic percentage of forest loss (increasing over time with noise)
        forest_loss_pct = max(0, min(100, rng.normal(1.5 * (year - 2010) / 15, 3)))
        # Synthetic temperature anomaly (warmer over time with noise)
        temp_anom = rng.normal(0.03 * (year - 2010), 0.4)
        # Synthetic protected area coverage (gradually increasing with noise)
        prot_cov = max(0.0, min(1.0, 0.2 + 0.02 * (year - 2010) + rng.normal(0, 0.05)))
        feat_rows.append([region, year, forest_loss_pct, temp_anom, prot_cov])

    # Assemble features DataFrame
    feats = pd.DataFrame(
        feat_rows,
        columns=["region_id", "year", "forest_loss_pct", "temp_anom", "prot_cov"],
    )

    # Merge features with population counts
    panel = df.merge(feats, on=["region_id", "year"]).sort_values(["species_id", "year"])

    # Lagged counts and growth rates
    panel["count_lag"] = panel.groupby("species_id")["count"].shift(1)
    panel["dlogN"] = np.log(panel["count"] + 1) - np.log(panel["count_lag"] + 1)

    # Drop rows where lag is not available (first year of each species)
    panel = panel.dropna().reset_index(drop=True)

    # Write the training dataset
    p.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(p / "training.parquet", index=False)
    print("\u2705 Saved data/processed/training.parquet")


if __name__ == "__main__":
    main()
