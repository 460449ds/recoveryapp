"""NPA Recovery Tracker: SARFAESI case workflow, notice formats and BC/DRA agent recovery tracking."""
from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from recovery.db import Db
from recovery.formats import FORMATS, MANUAL_FORMS, OBJECTIONS
from recovery.render import (DEFAULT_BANK, DEFAULT_HQ, base_context, merge, resolve_defaults, to_docx, to_text)
from recovery.service import accounts_table, case_view, csv_template, import_accounts, load_demo, screen
from recovery.timeline import PROFILES
from recovery.util import inr, parse_date

st.set_page_config(page_title="NPA Recovery Tracker", page_icon="📋", layout="wide")


@st.cache_resource
def get_db() -> Db:
    return Db(os.environ.get("RECOVERY_DB", "data/recovery.db"))


db = get_db()
settings = {k: db.get_setting(k) for k in ("bank_name", "bank_hq", "officer", "designation")}

PAGES = ["Dashboard", "Accounts", "SARFAESI case", "Notices & formats", "Agents & recovery", "Reference", "Settings"]
page = st.sidebar.radio("Module", PAGES)
st.sidebar.caption("Timelines and formats: Recovery Division Circular 31/2017. "
                   "Agent flow: SAM Instruction Circular 101314-2025 (BC NPA Recovery module).")

STATUS_ICON = {"Done": "✅", "Overdue": "🔴", "Due soon": "🟠", "Pending": "⚪"}


def applicable_accounts() -> list[dict]:
    return [a for a in db.accounts() if screen(a).applicable]


def account_label(a: dict) -> str:
    return f"{a['account_no']} - {a['borrower']}"


# --------------------------------------------------------------------------- Dashboard
if page == "Dashboard":
    st.title("NPA Recovery Tracker")
    accts = db.accounts()
    if not accts:
        st.info("No accounts yet. Go to **Accounts** to upload the allocated NPA account list (CSV) "
                "or load demo data.")
    appl = applicable_accounts()
    cases = db.cases()
    overdue_rows = []
    for c in cases:
        try:
            for r in case_view(db, c["account_no"]):
                if r["status"] in ("Overdue", "Due soon"):
                    acc = db.account(c["account_no"])
                    overdue_rows.append({"Account": c["account_no"], "Borrower": acc["borrower"], "Step": r["title"],
                                         "Due": r["due"], "Status": f"{STATUS_ICON[r['status']]} {r['status']}"})
        except ValueError:
            pass
    rec_total = sum(r["Recovery Amount"] for r in db.payment_report())
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("NPA accounts", len(accts))
    c2.metric("SARFAESI applicable", len(appl))
    c3.metric("Cases running", len(cases))
    c4.metric("Steps overdue / due soon", len(overdue_rows))
    c5.metric("Recovered via BCs (Rs.)", inr(rec_total))
    st.subheader("Actions needing attention")
    if overdue_rows:
        st.dataframe(pd.DataFrame(overdue_rows).sort_values("Due"), use_container_width=True, hide_index=True)
    else:
        st.write("Nothing overdue.")
    pending = [r for r in db.payment_report() if r["Status"] == "Pending at branch"]
    if pending:
        st.subheader("BC recoveries awaiting posting to the loan account")
        st.dataframe(pd.DataFrame(pending), use_container_width=True, hide_index=True)

# --------------------------------------------------------------------------- Accounts
elif page == "Accounts":
    st.title("NPA accounts")
    left, right = st.columns([2, 1])
    with left:
        up = st.file_uploader("Upload allocated NPA accounts (CSV)", type="csv")
        if up is not None and st.button("Import file"):
            n, errs = import_accounts(db, up.getvalue())
            st.success(f"Imported {n} account(s).")
            for e in errs:
                st.warning(e)
    with right:
        st.download_button("Download CSV template", csv_template(), "accounts_template.csv", "text/csv")
        if st.button("Load demo data (fictional)"):
            load_demo(db)
            st.success("Demo accounts and BCs loaded.")
    df = accounts_table(db)
    if df.empty:
        st.info("No accounts loaded.")
    else:
        only = st.checkbox("Show only SARFAESI-applicable accounts", value=True)
        view = df[df["sarfaesi_applicable"]] if only else df
        show = ["account_no", "borrower", "branch", "ro", "zo", "outstanding", "npa_date", "security_type",
                "sarfaesi_applicable", "case_open", "screen_notes"]
        st.dataframe(view[show], use_container_width=True, hide_index=True)
        st.caption("Applicability is a first-pass screen (NPA, security interest, agricultural land, Rs.1 lakh and "
                   "20% exclusions under s.31). The Authorized Officer must confirm before action.")
    with st.expander("Add or edit one account"):
        with st.form("acct"):
            c1, c2, c3 = st.columns(3)
            ano = c1.text_input("Account no.")
            bor = c2.text_input("Borrower")
            con = c3.text_input("Constitution", "Proprietorship")
            addr = st.text_input("Borrower address")
            guar = st.text_input("Guarantors/mortgagors (name, address; separate several with ';')")
            c1, c2, c3, c4 = st.columns(4)
            br, sol, ro, zo = c1.text_input("Branch"), c2.text_input("Branch SOL"), c3.text_input("RO"), c4.text_input("ZO")
            c1, c2, c3 = st.columns(3)
            fac = c1.text_input("Facility", "Cash Credit")
            lim = c2.number_input("Limit (Rs.)", 0.0, step=10000.0)
            out = c3.number_input("Outstanding (Rs.)", 0.0, step=10000.0)
            c1, c2, c3 = st.columns(3)
            npa = c1.date_input("NPA date (Day 1)", date.today() - timedelta(days=30))
            sec = c2.selectbox("Security type", ["Residential property", "Commercial property", "Industrial property",
                                                 "Plant & machinery", "Stock/book debts", "Vehicle",
                                                 "Agricultural land", "Unsecured"])
            ppi = c3.number_input("Principal + interest (Rs.), for 20% test", 0.0, step=10000.0)
            sdesc = st.text_area("Security description (as in mortgage/hypothecation deed)")
            cer = st.checkbox("CERSAI registration verified")
            if st.form_submit_button("Save account") and ano and bor:
                db.upsert_account(dict(account_no=ano, borrower=bor, constitution=con, address=addr, guarantors=guar,
                                       branch=br, branch_sol=sol, ro=ro, zo=zo, facility=fac, limit_amt=lim,
                                       outstanding=out, as_on=date.today().isoformat(), npa_date=npa.isoformat(),
                                       is_npa=1, security_type=sec, security_desc=sdesc, security_value=0,
                                       principal_plus_interest=ppi or None, cersai_done=int(cer)))
                st.success("Saved.")

# --------------------------------------------------------------------------- Case
elif page == "SARFAESI case":
    st.title("SARFAESI case tracker")
    appl = applicable_accounts()
    if not appl:
        st.info("No SARFAESI-applicable accounts. Load accounts first.")
        st.stop()
    sel = st.selectbox("Account", appl, format_func=account_label)
    acc = db.account(sel["account_no"])
    case = db.case(acc["account_no"])
    npa = parse_date(acc["npa_date"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Outstanding (Rs.)", inr(acc["outstanding"]))
    c2.metric("NPA date (Day 1)", npa.strftime("%d.%m.%Y") if npa else "not set")
    c3.metric("Day count", (date.today() - npa).days + 1 if npa else "-")
    c4.metric("CERSAI verified", "Yes" if acc["cersai_done"] else "No")
    if not npa:
        st.error("Set the NPA date on the Accounts page.")
        st.stop()
    if not case:
        st.subheader("Start SARFAESI action")
        with st.form("startcase"):
            prof = st.selectbox("Timeline", list(PROFILES), help="The two source documents give different windows.")
            off = st.text_input("Authorized Officer", settings["officer"])
            des = st.text_input("Designation", settings["designation"] or "Chief Manager")
            outer = st.checkbox("Use outer-limit days (e.g. Day 4 instead of Day 2)")
            if st.form_submit_button("Start case"):
                db.start_case(acc["account_no"], prof, off, des, outer, date.today())
                st.rerun()
        st.stop()
    st.caption(f"Timeline: {case['profile']} | Authorized Officer: {case['authorized_officer']}, {case['designation']}")
    rows = case_view(db, acc["account_no"])
    st.dataframe(pd.DataFrame([{
        "": STATUS_ICON[r["status"]], "Day": r["day"], "Due": r["due"], "Step": r["title"], "Status": r["status"],
        "Done on": r["done_on"], "Forms": ", ".join(r["formats"]),
        "Waiting on": ", ".join(r["blocked_by"]) if r["status"] != "Done" else "", "Note": r["note"]} for r in rows]),
        use_container_width=True, hide_index=True)
    st.subheader("Update a step")
    step = st.selectbox("Step", rows, format_func=lambda r: f"Day {r['day']}: {r['title']}")
    cc1, cc2, cc3 = st.columns([1, 2, 1])
    done_on = cc1.date_input("Completed on", step["done_on"] or date.today(), key=f"d_{step['key']}")
    remark = cc2.text_input("Remark / reference", step["remark"], key=f"r_{step['key']}")
    if step["blocked_by"] and not step["done_on"]:
        st.warning("Earlier steps not yet done: " + ", ".join(step["blocked_by"]))
    b1, b2 = st.columns(2)
    if b1.button("Mark done"):
        db.step_done(acc["account_no"], step["key"], done_on, remark)
        st.rerun()
    if step["done_on"] and b2.button("Undo"):
        db.step_done(acc["account_no"], step["key"], None)
        st.rerun()
    if step["formats"]:
        st.info("Formats for this step: " + ", ".join(step["formats"]) + ". Generate them under **Notices & formats**.")
    st.subheader("Notices issued on this account")
    n = db.notices(acc["account_no"])
    st.dataframe(pd.DataFrame(n) if n else pd.DataFrame(columns=["format_key", "issued_on"]),
                 use_container_width=True, hide_index=True)

# --------------------------------------------------------------------------- Formats
elif page == "Notices & formats":
    st.title("Notices and formats")
    accts = db.accounts()
    if not accts:
        st.info("Load accounts first.")
        st.stop()
    only = st.checkbox("SARFAESI-applicable accounts only", value=True)
    pool = applicable_accounts() if only else accts
    sel = st.selectbox("Account", pool, format_func=account_label)
    acc = db.account(sel["account_no"])
    case = db.case(acc["account_no"])
    stages = sorted({f.stage for f in FORMATS.values()}, key=lambda s: [f.stage for f in FORMATS.values()].index(s))
    stage = st.selectbox("Stage", ["All"] + stages)
    options = [f for f in FORMATS.values() if stage in ("All", f.stage)]
    fmt = st.selectbox("Format", options, format_func=lambda f: f"{f.key} - {f.title}")
    st.caption(f"Source: {fmt.source}")
    if fmt.draft:
        st.warning("Draft wording: this form is named in the circular but its text is in the SARFAESI Manual. "
                   "Conform it to the Manual form before issue.")
    ctx = base_context(acc, case, settings)
    defaults = resolve_defaults(fmt, ctx)
    values = {}
    with st.expander("Fill in / adjust fields", expanded=True):
        cols = st.columns(2)
        for i, (key, label, _d) in enumerate(fmt.fields):
            wk = f"{acc['account_no']}|{fmt.key}|{key}"
            with cols[i % 2]:
                if isinstance(defaults[key], bool):
                    values[key] = st.checkbox(label, defaults[key], key=wk)
                elif key in ("point_wise_reply", "time_schedule", "incidents", "property_description"):
                    values[key] = st.text_area(label, defaults[key], key=wk)
                else:
                    values[key] = st.text_input(label, defaults[key], key=wk)
    lines = merge(fmt, ctx, values)
    text = to_text(lines)
    st.text_area("Preview", text, height=360)
    d1, d2, d3 = st.columns(3)
    fname = f"{fmt.key}_{acc['account_no']}"
    d1.download_button("Download Word (.docx)", to_docx(fmt, lines), f"{fname}.docx",
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    d2.download_button("Download text", text, f"{fname}.txt", "text/plain")
    with d3.popover("Log as issued"):
        who = st.text_input("Addressee", acc["borrower"])
        mode = st.selectbox("Mode", ["Registered Post AD", "Speed Post", "Courier", "Hand delivery", "E-mail",
                                     "Affixation", "Newspaper publication"])
        trk = st.text_input("Tracking / consignment no.")
        rem = st.text_input("Remark")
        if st.button("Save to notice register"):
            db.log_notice(acc["account_no"], fmt.key, who, mode, trk, rem)
            st.success("Logged.")
    st.subheader("Notice register")
    n = db.notices(None)
    st.dataframe(pd.DataFrame(n) if n else pd.DataFrame(columns=["account_no", "format_key", "issued_on"]),
                 use_container_width=True, hide_index=True)
    with st.expander("Forms named in the circular but kept in the SARFAESI Manual 2008"):
        st.table(pd.DataFrame([{"Form": k, "Purpose": v} for k, v in MANUAL_FORMS.items()]))

# --------------------------------------------------------------------------- Agents
elif page == "Agents & recovery":
    st.title("BC / DRA agents and recovery")
    st.caption("Per the BC mobile-app NPA Recovery module SOP: only DRA-certified BCs get accounts, the BC enters amount, "
               "address and mobile with consent, a receipt is generated, the amount sits in 285/946000 Sundry Deposit "
               "A/c NPA Recovery of the linked branch, and the branch user credits the loan account through NPATM.")
    t1, t2, t3, t4 = st.tabs(["BC master", "Allocate accounts", "Record & post recovery", "Payment report"])
    with t1:
        with st.form("bc"):
            c1, c2, c3, c4 = st.columns(4)
            bid, bname = c1.text_input("BC ID / code"), c2.text_input("BC name")
            bmob, bsol = c3.text_input("Mobile"), c4.text_input("Linked branch SOL")
            dra = st.checkbox("DRA certified by IIBF")
            act = st.checkbox("Active", True)
            if st.form_submit_button("Save BC") and bid and bname:
                db.upsert_agent(bid, bname, bmob, dra, bsol, act)
        ag = db.agents()
        if ag:
            st.dataframe(pd.DataFrame(ag), use_container_width=True, hide_index=True)
    with t2:
        ags = [a for a in db.agents()]
        if not ags:
            st.info("Add a BC first.")
        else:
            bc = st.selectbox("BC", ags, format_func=lambda a: f"{a['bc_id']} - {a['name']}")
            only = st.checkbox("SARFAESI-applicable accounts only", True, key="alloc_only")
            pool = applicable_accounts() if only else db.accounts()
            if bc["branch_sol"]:
                pool = [a for a in pool if not a["branch_sol"] or a["branch_sol"] == bc["branch_sol"]] or pool
            picks = st.multiselect("Accounts", pool, format_func=account_label)
            if st.button("Allocate") and picks:
                try:
                    for a in picks:
                        db.allocate(bc["bc_id"], a["account_no"])
                    st.success(f"Allocated {len(picks)} account(s).")
                except PermissionError as e:
                    st.error(str(e))
            st.write("Currently allocated:")
            st.dataframe(pd.DataFrame(db.allocated_accounts(bc["bc_id"]))[["account_no", "borrower", "branch", "outstanding"]]
                         if db.allocated_accounts(bc["bc_id"]) else pd.DataFrame(), use_container_width=True, hide_index=True)
    with t3:
        ags = [a for a in db.agents() if a["dra_certified"] and a["active"]]
        if not ags:
            st.info("No DRA-certified active BC. Not eligible for recovery service.")
        else:
            bc = st.selectbox("BC logged in", ags, format_func=lambda a: f"{a['bc_id']} - {a['name']}", key="rec_bc")
            al = db.allocated_accounts(bc["bc_id"])
            if not al:
                st.info("No accounts allocated to this BC.")
            else:
                with st.form("rec"):
                    ac = st.selectbox("Account", al, format_func=account_label)
                    amt = st.number_input("Recovery amount (Rs.)", 0.0, step=500.0)
                    addr = st.text_input("Address where recovery made")
                    mob = st.text_input("Borrower mobile number")
                    ok = st.checkbox("Consent: I confirm the amount entered is correct and proceed with payment")
                    if st.form_submit_button("Proceed payment"):
                        try:
                            r = db.record_recovery(bc["bc_id"], ac["account_no"], amt, addr, mob, ok)
                            st.success(f"Recorded. Receipt {r['receipt_no']} - give to customer as proof of payment.")
                        except (ValueError, PermissionError) as e:
                            st.error(str(e))
        st.subheader("Branch: post to loan account (NPATM)")
        pend = [r for r in db.q("SELECT * FROM recoveries WHERE posted=0 ORDER BY id")]
        if not pend:
            st.write("Nothing pending.")
        for r in pend:
            c1, c2 = st.columns([4, 1])
            c1.write(f"{r['receipt_no']} | A/c {r['account_no']} | Rs.{inr(r['amount'])} | BC {r['bc_id']}")
            if c2.button("Mark posted", key=f"post{r['id']}"):
                db.mark_posted(r["id"])
                st.rerun()
    with t4:
        c1, c2 = st.columns(2)
        s = c1.date_input("From", date.today().replace(day=1))
        e = c2.date_input("To", date.today())
        rep = db.payment_report(s.isoformat(), e.isoformat())
        if rep:
            dfr = pd.DataFrame(rep)
            st.dataframe(dfr, use_container_width=True, hide_index=True)
            st.metric("Total recovered (Rs.)", inr(dfr["Recovery Amount"].sum()))
            st.download_button("Download report (CSV)", dfr.to_csv(index=False), "bc_payment_report.csv", "text/csv")
            st.caption("For verification and release of BC payments by the RO/ZO as per the Recovery Management Policy.")
        else:
            st.write("No recoveries in this period.")

# --------------------------------------------------------------------------- Reference
elif page == "Reference":
    st.title("Reference")
    t1, t2, t3 = st.tabs(["Timeline", "Replying to objections (Annexure-5)", "Reserve price benchmark"])
    with t1:
        for name, steps in PROFILES.items():
            st.subheader(name)
            st.dataframe(pd.DataFrame([{"Day": f"{s.day}" + (f" / {s.outer}" if s.outer else ""), "Step": s.title,
                                        "Forms": ", ".join(s.formats), "Note": s.note} for s in steps]),
                         use_container_width=True, hide_index=True)
        pdf = Path("docs/SARFAESI_Recovery_Timeline_and_Document_Register.pdf")
        if pdf.exists():
            st.download_button("Download printable timeline and document register (PDF)", pdf.read_bytes(), pdf.name,
                               "application/pdf")
    with t2:
        st.dataframe(pd.DataFrame(OBJECTIONS, columns=["Possible objection", "How the Bank should reply"]),
                     use_container_width=True, hide_index=True)
        st.caption("Reply within 15 days of receipt. A reasoned reply is required, not a ritual rejection "
                   "(Mardia Chemicals, SC 08.04.2004).")
    with t3:
        st.caption("First-auction reserve price benchmark from the 2026-27 portal policy.")
        cat = {"Vacant land / house / flat / commercial property": 0.85, "Tenanted / leased / litigated property": 0.75,
               "Hypothecated vehicles": 0.65, "Hypothecated stock": 0.60, "Plant & machinery / furniture": 0.50,
               "Book debts / receivables": 0.30}
        c = st.selectbox("Asset category", list(cat))
        fmv = st.number_input("Fair market value per valuer (Rs. lakh)", 0.0, step=1.0)
        st.metric("First auction reserve price (Rs. lakh)", f"{fmv * cat[c]:.2f}")

# --------------------------------------------------------------------------- Settings
else:
    st.title("Settings")
    with st.form("set"):
        bn = st.text_input("Bank name used in formats", settings["bank_name"] or DEFAULT_BANK)
        hq = st.text_area("Head office address", settings["bank_hq"] or DEFAULT_HQ)
        of = st.text_input("Default Authorized Officer", settings["officer"])
        ds = st.text_input("Default designation", settings["designation"] or "Chief Manager")
        if st.form_submit_button("Save"):
            for k, v in (("bank_name", bn), ("bank_hq", hq), ("officer", of), ("designation", ds)):
                db.set_setting(k, v)
            st.success("Saved.")
    st.caption("The circular's annexures name Punjab National Bank; the merge fields above replace that name. "
               "Data is stored in a local SQLite file (RECOVERY_DB, default data/recovery.db).")
