from __future__ import annotations

import io
from datetime import date

import pandas as pd

from .db import ACCOUNT_COLS, Db
from .eligibility import Screen, screen_account
from .timeline import PROFILES, blocked_by, status
from .util import parse_date

CSV_TEMPLATE_COLS = ACCOUNT_COLS


def csv_template() -> str:
    return ",".join(CSV_TEMPLATE_COLS) + "\n"


def import_accounts(db: Db, data: bytes | str) -> tuple[int, list[str]]:
    """Load accounts from CSV (UTF-8). Returns (rows_loaded, errors)."""
    text = data.decode("utf-8-sig") if isinstance(data, bytes) else data
    df = pd.read_csv(io.StringIO(text), dtype=str).fillna("")
    errors: list[str] = []
    n = 0
    for i, row in df.iterrows():
        try:
            rec = {c: row.get(c, "") for c in ACCOUNT_COLS}
            if not rec["account_no"].strip() or not rec["borrower"].strip():
                raise ValueError("account_no and borrower are required")
            for c in ("limit_amt", "outstanding", "security_value", "principal_plus_interest", "interest_rate"):
                rec[c] = float(str(rec[c]).replace(",", "")) if str(rec[c]).strip() else None
            for c in ("as_on", "npa_date"):
                d = parse_date(rec[c])
                rec[c] = d.isoformat() if d else None
            rec["is_npa"] = 0 if str(rec["is_npa"]).strip().lower() in ("0", "n", "no", "false") else 1
            rec["cersai_done"] = 1 if str(rec["cersai_done"]).strip().lower() in ("1", "y", "yes", "true") else 0
            db.upsert_account(rec)
            n += 1
        except Exception as e:  # report per-row, keep going
            errors.append(f"Row {i + 2}: {e}")
    return n, errors


def screen(acc: dict) -> Screen:
    return screen_account(
        is_npa=bool(acc.get("is_npa")), security_type=acc.get("security_type") or "",
        outstanding=acc.get("outstanding") or 0, principal_plus_interest=acc.get("principal_plus_interest"),
        security_interest_created=bool((acc.get("security_type") or "").strip()))


def accounts_table(db: Db) -> pd.DataFrame:
    rows = []
    cases = {c["account_no"] for c in db.cases()}
    for a in db.accounts():
        s = screen(a)
        rows.append({**a, "sarfaesi_applicable": s.applicable, "screen_notes": "; ".join(s.reasons),
                     "case_open": a["account_no"] in cases})
    return pd.DataFrame(rows)


def case_view(db: Db, account_no: str, today: date | None = None) -> list[dict]:
    today = today or date.today()
    acc = db.account(account_no)
    case = db.case(account_no)
    if not acc or not case:
        return []
    npa = parse_date(acc["npa_date"])
    if not npa:
        raise ValueError("Account has no NPA date; set it to compute the timeline.")
    steps = PROFILES[case["profile"]]
    done = db.steps(account_no)
    done_keys = set(done)
    out = []
    for s in steps:
        d = parse_date(done[s.key]["done_on"]) if s.key in done else None
        out.append({
            "key": s.key, "title": s.title, "day": s.outer if case["outer_limits"] and s.outer else s.day,
            "due": s.due(npa, bool(case["outer_limits"])), "done_on": d,
            "status": status(s, npa, d, today, bool(case["outer_limits"])),
            "formats": list(s.formats), "note": s.note, "blocked_by": blocked_by(s, done_keys),
            "remark": done[s.key]["remark"] if s.key in done else "",
        })
    return out


def load_demo(db: Db):
    today = date.today()
    from datetime import timedelta
    def d(n): return (today - timedelta(days=n)).isoformat()
    demo = [
        dict(account_no="DEMO-0001", borrower="Sunrise Traders (Demo)", constitution="Proprietorship",
             address="12 MG Road, Pune 411001", email="", mobile="9000000001", guarantors="Demo Guarantor One, 5 Lake View, Pune",
             branch="Pune Camp", branch_sol="0101", ro="Pune RO", zo="Pune ZO", facility="Cash Credit",
             limit_amt=2500000, outstanding=3456789.5, as_on=d(5), npa_date=d(40), is_npa=1,
             security_type="Residential property", security_desc="Flat 4B, Sunrise Apartments, MG Road, Pune",
             security_value=4000000, principal_plus_interest=3300000, interest_rate=10.5, cersai_done=1),
        dict(account_no="DEMO-0002", borrower="Kaveri Engineering (Demo)", constitution="Partnership",
             address="Plot 7, MIDC, Nashik 422007", email="", mobile="9000000002", guarantors="Demo Partner A; Demo Partner B",
             branch="Nashik Main", branch_sol="0102", ro="Pune RO", zo="Pune ZO", facility="Term Loan",
             limit_amt=8000000, outstanding=7200000, as_on=d(5), npa_date=d(100), is_npa=1,
             security_type="Industrial property + P&M", security_desc="Plot 7, MIDC Nashik with factory shed and machinery",
             security_value=9000000, principal_plus_interest=7000000, interest_rate=11, cersai_done=1),
        dict(account_no="DEMO-0003", borrower="Green Fields Farm (Demo)", constitution="Individual",
             address="Village Wadgaon", email="", mobile="", guarantors="", branch="Satara", branch_sol="0103",
             ro="Pune RO", zo="Pune ZO", facility="Crop Loan", limit_amt=900000, outstanding=950000, as_on=d(5),
             npa_date=d(200), is_npa=1, security_type="Agricultural land", security_desc="Agri land survey 44",
             security_value=1500000, principal_plus_interest=900000, interest_rate=7, cersai_done=0),
        dict(account_no="DEMO-0004", borrower="Quick Cards (Demo)", constitution="Individual", address="Pune",
             email="", mobile="", guarantors="", branch="Pune Camp", branch_sol="0101", ro="Pune RO", zo="Pune ZO",
             facility="Personal Loan", limit_amt=300000, outstanding=280000, as_on=d(5), npa_date=d(150), is_npa=1,
             security_type="Unsecured", security_desc="", security_value=0, principal_plus_interest=270000,
             interest_rate=14, cersai_done=0),
    ]
    for r in demo:
        db.upsert_account(r)
    db.upsert_agent("BC1001", "Demo BC One (DRA certified)", "9000000011", True, "0101")
    db.upsert_agent("BC1002", "Demo BC Two (not DRA certified)", "9000000012", False, "0102")
