# Player Selector and Framed Layout Design

## Goal

Make the deployed MLB demo easier to use and visually contained. Every selectable player must resolve successfully, and all text inside interactive controls must remain legible across supported browsers.

## Player Selection

Replace the separate first-name and last-name text fields with one searchable Streamlit select control populated from the cached local dataset. Each option will carry a stable player ID and a readable title-cased full name. When duplicate full names exist, the displayed label will include an identifying active-year range so users can distinguish them without exposing raw implementation details.

The existing **Search Player** button remains. Selecting a name does not render the charts until the user presses the button. The current lookup result structure, player card, verdict, and charts remain unchanged.

## Cross-Browser Control Contrast

Style the complete select-control surface rather than relying on Streamlit or browser defaults. CSS will explicitly set:

- a dark background for the select input and dropdown menu;
- light text for the selected value, typed search text, placeholder, and options;
- a visible border and focus state;
- a contrasting highlighted/hovered option state.

Selectors will target Streamlit/BaseWeb attributes and roles that are stable enough for the current component structure. The app will retain a native readable fallback if Streamlit changes its generated class names.

## Framed Layout

Change the main Streamlit block container from full-bleed width to a centered application panel. On desktop it will use a maximum width near 1,440 pixels, approximately 24 pixels of outer margin, a subtle border, rounded corners, overflow clipping, and a restrained shadow. The surrounding page background will be darker than the panel.

Responsive CSS will reduce the outer margin and corner radius on narrow screens so content remains usable without horizontal scrolling. Existing internal section spacing remains unchanged.

## Data Flow

1. The cached CSV loader prepares the player-season DataFrame once.
2. A pure helper derives sorted player selector options and their player IDs.
3. Streamlit displays the searchable selector.
4. On button press, the selected player ID retrieves the exact player's history and precomputed `years_left` output.
5. Existing rendering code displays the result.

## Error Handling

- The selector begins with an unselected placeholder and the button prompts the user to choose a player when needed.
- Player-ID lookup prevents same-name careers from being mixed.
- If cached data is missing or malformed, the existing local-data error treatment remains.
- If a selected player lacks usable output or chart history, the existing clear data-availability error remains.

## Verification and Deployment

- Add unit tests for sorted selector options, duplicate-name labels, and exact player-ID lookup.
- Add a Streamlit interaction check that selects and renders Aaron Judge, proving the UI is not Mike-Trout-specific.
- Run the full unit suite, Python compilation, Streamlit health check, and browser/AppTest interaction.
- Push the verified branch to `gsaluncf/mlb-career-longevity-demo` on `main`.
- Confirm Streamlit automatically redeploys, then verify the public Aaron Judge result and control contrast visually.
