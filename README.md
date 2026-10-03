# NPA Recovery Tracker

Streamlit app for a recovery desk: SARFAESI case tracking, notice/format generation, and BC (DRA-certified agent) recovery tracking.

| Module | What it does |
|---|---|
| Accounts | Upload the allocated NPA account list (CSV) and screen which accounts are SARFAESI-applicable |
| SARFAESI case | Day-wise timeline from the NPA date (Circular 31/2017, or the 2026-27 portal windows), mark steps done, overdue flags |
| Notices & formats | 20 formats (demand notices, panchnamas, possession notices, supplementary agreements, sale certificates, book-debt notices) merged from account data; Word/text download; notice register |
| Agents & recovery | DRA-certified BCs, account allocation, recovery entry with consent and receipt, branch posting, RO/ZO payment report |
| Reference | Timelines, replies to s.13(3A) objections (Annexure-5), reserve price benchmark |

Formats are transcribed from Recovery Division Circular 31/2017. SI-6 and SI-13 are drafts: the circular names them but their wording is in the SARFAESI Manual. Forms that exist only in the Manual are listed in the app but not reproduced. Set the bank name, head office and default officer under **Settings**.

```
uv sync
uv run streamlit run streamlit_app.py
uv run pytest
```

Data is stored in SQLite (`data/recovery.db`, override with `RECOVERY_DB`). Account CSV columns: see the template download on the Accounts page. `docs/` holds the printable timeline PDF and its generator.
