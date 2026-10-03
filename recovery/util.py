from __future__ import annotations

from datetime import date, datetime

_ONES = ("Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen Fourteen "
         "Fifteen Sixteen Seventeen Eighteen Nineteen").split()
_TENS = "_ _ Twenty Thirty Forty Fifty Sixty Seventy Eighty Ninety".split()


def _below_hundred(n: int) -> str:
    if n < 20:
        return _ONES[n]
    return _TENS[n // 10] + (f" {_ONES[n % 10]}" if n % 10 else "")


def _below_thousand(n: int) -> str:
    if n < 100:
        return _below_hundred(n)
    rest = f" and {_below_hundred(n % 100)}" if n % 100 else ""
    return f"{_ONES[n // 100]} Hundred{rest}"


def amount_in_words(amount: float) -> str:
    """Indian-system words, e.g. 1234567.5 -> 'Rupees Twelve Lakh ... and Fifty Paise Only'."""
    rupees = int(amount)
    paise = int(round((amount - rupees) * 100))
    if paise == 100:
        rupees, paise = rupees + 1, 0
    if rupees == 0 and paise == 0:
        return "Rupees Zero Only"
    parts = []
    for unit, label in ((10_000_000, "Crore"), (100_000, "Lakh"), (1_000, "Thousand")):
        q, rupees = divmod(rupees, unit)
        if q:
            parts.append(f"{_below_hundred(q) if q < 100 else _below_thousand(q)} {label}")
    if rupees:
        parts.append(_below_thousand(rupees))
    words = "Rupees " + " ".join(parts) if parts else "Rupees"
    if paise:
        words += f" and {_below_hundred(paise)} Paise"
    return words + " Only"


def inr(amount: float) -> str:
    """Format with Indian digit grouping: 1234567 -> '12,34,567.00'."""
    neg = amount < 0
    s = f"{abs(amount):.2f}"
    whole, frac = s.split(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        whole = ",".join(groups + [tail])
    return ("-" if neg else "") + whole + "." + frac


def parse_date(v) -> date | None:
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unrecognised date: {v!r}")


def fmt_date(d: date | None) -> str:
    return d.strftime("%d.%m.%Y") if d else ""
