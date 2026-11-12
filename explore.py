from statsbombpy import sb  # type: ignore # Ignoring statsbombpy import flag - all works as it should

comps = sb.competitions()
print(comps[['competition_name', 'season_name']])