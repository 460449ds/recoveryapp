"""Screening of whether an NPA account can be taken up under the SARFAESI Act.

This is a first-pass screen using the exclusions in section 31 of the Act as recalled by the
author, not the 2017 circular. The Authorized Officer / Law Division must confirm.
"""
from __future__ import annotations

from dataclasses import dataclass

NON_ENFORCEABLE_SECURITY = {"agricultural land", "unsecured", "none"}


@dataclass
class Screen:
    applicable: bool
    reasons: list[str]  # why not (when not applicable) or points to confirm (when applicable)


def screen_account(*, is_npa: bool, security_type: str, outstanding: float,
                   principal_plus_interest: float | None = None,
                   security_interest_created: bool = True) -> Screen:
    why_not: list[str] = []
    st = (security_type or "").strip().lower()
    if not is_npa:
        why_not.append("Account is not classified NPA.")
    if not security_interest_created or st in {"unsecured", "none", ""}:
        why_not.append("No security interest created in favour of the Bank.")
    if st == "agricultural land":
        why_not.append("Agricultural land is excluded from the Act (s.31).")
    if outstanding <= 100_000:
        why_not.append("Dues do not exceed Rs.1 lakh (s.31 exclusion).")
    if principal_plus_interest and principal_plus_interest > 0 and outstanding < 0.2 * principal_plus_interest:
        why_not.append("Dues are below 20% of principal and interest (s.31 exclusion).")
    if why_not:
        return Screen(False, why_not)
    return Screen(True, [
        "Confirm the mortgage/hypothecation is valid and CERSAI registration is done.",
        "Confirm limitation (12 years) and that no stay/DRT order is in force.",
    ])
