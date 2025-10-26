#!/usr/bin/env bash
set -e
python etl/make_demo_data.py
python features/make_features.py
python modeling/train_baseline.py
python modeling/simulate_risk.py
echo '✅ Pipeline complete.'
