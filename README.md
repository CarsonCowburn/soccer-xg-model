# Soccer xG Model

An expected goals model built on StatsBomb open event data.

**xG** is the probability that a shot becomes a goal, based on things such as the location where it was take, and how (header, etc.). 

> **Status:** Baseline model complete. Player/Team dashboard is in progress.

## Data

[StatsBomb Open Data](https://github.com/statsbomb/open-data), accessed with [`statsbombpy`](https://github.com/statsbomb/statsbombpy).

- **Competition:** FIFA Mens World Cup 2022 (64 matches)
- **Shots:** 1,430 non-penalty shots (penalties excluded from dataset)

Raw data isn't stored in the repo. To download it, run 'notebooks/01_load_shots.ipynb'.

## Approach

**Features**, calculated from each shot's location on StatsBomb's x,y pitch (120 x 80):

| Feature | Description |
|---|---|
| `distance` | Straight-line distance to the centre of the goal (yards) |
| `angle` | Angle the goal mouth makes from the shot location (degrees). A wider angle means more of the goal is visible. |
| `is_header` | Whether the shot was a header |

**Model:** logistic regression model, trained on 75% of shots and evaluated on the held-out remaining 25%, stratified by outcome.

## Results

Evaluated on the same held-out test shots:
 
| Model | Log loss ↓ | Brier ↓ | ROC AUC ↑ | Total xG | Actual goals |
|---|---|---|---|---|---|
| This model | 0.283 | 0.083 | 0.799 | 35.0 | 38 |
| StatsBomb xG | 0.255 | 0.074 | 0.844 | 33.5 | 38 |

Due to only having three location-based features, my model trails StatsBomb's commerical xG, which also accounts for goalkeeper and defender positions, but it is reasonably close (ROC AUC for my model is 0.80 vs StatsBomb's 0.84) and is well calibrated - having 35.0 xG against 38 actual. This test set is small, so the numbers carry sampling noise, but the coefficients behave as expected. Converted to oddds multipliers:

| Feature | Odds multiplier | Interpretation |
|---|---|---|
| Distance | 0.89 per yard | Each extra yard cuts the odds of scoring by ~11% |
| Angle | 1.008 per degree | Each extra 10° of goal visible raises the odds by ~8% |
| Header | 0.29 | Headers have ~71% lower odds than foot shots from the same spot |

Angle's effect appears small due to the fact that it overlaps heavily with distance as close shots tend to have wider angles. Once the distance is know, angle only really separates central shots from wide onces at the same range.

## Notebooks

1. `01_load_shots.ipynb`: downloads World Cup 2022 shot data from StatsBomb
2. `02_features.ipynb`: builds distance, angle and header features
3. `03_baseline_model.ipynb`: trains the logistic regression and compares it to StatsBomb's xG

## Running it

```bash
git clone https://github.com/CarsonCowburn/soccer-xg-model.git
cd soccer-xg-model
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run the notebooks in order.

## Next steps

- [ ] Add more competitions to grow training set
- [ ] Add new features: under pressure, play pattern, first-time shots, assist type, etc.
- [ ] Calibration curves and cross-validation
-[ ] Split train/test by match to avoid leakage
- [ ] Strealit dashboard: player and team xG, shot maps

## Acknowledgments

Data provided [StatsBomb](https://statsbomb.com/) by through their free open data release.