import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
PAGES = ["Dashboard", "Accounts", "SARFAESI case", "Notices & formats", "Agents & recovery", "Reference", "Settings"]


@pytest.fixture()
def app(monkeypatch, tmp_path):
    monkeypatch.setenv("RECOVERY_DB", str(tmp_path / "t.db"))
    import streamlit as st
    st.cache_resource.clear()
    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30)
    at.run()
    return at


def test_every_page_renders_empty_and_with_demo(app):
    for p in PAGES:
        app.sidebar.radio[0].set_value(p).run()
        assert not app.exception, (p, app.exception)
    app.sidebar.radio[0].set_value("Accounts").run()
    [b for b in app.button if b.label.startswith("Load demo")][0].click().run()
    for p in PAGES:
        app.sidebar.radio[0].set_value(p).run()
        assert not app.exception, (p, app.exception)


def test_case_flow(app):
    app.sidebar.radio[0].set_value("Accounts").run()
    [b for b in app.button if b.label.startswith("Load demo")][0].click().run()
    app.sidebar.radio[0].set_value("SARFAESI case").run()
    sub = [b for b in app.button if b.label == "Start case"][0]
    sub.click().run()
    assert not app.exception
    assert any("Timeline:" in c.value for c in app.caption)
