"""SARFAESI action timeline. Day 1 = date the account became NPA.

Two profiles are offered because the two source documents differ:
  * "circular_2017": PNB Recovery Division Circular 31/2017 work-flow chart (detailed, step by step)
  * "portal_2026": the 2026-27 portal spec windows (coarser)
Each step: key, title, due offset in days (Day N means NPA date + N - 1), linked format keys, owner.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass(frozen=True)
class Step:
    key: str
    title: str
    day: int                       # statutory/standard target day (Day 1 = NPA date)
    outer: int | None = None       # alternate outer-limit day, where the circular gives two
    formats: tuple[str, ...] = ()
    note: str = ""
    depends_on: tuple[str, ...] = field(default=())

    def due(self, npa_date: date, outer: bool = False) -> date:
        d = self.outer if (outer and self.outer) else self.day
        return npa_date + timedelta(days=d - 1)


CIRCULAR_2017 = [
    Step("sanction", "Branch Head's note and administrative sanction (SI-2)", 1, None, ("SI-2",)),
    Step("demand", "Issue 60-day demand notice u/s 13(2) to borrowers, guarantors, mortgagors", 2, 4,
         ("SI-4", "SI-4A"), "Send to all addresses by more than one mode; include s.13(8) redemption clause."),
    Step("service", "Confirm service; track post and e-mail; substituted service if unserved", 9, 11,
         (), "Track on India Post; affix and publish in two newspapers if service failed.", ("demand",)),
    Step("reply_3a", "Reply to any s.13(3A) representation (statutory limit 15 days from receipt)", 69, 71,
         ("REPLY-13-3A",), "Reasoned reply mandatory. No possession notice before this reply.", ("demand",)),
    Step("agency", "Engage supporting agency; pre-possession survey report", 69, 71, (),
         "Circle Head/ZM permission; consortium accounts need 60% consent."),
    Step("pre_possession", "Pre-possession notice to deliver possession (SI-6)", 69, 71, ("SI-6",),
         "Check no stay from DRT/Court.", ("service", "reply_3a")),
    Step("possession", "Take possession u/s 13(4) (10 days after SI-6) with panchnama/inventory", 79, 81,
         ("SI-7A", "SI-7B", "SI-7C", "SI-7D", "SI-10"), "Photograph/video affixation; keep witnesses.", ("pre_possession",)),
    Step("sec14", "File s.14 application before DM/CMM for physical possession", 90, 92, ("SEC14",),
         "Circular para 14.9 advises filing together with the 13(4) notice.", ("possession",)),
    Step("publish_possession", "Publish possession notice in two newspapers (within 7 days of possession)", 82, 84,
         ("SI-10", "SI-10A", "SI-10B"), "Immovables only; one vernacular paper.", ("possession",)),
    Step("valuation", "Valuation by Board-approved valuer", 82, 84, (), "Report normally not older than 1 year."),
    Step("reserve_price", "Reserve price and mode of sale fixed by COCESI / ZM", 84, 86, (), "COCESI finalises within 2 days.",
         ("valuation",)),
    Step("sale_notice", "30-day sale notice to borrower; public notice published and affixed", 87, 89,
         ("SI-13", "SI-14"), "Also load on bank website and tenders.gov.in; 30 days before auction.", ("reserve_price",)),
    Step("auction", "Auction / tender opening; 25% deposit same or next working day", 121, 123, (),
         "Check no stay; reserve price floor.", ("sale_notice",)),
    Step("confirmation", "Committee of Officers confirms sale (immovables) - within 15 days", 136, 138, (),
         "Not needed for movables.", ("auction",)),
    Step("balance", "Balance 75% received (15 days from confirmation; up to 3 months if agreed in writing)", 136, 138,
         (), "", ("confirmation",)),
    Step("certificate", "Certificate of Sale issued (on full payment and delivery)", 138, None, ("SI-15", "SI-17"),
         "Circular gives no day; placeholder at balance-payment day.", ("balance",)),
    Step("appropriation", "Appropriate proceeds: costs, principal, interest, surplus", 140, None, (),
         "Circular gives no day; placeholder. Update SARFAESI portal.",
         ("certificate",)),
]

PORTAL_2026 = [
    Step("cersai", "Verify CERSAI registration", 1, None, (), "Portal 2026-27 policy."),
    Step("demand", "Issue Section 13(2) notice", 7, None, ("SI-4", "SI-4A")),
    Step("service", "Complete notice service / publication and pasting if returned unserved", 15, None, (), "", ("demand",)),
    Step("possession", "Constructive possession; publish possession notice (7 days); file s.14 application",
         90, None, ("SI-7A", "SI-7B", "SI-7C", "SI-7D", "SI-10", "SEC14"), "Window: Day 76 to 90.", ("service",)),
    Step("sale_notice", "Issue 30-day sale notice under Rule 8(6) / 6(2)", 100, None, ("SI-13", "SI-14"),
         "Window: Day 91 to 100.", ("possession",)),
    Step("physical", "Physical possession via CMM/DM/CJM order", 130, None, (), "Window: Day 100 to 130.", ("possession",)),
    Step("eauction", "E-auction notice publication and execution", 165, None, (), "Window: Day 131 to 165.", ("sale_notice",)),
]

PROFILES = {
    "Circular 31/2017 (detailed)": CIRCULAR_2017,
    "Portal 2026-27 policy (windows)": PORTAL_2026,
}


def status(step: Step, npa_date: date, done_on: date | None, today: date, outer: bool = False) -> str:
    if done_on:
        return "Done"
    due = step.due(npa_date, outer)
    if today > due:
        return "Overdue"
    if (due - today).days <= 3:
        return "Due soon"
    return "Pending"


def blocked_by(step: Step, done: set[str]) -> list[str]:
    return [d for d in step.depends_on if d not in done]
