"""Local data access for the self-contained MLB Streamlit demo."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "playerID",
    "yearID",
    "age",
    "nameFirst",
    "nameLast",
    "wOBA",
    "career_PA",
    "career_injuries",
    "years_left",
]

NUMERIC_COLUMNS = [
    "yearID",
    "age",
    "wOBA",
    "career_PA",
    "career_injuries",
    "years_left",
]


class PlayerNotFoundError(LookupError):
    """Raised when no player matches the requested full name."""


class PlayerOutputUnavailableError(ValueError):
    """Raised when a player's precomputed output is missing."""


def load_player_data(path: str | Path) -> pd.DataFrame:
    """Read and normalize the player-season columns used by the demo."""
    df = pd.read_csv(
        path,
        usecols=REQUIRED_COLUMNS,
        na_values=["NA"],
        low_memory=False,
    )
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    for column in ("nameFirst", "nameLast"):
        df[column] = df[column].astype("string").str.lower().str.strip()
    return df


def build_player_options(df: pd.DataFrame) -> list[tuple[str, str]]:
    """Return sorted player IDs and readable labels for the search control."""
    players = df.copy()
    players["yearID"] = pd.to_numeric(players["yearID"], errors="coerce")
    players = players.dropna(
        subset=["playerID", "nameFirst", "nameLast", "yearID"]
    ).sort_values("yearID")

    latest_names = players.groupby("playerID", as_index=False).tail(1).copy()
    year_spans = players.groupby("playerID")["yearID"].agg(["min", "max"])
    latest_names = latest_names.join(year_spans, on="playerID")
    latest_names["full_name"] = (
        latest_names["nameFirst"].astype(str).str.strip()
        + " "
        + latest_names["nameLast"].astype(str).str.strip()
    ).str.title()
    duplicated_names = latest_names["full_name"].duplicated(keep=False)

    options = []
    for row, is_duplicate in zip(
        latest_names.itertuples(index=False), duplicated_names, strict=True
    ):
        label = row.full_name
        if is_duplicate:
            first_year = int(row.min)
            last_year = int(row.max)
            year_label = (
                str(first_year)
                if first_year == last_year
                else f"{first_year}–{last_year}"
            )
            label = f"{label} ({year_label})"
        options.append((str(row.playerID), label))

    return sorted(options, key=lambda option: (option[1].casefold(), option[0]))


def get_player_record(
    df: pd.DataFrame, first_name: str, last_name: str
) -> dict[str, object]:
    """Return one player's ordered history and latest precomputed output."""
    first = first_name.lower().strip()
    last = last_name.lower().strip()
    first_values = df["nameFirst"].astype("string").str.lower().str.strip()
    last_values = df["nameLast"].astype("string").str.lower().str.strip()
    matches = df[(first_values == first) & (last_values == last)].copy()

    if matches.empty:
        raise PlayerNotFoundError(f"No player found for {first_name} {last_name}")

    matches["yearID"] = pd.to_numeric(matches["yearID"], errors="coerce")
    matches = matches.dropna(subset=["yearID"])
    if matches.empty:
        raise PlayerNotFoundError(f"No season data found for {first_name} {last_name}")

    most_recent_year = matches["yearID"].max()
    selected_player_id = str(
        matches.loc[matches["yearID"] == most_recent_year, "playerID"].iloc[-1]
    )
    player_df = matches[matches["playerID"].astype(str) == selected_player_id]
    return _build_player_record(player_df)


def get_player_record_by_id(
    df: pd.DataFrame, player_id: str
) -> dict[str, object]:
    """Return the ordered history for one exact player ID."""
    player_df = df[df["playerID"].astype(str) == str(player_id)].copy()
    if player_df.empty:
        raise PlayerNotFoundError(f"No player found for ID {player_id}")
    return _build_player_record(player_df)


def _build_player_record(player_df: pd.DataFrame) -> dict[str, object]:
    """Build the response-shaped record consumed by the Streamlit UI."""
    player_df = player_df.copy()
    player_df["yearID"] = pd.to_numeric(player_df["yearID"], errors="coerce")
    player_df = player_df.dropna(subset=["yearID"]).sort_values("yearID")
    if player_df.empty:
        raise PlayerNotFoundError("No season data found for this player")

    latest = player_df.iloc[-1]
    display_name = f"{latest['nameFirst']} {latest['nameLast']}"

    prediction = pd.to_numeric(latest["years_left"], errors="coerce")
    if pd.isna(prediction):
        raise PlayerOutputUnavailableError(
            f"No precomputed career output is available for {display_name}"
        )

    history = player_df.copy()
    history["wOBA"] = pd.to_numeric(history["wOBA"], errors="coerce")
    history["career_PA"] = pd.to_numeric(history["career_PA"], errors="coerce")
    history["career_injuries"] = pd.to_numeric(
        history["career_injuries"], errors="coerce"
    ).fillna(0)
    history = history.dropna(subset=["yearID", "wOBA"])

    career_history = [
        {
            "yearID": int(row.yearID),
            "age": None if pd.isna(row.age) else float(row.age),
            "wOBA": float(row.wOBA),
            "career_PA": 0.0 if pd.isna(row.career_PA) else float(row.career_PA),
            "career_injuries": float(row.career_injuries),
        }
        for row in history.itertuples(index=False)
    ]
    if not career_history:
        raise PlayerOutputUnavailableError(
            f"No chartable career history is available for {display_name}"
        )

    latest_season = int(latest["yearID"])
    prediction_value = max(0.0, float(prediction))
    latest_age = pd.to_numeric(latest["age"], errors="coerce")
    selected_player_id = str(latest["playerID"])

    return {
        "playerID": selected_player_id,
        "nameFirst": str(latest["nameFirst"]),
        "nameLast": str(latest["nameLast"]),
        "seasons_played": int(len(player_df)),
        "latest_season": latest_season,
        "latest_age": None if pd.isna(latest_age) else float(latest_age),
        "prediction": prediction_value,
        "estimated_final_season": int(latest_season + prediction_value),
        "career_history": career_history,
    }
