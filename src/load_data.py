# Import necessary tools
from pathlib import Path
import warnings
import pandas as pd
from statsbombpy import sb

# To hide statsbombpy's 'no credentials' warning
warnings.filterwarnings("ignore")

# Set up file path
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "events"
OUT = ROOT / "data" / "processed" / "shots.parquet"

# Get data for the following competitions
COMPETITIONS = [
    ("FIFA World Cup", "2022"), 
    ("FIFA World Cup", "2018"), 
    ("UEFA Euro", "2020"), 
    ("UEFA Euro", "2024"), 
    ("Premier League", "2015/2016"),
]

def get_matches():
    comps = sb.competitions()
    frames = []
    for comp, season in COMPETITIONS:
        row = comps[(comps.competition_name == comp) & (comps.season_name == season)]
        if row.empty:
            print(f"NOT FOUND: {comp} {season}")
            continue
        m = sb.matches(competition_id = int(row.competition_id.iloc[0]),
                       season_id = int(row.season_id.iloc[0]))
        m["competition"], m["season"] = comp, season
        frames.append(m[["match_id", "competition", "season", "match_date", "home_team", "away_team"]])
    return pd.concat(frames, ignore_index = True)
    
def load_events(match_id):
    path = RAW / f"{match_id}.pkl"
    if path.exists():
        return pd.read_pickle(path)
    ev = sb.events(match_id = match_id)
    ev.to_pickle(path)
    return ev

BASE_COLS = ["id", "match_id", "period", "minute", "second", "team", "player", "player_id", "position", "location",
             "play_pattern", "under_pressure"]

def build_shots():
    matches = get_matches()
    shots = []
    
    for i, row in enumerate(matches.itertuples(), 1):
        ev = load_events(row.match_id)
        s = ev[ev["type"] == "Shot"].copy()
        s["match_id"] = row.match_id
        keep = [c for c in BASE_COLS if c in s] + [c for c in s if c.startswith("shot")]
        s = s[keep]
        s["competition"], s["season"] = row.competition, row.season
        shots.append(s)

        if i % 50 == 0:
            print(f"{i}/{len(matches)} matches")
    return pd.concat(shots, ignore_index = True)

if __name__ == "__main__":
    df = build_shots()
    df.to_parquet(OUT, index = False)
    print(f"Saved {len(df):,} shots from {df.match_id.nunique()} matches -> {OUT}")
    print(df.groupby(["competition", "season"]).size())