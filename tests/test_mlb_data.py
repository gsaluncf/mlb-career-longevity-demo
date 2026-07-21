from pathlib import Path

import pandas as pd
import pytest

from mlb_data import (
    PlayerNotFoundError,
    PlayerOutputUnavailableError,
    get_player_record,
    load_player_data,
)


def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "playerID": "old01",
                "yearID": 2000,
                "age": 25,
                "nameFirst": "sam",
                "nameLast": "lee",
                "wOBA": 0.310,
                "career_PA": 100,
                "career_injuries": 0,
                "years_left": 2,
            },
            {
                "playerID": "new01",
                "yearID": 2022,
                "age": 27,
                "nameFirst": "sam",
                "nameLast": "lee",
                "wOBA": 0.330,
                "career_PA": 400,
                "career_injuries": 1,
                "years_left": 4,
            },
            {
                "playerID": "new01",
                "yearID": 2023,
                "age": 28,
                "nameFirst": "sam",
                "nameLast": "lee",
                "wOBA": 0.340,
                "career_PA": 800,
                "career_injuries": 2,
                "years_left": 3,
            },
        ]
    )


def test_lookup_is_case_insensitive_and_selects_most_recent_identity():
    result = get_player_record(sample_data(), " SAM ", "Lee")

    assert result["playerID"] == "new01"
    assert result["prediction"] == 3.0
    assert [row["yearID"] for row in result["career_history"]] == [2022, 2023]


def test_unknown_player_raises_not_found():
    with pytest.raises(PlayerNotFoundError):
        get_player_record(sample_data(), "missing", "player")


def test_missing_latest_output_raises_clear_error():
    data = sample_data()
    data.loc[data["yearID"] == 2023, "years_left"] = pd.NA

    with pytest.raises(PlayerOutputUnavailableError):
        get_player_record(data, "sam", "lee")


def test_checked_in_dataset_supports_demo_lookup():
    csv_path = Path(__file__).parents[1] / "sdm2_cum_inj.csv"
    df = load_player_data(csv_path)

    result = get_player_record(df, "mike", "trout")

    assert result["seasons_played"] > 0
    assert result["prediction"] >= 0
    assert result["career_history"]
