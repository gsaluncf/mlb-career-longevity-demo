# MLB Player Selector and Framed Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace unrestricted player-name text entry with a guaranteed-valid searchable selector and contain the existing Streamlit UI in a responsive framed panel with explicit cross-browser control contrast.

**Architecture:** Extend the pure `mlb_data.py` service with selector-option generation and exact player-ID lookup, then have `app.py` render those options through one Streamlit selectbox. Keep the existing result structure and charts, and implement the frame and control contrast entirely through the app's existing CSS layer.

**Tech Stack:** Python, pandas, Streamlit, Plotly, pytest, Streamlit AppTest

## Global Constraints

- Preserve the existing hero, player card, verdict, and Plotly charts.
- Every displayed player option must resolve to exactly one player ID.
- Selected values, typed search text, placeholders, dropdown options, and focus states must remain legible across browsers.
- Use a centered panel near 1,440 pixels maximum width with approximately 24 pixels of desktop margin and reduced mobile spacing.
- Continue using the checked-in CSV and precomputed `years_left` output with no secrets or external API.
- Push verified changes to `gsaluncf/mlb-career-longevity-demo` on `main` for automatic Streamlit redeployment.

---

### Task 1: Player Selector Data Interfaces

**Files:**
- Modify: `mlb_data.py`
- Modify: `tests/test_mlb_data.py`

**Interfaces:**
- Produces: `build_player_options(df: pandas.DataFrame) -> list[tuple[str, str]]`, where each tuple is `(player_id, display_label)`.
- Produces: `get_player_record_by_id(df: pandas.DataFrame, player_id: str) -> dict[str, object]`.
- Preserves: `get_player_record(df, first_name, last_name) -> dict[str, object]` for compatibility.

- [ ] **Step 1: Write failing option and player-ID tests**

Add tests that require alphabetically sorted labels, year ranges for duplicate full names, and exact player-ID lookup:

```python
def test_player_options_are_sorted_and_disambiguate_duplicate_names():
    options = build_player_options(sample_data())
    assert options == [
        ("old01", "Sam Lee (2000)"),
        ("new01", "Sam Lee (2022–2023)"),
    ]


def test_player_id_lookup_returns_exact_identity():
    result = get_player_record_by_id(sample_data(), "old01")
    assert result["playerID"] == "old01"
    assert result["latest_season"] == 2000
```

Import `build_player_options` and `get_player_record_by_id` at the top of the test module.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `python -m pytest tests/test_mlb_data.py -v`

Expected: collection fails because the two new functions are not defined.

- [ ] **Step 3: Implement the minimal selector interfaces**

Implement `build_player_options` by grouping normalized rows by `playerID`, selecting the latest name, calculating minimum and maximum valid `yearID`, detecting full-name collisions across IDs, and adding a single year or en-dash year range only to collided labels. Sort returned tuples by case-folded label and then player ID.

Implement `get_player_record_by_id` by exact string comparison on `playerID`, raising `PlayerNotFoundError` when absent, and routing the selected rows through a shared private record-building helper extracted from the existing function. Preserve name-based lookup behavior.

- [ ] **Step 4: Run the full unit suite and verify GREEN**

Run: `python -m pytest -v`

Expected: all existing and new tests pass.

- [ ] **Step 5: Commit the data interfaces**

```powershell
git add -- mlb_data.py tests/test_mlb_data.py
git commit -m "feat: add searchable player selector data"
```

### Task 2: Searchable Control and Framed Streamlit Layout

**Files:**
- Modify: `app.py`
- Test: `tests/test_mlb_data.py`

**Interfaces:**
- Consumes: `build_player_options(df) -> list[tuple[str, str]]`.
- Consumes: `get_player_record_by_id(df, player_id) -> dict[str, object]`.

- [ ] **Step 1: Add the selector to the Streamlit app**

Import the new helpers, derive `player_ids` and `player_labels` from cached data, and replace the two text inputs with:

```python
selected_player_id = st.selectbox(
    "SELECT PLAYER",
    options=player_ids,
    index=None,
    placeholder="Start typing a player name…",
    format_func=player_labels.get,
)
```

Keep the existing button. On click, call `get_player_record_by_id(cached_player_data(), selected_player_id)`. If the button is clicked without a selection, show `Please select a player.`

- [ ] **Step 2: Add explicit cross-browser select contrast**

Extend the existing CSS with selectors covering `div[data-baseweb="select"]`, its `input`, its placeholder pseudo-element, `div[role="listbox"]`, and `div[role="option"]`. Set dark backgrounds, `color` and `-webkit-text-fill-color` to the existing light palette, a visible border/focus state, and contrasting hover/selected option backgrounds.

- [ ] **Step 3: Add the responsive application frame**

Change the outer page to a darker background and style `.block-container` with `width: calc(100% - 48px)`, `max-width: 1440px`, `margin: 24px auto`, zero internal container padding, a subtle border, `border-radius: 12px`, `overflow: hidden`, and a restrained shadow. Add a media query below 700px using `width: calc(100% - 16px)`, `margin: 8px auto`, and a smaller radius.

- [ ] **Step 4: Verify a non-Trout interaction locally**

Run a Streamlit AppTest that loads `app.py`, selects `judgeaa01`, clicks **SEARCH PLAYER**, and asserts there are no exceptions or error elements and that the rendered markdown contains `Aaron Judge`.

Run:

```powershell
python -m pytest -v
python -m py_compile app.py mlb_data.py
```

Expected: all tests pass and compilation exits successfully.

- [ ] **Step 5: Commit the UI change**

```powershell
git add -- app.py
git commit -m "feat: add player selector and framed layout"
```

### Task 3: Deployment and Public Verification

**Files:**
- Modify only if verification exposes a tested defect.

**Interfaces:**
- Consumes: Git remote `deployment` tracking `gsaluncf/mlb-career-longevity-demo`.
- Produces: updated `main` deployment at `https://mlb-career-longevity-demo.streamlit.app/`.

- [ ] **Step 1: Run final local verification**

```powershell
python -m pytest -v
python -m py_compile app.py mlb_data.py
git diff --check
git status --short
```

Expected: tests and compilation pass, diff check is clean, and the worktree has no unintended changes.

- [ ] **Step 2: Push the verified branch**

Run: `git push deployment HEAD:main`

Expected: GitHub accepts the new commits and Streamlit begins an automatic redeployment.

- [ ] **Step 3: Verify the public redeployment**

Open `https://mlb-career-longevity-demo.streamlit.app/`, confirm the centered frame and readable select text, select Aaron Judge, click **SEARCH PLAYER**, and confirm the profile and chart section headings render without an error alert.

- [ ] **Step 4: Preserve the deployment worktree**

Keep branch `codex/self-contained-streamlit` and its worktree in place for further grading adjustments; do not merge it into the student's `origin` or delete it.
