import numpy as np, pandas as pd, pathlib
p = pathlib.Path('data/processed'); p.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)

species = ['CA_CONDOR','SIERRA_FOX','SAGE_GROUSE','DESERT_TORT']
regions = ['R1','R2','R3']
rows = []
for sp in species:
    r = rng.uniform(-0.05, 0.08)
    N = rng.integers(50, 200)
    for year in range(2008, 2026):
        env = rng.normal(0, 0.08)
        N = max(5, int(N * np.exp(r + env)))
        rows.append([sp, year, N, rng.choice(regions)])

pd.DataFrame(rows, columns=['species_id','year','count','region_id']).to_parquet(p/'population_panel.parquet', index=False)
print('Saved data/processed/population_panel.parquet')
