from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS accounts (
  account_no TEXT PRIMARY KEY, borrower TEXT NOT NULL, constitution TEXT, address TEXT, email TEXT, mobile TEXT,
  guarantors TEXT, branch TEXT, branch_sol TEXT, ro TEXT, zo TEXT, facility TEXT,
  limit_amt REAL DEFAULT 0, outstanding REAL DEFAULT 0, as_on TEXT, npa_date TEXT, is_npa INTEGER DEFAULT 1,
  security_type TEXT, security_desc TEXT, security_value REAL DEFAULT 0, principal_plus_interest REAL,
  interest_rate REAL, cersai_done INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS agents (
  bc_id TEXT PRIMARY KEY, name TEXT NOT NULL, mobile TEXT, dra_certified INTEGER DEFAULT 0,
  branch_sol TEXT, active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS allocations (
  bc_id TEXT NOT NULL, account_no TEXT NOT NULL, allocated_on TEXT, PRIMARY KEY (bc_id, account_no));
CREATE TABLE IF NOT EXISTS recoveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT, bc_id TEXT NOT NULL, account_no TEXT NOT NULL, amount REAL NOT NULL,
  address TEXT, mobile TEXT, consent INTEGER NOT NULL, receipt_no TEXT, recorded_at TEXT,
  posted INTEGER DEFAULT 0, posted_on TEXT);
CREATE TABLE IF NOT EXISTS cases (
  account_no TEXT PRIMARY KEY, profile TEXT NOT NULL, started_on TEXT, authorized_officer TEXT,
  designation TEXT, outer_limits INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS case_steps (
  account_no TEXT NOT NULL, step_key TEXT NOT NULL, done_on TEXT, remark TEXT, PRIMARY KEY (account_no, step_key));
CREATE TABLE IF NOT EXISTS notices (
  id INTEGER PRIMARY KEY AUTOINCREMENT, account_no TEXT NOT NULL, format_key TEXT NOT NULL, issued_on TEXT,
  addressee TEXT, mode TEXT, tracking_no TEXT, remark TEXT);
"""

ACCOUNT_COLS = ["account_no", "borrower", "constitution", "address", "email", "mobile", "guarantors", "branch",
                "branch_sol", "ro", "zo", "facility", "limit_amt", "outstanding", "as_on", "npa_date", "is_npa",
                "security_type", "security_desc", "security_value", "principal_plus_interest", "interest_rate",
                "cersai_done"]


class Db:
    def __init__(self, path: str | Path = ":memory:"):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(str(path), check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.con.executescript(SCHEMA)

    # ---- generic
    def q(self, sql: str, args=()) -> list[dict]:
        return [dict(r) for r in self.con.execute(sql, args).fetchall()]

    def x(self, sql: str, args=()):
        cur = self.con.execute(sql, args)
        self.con.commit()
        return cur

    # ---- settings
    def get_setting(self, k: str, default: str = "") -> str:
        r = self.q("SELECT v FROM settings WHERE k=?", (k,))
        return r[0]["v"] if r else default

    def set_setting(self, k: str, v: str):
        self.x("INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, v))

    # ---- accounts
    def upsert_account(self, rec: dict):
        row = {c: rec.get(c) for c in ACCOUNT_COLS}
        cols = ",".join(ACCOUNT_COLS)
        ph = ",".join("?" * len(ACCOUNT_COLS))
        upd = ",".join(f"{c}=excluded.{c}" for c in ACCOUNT_COLS if c != "account_no")
        self.x(f"INSERT INTO accounts({cols}) VALUES({ph}) ON CONFLICT(account_no) DO UPDATE SET {upd}",
               [row[c] for c in ACCOUNT_COLS])

    def accounts(self) -> list[dict]:
        return self.q("SELECT * FROM accounts ORDER BY account_no")

    def account(self, account_no: str) -> dict | None:
        r = self.q("SELECT * FROM accounts WHERE account_no=?", (account_no,))
        return r[0] if r else None

    # ---- agents
    def upsert_agent(self, bc_id: str, name: str, mobile: str, dra: bool, branch_sol: str, active: bool = True):
        self.x("""INSERT INTO agents(bc_id,name,mobile,dra_certified,branch_sol,active) VALUES(?,?,?,?,?,?)
                  ON CONFLICT(bc_id) DO UPDATE SET name=excluded.name, mobile=excluded.mobile,
                  dra_certified=excluded.dra_certified, branch_sol=excluded.branch_sol, active=excluded.active""",
               (bc_id, name, mobile, int(dra), branch_sol, int(active)))

    def agents(self) -> list[dict]:
        return self.q("SELECT * FROM agents ORDER BY bc_id")

    def allocate(self, bc_id: str, account_no: str):
        """Only DRA-certified, active agents may be allocated accounts (per BC module SOP)."""
        ag = self.q("SELECT * FROM agents WHERE bc_id=?", (bc_id,))
        if not ag:
            raise ValueError(f"Unknown BC {bc_id}")
        if not ag[0]["dra_certified"] or not ag[0]["active"]:
            raise PermissionError("BC is not DRA-certified/active: not eligible for recovery service.")
        if not self.account(account_no):
            raise ValueError(f"Unknown account {account_no}")
        self.x("INSERT OR IGNORE INTO allocations(bc_id,account_no,allocated_on) VALUES(?,?,?)",
               (bc_id, account_no, date.today().isoformat()))

    def allocated_accounts(self, bc_id: str) -> list[dict]:
        return self.q("""SELECT a.* FROM accounts a JOIN allocations l ON l.account_no=a.account_no
                         WHERE l.bc_id=? ORDER BY a.account_no""", (bc_id,))

    # ---- recoveries
    def record_recovery(self, bc_id: str, account_no: str, amount: float, address: str, mobile: str,
                        consent: bool) -> dict:
        if not consent:
            raise ValueError("Consent is required to proceed with payment.")
        if amount <= 0:
            raise ValueError("Recovery amount must be positive.")
        if not self.q("SELECT 1 FROM allocations WHERE bc_id=? AND account_no=?", (bc_id, account_no)):
            raise PermissionError("Account is not allocated to this BC.")
        ag = self.q("SELECT * FROM agents WHERE bc_id=?", (bc_id,))[0]
        if not ag["dra_certified"] or not ag["active"]:
            raise PermissionError("BC is not DRA-certified/active.")
        now = datetime.now()
        cur = self.x("""INSERT INTO recoveries(bc_id,account_no,amount,address,mobile,consent,recorded_at)
                        VALUES(?,?,?,?,?,1,?)""", (bc_id, account_no, amount, address, mobile, now.isoformat(timespec="seconds")))
        rid = cur.lastrowid
        receipt = f"RCP-{now:%Y%m%d}-{rid:06d}"
        self.x("UPDATE recoveries SET receipt_no=? WHERE id=?", (receipt, rid))
        return self.q("SELECT * FROM recoveries WHERE id=?", (rid,))[0]

    def mark_posted(self, rec_id: int):
        self.x("UPDATE recoveries SET posted=1, posted_on=? WHERE id=?", (date.today().isoformat(), rec_id))

    def payment_report(self, start: str | None = None, end: str | None = None) -> list[dict]:
        sql = """SELECT g.bc_id AS "BC ID", g.name AS "BC Name", r.account_no AS "Account Number",
                        r.amount AS "Recovery Amount", a.branch AS "Associated Branch", a.ro AS "RO", a.zo AS "ZO",
                        r.receipt_no AS "Receipt", substr(r.recorded_at,1,10) AS "Date",
                        CASE r.posted WHEN 1 THEN 'Posted to loan a/c' ELSE 'Pending at branch' END AS "Status"
                 FROM recoveries r JOIN agents g ON g.bc_id=r.bc_id JOIN accounts a ON a.account_no=r.account_no
                 WHERE 1=1"""
        args: list = []
        if start:
            sql += " AND substr(r.recorded_at,1,10)>=?"
            args.append(start)
        if end:
            sql += " AND substr(r.recorded_at,1,10)<=?"
            args.append(end)
        return self.q(sql + " ORDER BY r.recorded_at", args)

    # ---- cases
    def start_case(self, account_no: str, profile: str, officer: str, designation: str, outer: bool, started_on: date):
        self.x("""INSERT INTO cases(account_no,profile,started_on,authorized_officer,designation,outer_limits)
                  VALUES(?,?,?,?,?,?) ON CONFLICT(account_no) DO UPDATE SET profile=excluded.profile,
                  authorized_officer=excluded.authorized_officer, designation=excluded.designation,
                  outer_limits=excluded.outer_limits""",
               (account_no, profile, started_on.isoformat(), officer, designation, int(outer)))

    def case(self, account_no: str) -> dict | None:
        r = self.q("SELECT * FROM cases WHERE account_no=?", (account_no,))
        return r[0] if r else None

    def cases(self) -> list[dict]:
        return self.q("SELECT * FROM cases ORDER BY account_no")

    def step_done(self, account_no: str, key: str, done_on: date | None, remark: str = ""):
        if done_on is None:
            self.x("DELETE FROM case_steps WHERE account_no=? AND step_key=?", (account_no, key))
        else:
            self.x("""INSERT INTO case_steps(account_no,step_key,done_on,remark) VALUES(?,?,?,?)
                      ON CONFLICT(account_no,step_key) DO UPDATE SET done_on=excluded.done_on, remark=excluded.remark""",
                   (account_no, key, done_on.isoformat(), remark))

    def steps(self, account_no: str) -> dict[str, dict]:
        return {r["step_key"]: r for r in self.q("SELECT * FROM case_steps WHERE account_no=?", (account_no,))}

    # ---- notices
    def log_notice(self, account_no: str, format_key: str, addressee: str = "", mode: str = "",
                   tracking_no: str = "", remark: str = "", issued_on: date | None = None):
        self.x("""INSERT INTO notices(account_no,format_key,issued_on,addressee,mode,tracking_no,remark)
                  VALUES(?,?,?,?,?,?,?)""", (account_no, format_key, (issued_on or date.today()).isoformat(),
                                             addressee, mode, tracking_no, remark))

    def notices(self, account_no: str | None = None) -> list[dict]:
        if account_no:
            return self.q("SELECT * FROM notices WHERE account_no=? ORDER BY id DESC", (account_no,))
        return self.q("SELECT * FROM notices ORDER BY id DESC")
