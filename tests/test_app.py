from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_searches_non_trout_player_from_selector():
    app_path = Path(__file__).parents[1] / "app.py"
    app = AppTest.from_file(str(app_path))

    app.run(timeout=30)

    assert len(app.selectbox) == 1
    app.selectbox[0].select("judgeaa01")
    app.button[0].click().run(timeout=30)

    assert not app.exception
    assert not app.error
    assert any("Aaron Judge" in element.value for element in app.markdown)


def test_styles_current_streamlit_combobox_markup_for_contrast():
    app_source = (Path(__file__).parents[1] / "app.py").read_text(encoding="utf-8")

    assert '.stSelectbox div[role="group"]' in app_source
    assert '.stSelectbox input[role="combobox"]' in app_source
