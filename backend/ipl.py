import pandas as pd
import numpy as np
import json
 
# Load datasets
matches = pd.read_csv("IPL_Ball_by_Ball_2008_2022 (1).csv")
balls = pd.read_csv("IPL_Matches_2008_2022.csv")

# Merge datasets
df = pd.merge(matches, balls, on="ID", how="left")

# ------------------ TEAM PERFORMANCE ------------------
def teamAPI(team_name):
    # Matches played by team
    team_matches = balls[(balls["Team1"] == team_name) | (balls["Team2"] == team_name)]
    total_matches = len(team_matches)

    # Wins / Loss / Tie
    wins = (team_matches["WinningTeam"] == team_name).sum()
    losses = ((team_matches["WinningTeam"] != team_name) & (team_matches["WinningTeam"].notna())).sum()
    ties = team_matches[team_matches["WonBy"] == "Tie"].shape[0]

    # Run Rate (BattingTeam only)
    team_batting = df[df["BattingTeam"] == team_name]
    total_runs = team_batting["total_run"].sum()
    total_overs = team_batting["overs"].nunique()
    run_rate = round(total_runs / total_overs, 2) if total_overs > 0 else 0

    # Performance vs other teams
    vs_team = (
        team_matches.groupby("WinningTeam")
        .size()
        .reset_index(name="wins")
    )

    return {
        "team": team_name,
        "total_matches": int(total_matches),
        "wins": int(wins),
        "losses": int(losses),
        "ties": int(ties),
        "run_rate": run_rate,
        "vs_team": vs_team.to_dict(orient="records")
    }

# ------------------ BOWLER PERFORMANCE ------------------
def bowlerAPI(bowler_name):
    bowler_data = df[df["bowler"] == bowler_name]

    total_balls = len(bowler_data)
    total_runs = bowler_data["total_run"].sum()
    wickets = bowler_data[bowler_data["isWicketDelivery"] == 1]["player_out"].count()
    economy = round(total_runs / (total_balls / 6), 2) if total_balls > 0 else 0

    vs_team = (
        bowler_data.groupby("BattingTeam")
        .agg(
            balls_bowled=("ballnumber", "count"),
            runs_conceded=("total_run", "sum"),
            wickets=("player_out", "count")
        )
        .reset_index()
    )

    return {
        "bowler": bowler_name,
        "overall": {
            "balls_bowled": int(total_balls),
            "runs_conceded": int(total_runs),
            "wickets": int(wickets),
            "economy": economy
        },
        "vs_team": vs_team.to_dict(orient="records")
    }

# ------------------ BATSMAN PERFORMANCE ------------------
def batsmanAPI(batsman_name):
    # Filter only this batsman
    bat_data = df[df["batter"] == batsman_name].copy()

    # Derive BowlingTeam = opponent of BattingTeam
    bat_data["BowlingTeam"] = bat_data.apply(
        lambda x: x["Team1"] if x["BattingTeam"] == x["Team2"] else x["Team2"],
        axis=1
    )

    # Overall stats
    total_runs = bat_data["batsman_run"].sum()
    balls_faced = len(bat_data)
    dismissals = bat_data[bat_data["player_out"] == batsman_name].shape[0]
    avg = round(total_runs / dismissals, 2) if dismissals > 0 else total_runs
    strike_rate = round((total_runs / balls_faced) * 100, 2) if balls_faced > 0 else 0

    # Vs Team stats
    vs_team = (
        bat_data.groupby("BowlingTeam")
        .agg(
            runs=("batsman_run", "sum"),
            balls=("ballnumber", "count"),
            dismissals=("player_out", lambda x: (x == batsman_name).sum())
        )
        .reset_index()
    )

    return {
        "batsman": batsman_name,
        "overall": {
            "runs": int(total_runs),
            "balls_faced": int(balls_faced),
            "average": avg,
            "strike_rate": strike_rate
        },
        "vs_team": vs_team.to_dict(orient="records")
    }


# ------------------ ALL BOWLERS ------------------
def allBowlers():
    return json.dumps(sorted(df["bowler"].unique().tolist()))

# ------------------ ALL BATSMEN ------------------
def allBatsmen():
    return json.dumps(sorted(df["batter"].unique().tolist()))
