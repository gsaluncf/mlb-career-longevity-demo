# Self-Contained Streamlit Demo Design

## Goal

Make the existing MLB Career Longevity Predictor run reliably on Streamlit Community Cloud without its unavailable EC2 API, S3 bucket, or trained model. Preserve the current presentation and use the checked-in dataset's recorded `years_left` value as the displayed output.

## Scope

- Keep the existing Streamlit page, player card, verdict, and Plotly charts.
- Replace the HTTP player lookup with a local lookup against `sdm2_cum_inj.csv`.
- Cache the parsed dataset with Streamlit so reruns do not repeatedly read and normalize the CSV.
- Treat the latest player-season row's `years_left` value as a precomputed output, not a live model inference.
- Remove unused runtime dependencies on the external FastAPI service and `requests`.
- Update documentation and add focused tests for data loading and player lookup.

Rebuilding or retraining the Random Forest, deploying FastAPI, and reproducing the original AWS/Databricks pipeline are outside this stabilization task.

## Architecture and Components

`app.py` will remain the Streamlit entry point. A small set of pure helper functions will provide clear boundaries:

1. A cached loader reads only the columns needed by the application, converts sentinel `NA` values to missing data, normalizes names, and returns a prepared DataFrame.
2. A player lookup function filters by normalized first and last name, sorts seasons, validates that usable records exist, and converts the rows into the response-shaped structure already consumed by the UI.
3. The existing rendering code consumes that local result, minimizing changes to layout and chart behavior.

Pure lookup logic will be kept separate from Streamlit widgets so it can be tested without starting a web server.

## Data Flow

1. Streamlit starts and loads `sdm2_cum_inj.csv` relative to `app.py`.
2. `st.cache_data` retains the prepared DataFrame across normal Streamlit reruns.
3. The user enters a first and last name and selects **Search Player**.
4. The app finds matching seasons locally and selects the latest season.
5. The latest `years_left` value becomes the displayed years-remaining output; the latest season plus that value becomes the estimated final season.
6. All of the player's season rows feed the existing performance and injury charts.

## Edge Cases and Error Handling

- Searches are case-insensitive and ignore leading or trailing whitespace.
- Unknown players produce a friendly not-found message.
- Missing or unusable `years_left` data produces a clear data-availability message rather than a fabricated result.
- Numeric chart fields are coerced safely; rows without the required season value are excluded.
- Duplicate full names use all exact-name matching records, consistent with the current two-field search interface. If player IDs differ, the most recently active player's records are selected to avoid mixing careers.
- Missing CSV files or malformed data produce an actionable Streamlit error.

## User-Facing Accuracy

Copy that currently claims a live Random Forest prediction will be adjusted to say the app displays a precomputed dataset output. Historical project metrics and architecture may remain in the README as project context, but the current demo path will be explicitly documented as self-contained.

## Verification

- Unit tests will cover successful lookup, case-insensitive names, unknown players, duplicate-name selection, and missing-output handling.
- A syntax/import check will confirm the Streamlit entry point loads.
- A local Streamlit smoke test will confirm the server starts and responds.
- The existing CSV will be queried for at least one known player to confirm the full data-to-display path.

## Deployment

The repository will be deployable on Streamlit Community Cloud with `app.py` as the entry point. The repository, `requirements.txt`, `app.py`, and `sdm2_cum_inj.csv` are the only runtime artifacts required. No secrets or external services are needed.
