# Self-Contained Streamlit Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the MLB Career Longevity Predictor deployable as a self-contained Streamlit app using the checked-in CSV and its precomputed `years_left` output.

**Architecture:** Add a small pure-Python data module for loading, normalizing, and querying player-season data. Keep Streamlit rendering in `app.py`, wrap dataset loading with `st.cache_data`, and feed the existing UI a response-shaped local result so the visual code changes minimally.

**Tech Stack:** Python, pandas, Streamlit, Plotly, pytest

## Global Constraints

- Preserve the existing Streamlit page, player card, verdict, and Plotly charts.
- Use the latest selected player-season row's `years_left` value as a precomputed output, not live model inference.
- Require no secrets, EC2 service, FastAPI service, S3 bucket, or trained model at runtime.
- Load `sdm2_cum_inj.csv` relative to `app.py` and cache the prepared DataFrame with `st.cache_data`.
- Keep the deployment entry point as `app.py`.

---

## File Structure

- Create `mlb_data.py`: pure dataset loading, normalization, player selection, validation, and response construction.
- Create `tests/test_mlb_data.py`: focused unit tests for lookup behavior and data errors.
- Modify `app.py`: cached local loading, lookup integration, robust chart inputs, and accurate demo wording.
- Modify `requirements.txt`: remove the unused HTTP client and include the test dependency used by verification.
- Modify `README.md`: document the self-contained demo and Streamlit deployment path while preserving the original project architecture as historical context.

### Task 1: Local Player Data Service

**Files:**
- Create: `mlb_data.py`
- Create: `tests/test_mlb_data.py`

**Interfaces:**
- Produces: `load_player_data(path: str | Path) -> pandas.DataFrame`
- Produces: `get_player_record(df: pandas.DataFrame, first_name: str, last_name: str) -> dict[str, object]`
- Produces: `PlayerNotFoundError` and `PlayerOutputUnavailableError`

- [ ] **Step 1: Write failing lookup and error tests**

Create a compact fixture with mixed-case input, two player IDs sharing a name, multiple seasons, and one record with missing `years_left`. Assert that lookup is case-insensitive, selects the player ID with the most recent season, returns ordered career history, raises `PlayerNotFoundError` for an unknown name, and raises `PlayerOutputUnavailableError` when the selected latest output is missing.

```python
import pandas as pd
import pytest

from mlb_data import (
    PlayerNotFoundError,
    PlayerOutputUnavailableError,
    get_player_record,
)


def sample_data():
    return pd.DataFrame([
        {"playerID": "old01", "yearID": 2000, "age": 25, "nameFirst": "sam", "nameLast": "lee", "wOBA": .310, "career_PA": 100, "career_injuries": 0, "years_left": 2},
        {"playerID": "new01", "yearID": 2022, "age": 27, "nameFirst": "sam", "nameLast": "lee", "wOBA": .330, "career_PA": 400, "career_injuries": 1, "years_left": 4},
        {"playerID": "new01", "yearID": 2023, "age": 28, "nameFirst": "sam", "nameLast": "lee", "wOBA": .340, "career_PA": 800, "career_injuries": 2, "years_left": 3},
    ])


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
```

- [ ] **Step 2: Run the tests and verify the expected failure**

Run: `python -m pytest tests/test_mlb_data.py -v`

Expected: collection fails with `ModuleNotFoundError: No module named 'mlb_data'`.

- [ ] **Step 3: Implement the minimal data service**

Implement the declared exceptions and functions. `load_player_data` must use an explicit required-column list, `na_values=["NA"]`, numeric coercion for chart/output columns, and lowercase stripped name columns. `get_player_record` must normalize query text, find exact full-name matches, select the `playerID` present on the maximum matching `yearID`, sort that identity's seasons, validate the latest `years_left`, and return the keys already consumed by the UI:

```python
{
    "playerID": str,
    "nameFirst": str,
    "nameLast": str,
    "seasons_played": int,
    "latest_season": int,
    "latest_age": float,
    "prediction": float,
    "estimated_final_season": int,
    "career_history": list[dict[str, int | float]],
}
```

Career history must omit rows without a valid `yearID` or `wOBA`, sort ascending, and fill missing cumulative injuries with zero.

- [ ] **Step 4: Run the focused tests and verify they pass**

Run: `python -m pytest tests/test_mlb_data.py -v`

Expected: all tests pass.

- [ ] **Step 5: Commit the data service**

```powershell
git add -- mlb_data.py tests/test_mlb_data.py
git commit -m "feat: add local MLB player data service"
```

### Task 2: Cached Streamlit Integration

**Files:**
- Modify: `app.py`
- Modify: `requirements.txt`
- Test: `tests/test_mlb_data.py`

**Interfaces:**
- Consumes: `load_player_data(path) -> DataFrame`
- Consumes: `get_player_record(df, first_name, last_name) -> dict`
- Consumes: `PlayerNotFoundError` and `PlayerOutputUnavailableError`

- [ ] **Step 1: Add a failing real-dataset integration test**

Add a test that loads the repository CSV, looks up Mike Trout, and asserts a non-empty ordered career history and a numeric precomputed output:

```python
from pathlib import Path
from mlb_data import load_player_data


def test_checked_in_dataset_supports_demo_lookup():
    df = load_player_data(Path(__file__).parents[1] / "sdm2_cum_inj.csv")
    result = get_player_record(df, "mike", "trout")
    assert result["seasons_played"] > 0
    assert result["prediction"] >= 0
    assert result["career_history"]
```

- [ ] **Step 2: Run the integration test before wiring Streamlit**

Run: `python -m pytest tests/test_mlb_data.py::test_checked_in_dataset_supports_demo_lookup -v`

Expected: PASS if the loader contract is correct; otherwise correct only the data service until it passes.

- [ ] **Step 3: Replace HTTP lookup with cached local lookup**

In `app.py`, remove `requests` and `API_URL`, import `Path` and the data-service interfaces, and add:

```python
@st.cache_data(show_spinner="Loading player history…")
def cached_player_data():
    return load_player_data(Path(__file__).with_name("sdm2_cum_inj.csv"))
```

Inside the search handler, replace `requests.get(...)` and `response.json()` with:

```python
data = get_player_record(cached_player_data(), first_name, last_name)
```

Catch `PlayerNotFoundError` and `PlayerOutputUnavailableError` separately for friendly user messages. Keep a final exception handler for missing/malformed file errors, using `st.error` without exposing a remote-API label.

- [ ] **Step 4: Make displayed claims match the cached output**

Change the hero badge and footer from live Random Forest prediction wording to “Precomputed Project Output” or equivalent. Keep the historical model metrics only where clearly marked as original-project context. Replace the API spinner text with local career-data wording.

- [ ] **Step 5: Remove the unused HTTP dependency and run checks**

Remove `requests` from `requirements.txt`; add `pytest` so a fresh environment can run the documented tests. Run:

```powershell
python -m pytest -v
python -m py_compile app.py mlb_data.py
```

Expected: all tests pass and compilation exits successfully.

- [ ] **Step 6: Commit the working application**

```powershell
git add -- app.py requirements.txt tests/test_mlb_data.py
git commit -m "feat: run Streamlit demo from cached local data"
```

### Task 3: Deployment Documentation and Smoke Test

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: Streamlit entry point `app.py`
- Consumes: runtime files `requirements.txt` and `sdm2_cum_inj.csv`

- [ ] **Step 1: Update the README run and deployment instructions**

Document these exact local commands:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Document Streamlit Community Cloud setup: connect the repository, select `app.py`, deploy without secrets, and ensure `sdm2_cum_inj.csv` is committed. Explain that the current demo uses cached local data and the recorded `years_left` output while the EC2/S3/MLflow diagram describes the original student architecture.

- [ ] **Step 2: Run a bounded Streamlit smoke test**

Start Streamlit headlessly on an unused local port, poll `/_stcore/health`, and terminate the process after a successful response:

```powershell
$process = Start-Process python -ArgumentList '-m','streamlit','run','app.py','--server.headless=true','--server.port=8765' -PassThru -WindowStyle Hidden
try { Invoke-WebRequest 'http://localhost:8765/_stcore/health' -UseBasicParsing } finally { Stop-Process -Id $process.Id }
```

Expected: HTTP 200 with body `ok`.

- [ ] **Step 3: Run final verification**

```powershell
python -m pytest -v
python -m py_compile app.py mlb_data.py
git diff --check
git status --short
```

Expected: tests pass, compilation and diff check succeed, and status contains only the intended README/plan changes before commit.

- [ ] **Step 4: Commit deployment documentation**

```powershell
git add -- README.md docs/superpowers/plans/2026-07-21-self-contained-streamlit-demo.md
git commit -m "docs: explain self-contained Streamlit deployment"
```
