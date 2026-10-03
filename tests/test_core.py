from datetime import date

import pytest

from recovery.db import Db
from recovery.eligibility import screen_account
from recovery.formats import FORMATS
from recovery.render import base_context, merge, resolve_defaults, to_docx, to_text
from recovery.service import accounts_table, case_view, import_accounts, load_demo
from recovery.timeline import CIRCULAR_2017, status
from recovery.util import amount_in_words, inr


def test_words_and_inr():
    assert amount_in_words(100000) == "Rupees One Lakh Only"
    assert amount_in_words(1234567.5).endswith("Fifty Paise Only")
    assert inr(1234567) == "12,34,567.00"


def test_screening():
    assert screen_account(is_npa=True, security_type="Residential property", outstanding=500000).applicable
    assert not screen_account(is_npa=True, security_type="Agricultural land", outstanding=500000).applicable
    assert not screen_account(is_npa=True, security_type="Residential property", outstanding=50000).applicable
    assert not screen_account(is_npa=False, security_type="Residential property", outstanding=500000).applicable
    assert not screen_account(is_npa=True, security_type="Residential property", outstanding=100000,
                              principal_plus_interest=1000000).applicable


def test_timeline_dates():
    s = {x.key: x for x in CIRCULAR_2017}
    npa = date(2026, 1, 1)
    assert s["demand"].due(npa) == date(2026, 1, 2)           # Day 2 (Day 1 = NPA date)
    assert s["demand"].due(npa, outer=True) == date(2026, 1, 4)  # Day 4
    assert s["possession"].due(npa) == date(2026, 3, 20)      # Day 79
    assert status(s["demand"], npa, None, date(2026, 2, 1)) == "Overdue"
    assert status(s["demand"], npa, date(2026, 1, 2), date(2026, 2, 1)) == "Done"


def test_import_and_case_flow():
    db = Db()
    csv = "account_no,borrower,outstanding,npa_date,security_type,is_npa\nA1,Acme,500000,2026-01-01,Residential property,1\n,NoNo,1,,,\n"
    n, errs = import_accounts(db, csv)
    assert n == 1 and len(errs) == 1
    db.start_case("A1", "Circular 31/2017 (detailed)", "Officer", "Chief Manager", False, date.today())
    rows = case_view(db, "A1", date(2026, 1, 10))
    assert rows[0]["key"] == "sanction" and rows[0]["status"] == "Overdue"
    db.step_done("A1", "sanction", date(2026, 1, 1))
    assert case_view(db, "A1", date(2026, 1, 10))[0]["status"] == "Done"
    pre = next(r for r in case_view(db, "A1") if r["key"] == "pre_possession")
    assert "service" in pre["blocked_by"]


def test_agents_rules():
    db = Db()
    load_demo(db)
    db.allocate("BC1001", "DEMO-0001")
    with pytest.raises(PermissionError):
        db.allocate("BC1002", "DEMO-0001")       # not DRA certified
    with pytest.raises(PermissionError):
        db.record_recovery("BC1001", "DEMO-0002", 1000, "addr", "9", True)  # not allocated
    with pytest.raises(ValueError):
        db.record_recovery("BC1001", "DEMO-0001", 1000, "addr", "9", False)  # no consent
    r = db.record_recovery("BC1001", "DEMO-0001", 2500.0, "addr", "9000", True)
    assert r["receipt_no"].startswith("RCP-")
    rep = db.payment_report()
    assert rep[0]["BC ID"] == "BC1001" and rep[0]["RO"] == "Pune RO" and rep[0]["Status"] == "Pending at branch"
    db.mark_posted(r["id"])
    assert db.payment_report()[0]["Status"] == "Posted to loan a/c"


def test_all_formats_render():
    db = Db()
    load_demo(db)
    acc = db.account("DEMO-0001")
    ctx = base_context(acc, None, {})
    for key, fmt in FORMATS.items():
        vals = resolve_defaults(fmt, ctx)
        lines = merge(fmt, ctx, vals)
        assert to_text(lines).strip(), key
        assert to_docx(fmt, lines)[:2] == b"PK", key
    t = to_text(merge(FORMATS["SI-4"], ctx, resolve_defaults(FORMATS["SI-4"], ctx)))
    assert "Sunrise Traders" in t and "sub-section (8) of section 13" in t and "60 days (sixty days)" in t


def test_accounts_table_flags_applicable():
    db = Db()
    load_demo(db)
    df = accounts_table(db).set_index("account_no")
    assert df.loc["DEMO-0001", "sarfaesi_applicable"] and df.loc["DEMO-0002", "sarfaesi_applicable"]
    assert not df.loc["DEMO-0003", "sarfaesi_applicable"] and not df.loc["DEMO-0004", "sarfaesi_applicable"]
