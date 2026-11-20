from pathlib import Path
import pandas as pd

# Creating paths of root and processed, and tag columns
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"

TAG_COLS = ["under_pressure", "shot_first_time", "shot_one_on_one", "shot_open_goal", "shot_aerial_won", 
            "shot_deflected", "shot_follows_dribble", "shot_redirect"]

def clean_shots(df):
    log = {"raw": len(df)}

    # Drop penalty shootout shots
    df = df[df["period"] != 5].copy()
    log["after_shootouts"] = len(df)

    is_pen = df["shot_type"] == "Penalty"
    pens, df = df[is_pen].copy(), df[~is_pen].copy()
    log["penalties"] = len(pens)

    for d in (df, pens):
        d["x"] = d["location"].str[0].clip(upper = 120)
        d["y"] = d["location"].str[1]
        d["is_goal"] = d["shot_outcome"] == "Goal"

    # Keeps True as True, makes NaN False
    for c in TAG_COLS:
        if c in df:
            df[c] = df[c].eq(True)

    log["model_shots"] = len(df)
    return df, pens, log

# Checks to stop script if something is wrong instead of failing later on
def check(df):
    assert df["location"].notna().all(), "missing locations"
    assert df["x"].between(0, 120).all() and df["y"].between(0, 80).all(), "shots off pitch"
    assert not df["id"].duplicated().any(), "duplicate shot ID's"
    assert (df["period"] != 5).all() and (df["shot_type"] != "Penalty").all(), "pens/shootouts left"

# Block of code to run script properly
if __name__ == "__main__":
    raw = pd.read_parquet(PROC / "shots.parquet")
    shots, pens, log = clean_shots(raw)
    check(shots)
    shots.to_parquet(PROC / "shots_clean.parquet", index = False)
    pens.to_parquet(PROC / "penalties.parquet", index = False)
    print(log)
    print(f"Goal rate: {shots.is_goal.mean():.1%}  \nPenalty conversion: {pens.is_goal.mean():.1%}")