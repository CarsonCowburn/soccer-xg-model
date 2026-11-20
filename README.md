# Soccer xG Model

An expected goals model built on StatsBomb open event data.

**xG** is the probability that a shot becomes a goal, based on things such as the location where it was taken, and how (header, etc.). 

> **Status:** Baseline model complete. Player/Team dashboard is in progress.

## Data

[StatsBomb Open Data](https://github.com/statsbomb/open-data), accessed with [`statsbombpy`](https://github.com/statsbomb/statsbombpy).

- **Competitions:** FIFA World Cup 2018 & 2022, UEFA Euro 2020 & 2024, Premier League 2015/16 (610 matches)
- **Shots:** 15,737 total; 15,423 after removing 172 penalties and 142 penalty-shootout kicks

Raw data isn't stored in the repo. To download it, run:

```bash
uv run python src/load_data.py
```

This caches each match's events in `data/raw/events/` and saves all shots to `data/processed/shots.parquet`. The first run takes about 20 minutes; re-runs load from cache in under a minute.

### Cleaning

Then clean the shots with `python src/clean.py`, which:

- drops 142 penalty-shootout kicks (`period == 5`)
- sets aside 172 penalties in `data/processed/penalties.parquet` 
- splits each shot's location into `x`, `y` (x capped at 120) and adds `is_goal`
- fills StatsBomb's True-only Tag columns (e.g. `under_pressure`, `shot_first_time`) with False where missing
- checks for missing locations, off-pitch coordinates and duplicate shots

Result: 15,423 shots in `data/processed/shots_clean.parquet`, with a 9.2% goal rate.

## Approach

**Features**, calculated from each shot's location on StatsBomb's x,y pitch (120 x 80):

| Feature | Description |
|---|---|
| `distance` | Straight-line distance to the centre of the goal (yards) |
| `angle` | Angle the goal mouth makes from the shot location (degrees). A wider angle means more of the goal is visible. |
| `is_header` | Whether the shot was a header |

**Model:** logistic regression model, trained on 75% of shots and evaluated on the held-out remaining 25%, stratified by outcome.

## Results

> Results below are from the World Cup 2022 baseline; being re-run on the expanded dataset.

Evaluated on the same held-out test shots:
 
| Model | Log loss ↓ | Brier ↓ | ROC AUC ↑ | Total xG | Actual goals |
|---|---|---|---|---|---|
| This model | 0.279 | 0.082 | 0.807 | 35.0 | 38 |
| StatsBomb xG | 0.255 | 0.074 | 0.844 | 33.5 | 38 |

Due to only having three location-based features, my model trails StatsBomb's commercial xG, which also accounts for goalkeeper and defender positions, but it is reasonably close (ROC AUC for my model is 0.81 vs StatsBomb's 0.84) and is well calibrated - having 35.0 xG against 38 actual. This test set is small, so the numbers carry sampling noise, but the coefficients behave as expected. Converted to odds multipliers:

| Feature | Odds multiplier | Interpretation |
|---|---|---|
| Distance | 0.90 per yard | Each extra yard cuts the odds of scoring by ~10% |
| Angle | 1.022 per degree | Each extra 10° of goal visible raises the odds by ~25% |
| Header | 0.28 | Headers have ~72% lower odds than foot shots from the same spot |

Distance and angle overlap heavily, as close shots tend to have wider angles. Once the distance is known, angle mainly separates central shots from wide ones at the same range.

## Notebooks

1. `01_load_shots.ipynb`: first look at World Cup 2022 shot data (loading now done by `src/load_data.py`)
2. `02_eda.ipynb`: goal rates by body part, shot type, pressure and play pattern, plus a shot map
3. `03_features.ipynb`: builds distance, angle and header features
4. `04_baseline_model.ipynb`: trains the logistic regression and compares it to StatsBomb's xG

## Running it

```bash
git clone https://github.com/CarsonCowburn/soccer-xg-model.git
cd soccer-xg-model
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then download and clean the data, and run the notebooks in order:

```bash
python src/load_data.py
python src/clean.py
```

## Next steps

- [x] Add more competitions to grow training set
- [ ] Add new features: under pressure, play pattern, first-time shots, assist type, etc.
- [ ] Calibration curves and cross-validation
- [ ] Split train/test by match to avoid leakage
- [ ] Streamlit dashboard: player and team xG, shot maps

## Acknowledgments

Data provided by [StatsBomb](https://statsbomb.com/) through their free open data release.