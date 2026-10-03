"""Build blank, print-ready annexure PDFs for the web page from recovery/formats.py.

Run from the repo root:  python3 web/build_annexure_pdfs.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from recovery.formats import FORMATS, OBJECTIONS
from recovery.render import merge, resolve_defaults

OUT = Path(__file__).parent / "annexures"
ss = getSampleStyleSheet()
BODY = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10, leading=13.5, alignment=4, spaceAfter=5)
CENTER = ParagraphStyle("c", parent=BODY, alignment=1, fontName="Helvetica-Bold", fontSize=11.5, spaceAfter=3)
SUB = ParagraphStyle("s", parent=CENTER, fontSize=10)
RIGHT = ParagraphStyle("r", parent=BODY, alignment=2)
CELL = ParagraphStyle("t", parent=BODY, fontSize=8.5, leading=10.5, alignment=0, spaceAfter=0)
NOTE = ParagraphStyle("n", parent=BODY, fontSize=8, textColor=colors.HexColor("#b00020"), alignment=0)

# blank merge context: every merge field prints as a blank line, except the bank placeholders
CTX = {"bank_name": "[BANK NAME]", "bank_hq": "[HEAD OFFICE ADDRESS]", "today": ""}


def md(t: str) -> str:
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def render(lines, story):
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([Paragraph(md(c.strip()), CELL) for c in lines[i].strip("|").split("|")])
                i += 1
            n = max(len(r) for r in rows)
            rows = [r + [Paragraph("", CELL)] * (n - len(r)) for r in rows]
            t = Table(rows, colWidths=[(A4[0] - 40 * mm) / n] * n, repeatRows=1)
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                                   ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            story += [t, Spacer(1, 6)]
            continue
        i += 1
        if ln.startswith("##"):
            story.append(Paragraph(md(ln[2:].strip()), SUB))
        elif ln.startswith("#"):
            story.append(Paragraph(md(ln[1:].strip()), CENTER))
        elif ln.startswith(">>"):
            story.append(Paragraph(md(ln[2:].strip()), RIGHT))
        elif ln.startswith("** "):
            story.append(Paragraph("<b>" + md(ln[3:].strip()) + "</b>", BODY))
        else:
            story.append(Paragraph(md(ln), BODY))


def build(path: Path, title: str, fn):
    story = []
    fn(story)
    SimpleDocTemplate(str(path), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm,
                      bottomMargin=18 * mm, title=title).build(story)


def form_pdf(key: str, filename: str):
    fmt = FORMATS[key]
    vals = resolve_defaults(fmt, {**CTX})
    # blank every text field (keep checkbox defaults) so the form prints as an empty template
    vals = {k: (v if isinstance(v, bool) else "") for k, v in vals.items()}
    lines = merge(fmt, CTX, vals)

    def fn(story):
        if fmt.draft:
            story.append(Paragraph("DRAFT - wording is not from the circular. Conform to the SARFAESI Manual form "
                                   "before issue.", NOTE))
        render(lines, story)
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"Source: {fmt.source}. Blank template; bank name and fields to be completed.", NOTE))
    build(OUT / filename, fmt.title, fn)


def annexure3(story):
    story += [Paragraph("Annexure-3", RIGHT),
              Paragraph("Tracking of notices sent under Section 13(2) by Registered Post / Speed Post", CENTER)]
    for t in [
        "Normally, notices sent by Registered Post / Speed Post (Acknowledgement Due) are served within a reasonable period of 7 days or so. "
        "Instead of waiting for acknowledgements or undelivered-notice reports, track delivery on the India Post website.",
        "<b>Step 1.</b> Open http://www.indiapost.gov.in/ (the current India Post tracking page).",
        "<b>Step 2.</b> From the menu choose <b>Tools</b>, then <b>Track consignment</b> (Track All Mail Items).",
        "<b>Step 3.</b> Enter the 13-character consignment number (Speed Post / EMS e.g. EE123456789IN; Registered Mail e.g. RX123456789IN) and press <b>Go</b>.",
        "<b>Step 4.</b> The result shows booked at / booked on / delivered at / delivered on. Take a black-and-white print for the file.",
        "<b>Step 5.</b> Click <b>Details</b> for the detailed track events (booked, bagged, despatched, opened, delivered). Print and place in the file.",
        "If not satisfied with the status, a complaint can be lodged on the site; the Post Office is understood to reply within 5 days. "
        "Keep any acknowledgements received. As a precaution, obtain a signed service report from the concerned Post Office and keep it on record."]:
        story.append(Paragraph(t, BODY))


def annexure4(story):
    story += [Paragraph("Annexure-4", RIGHT),
              Paragraph("Tracking of notices sent by e-mail under Section 13(2)", CENTER)]
    for t in [
        "Under Rule 3 of the Security Interest (Enforcement) Rules 2002 the demand notice may be sent by e-mail. Wherever e-mail addresses of the "
        "obligants are available, send the Section 13(2) notice by e-mail also.",
        "Print the e-mail as sent to each obligant and keep it in the file. If Read Receipt / Delivery Receipt is activated, also print the receipt "
        "message: it is the most important document to prove in court that the e-mail was delivered.",
        "<b>To activate receipts in Microsoft Outlook:</b>",
        "<b>Step 1.</b> Tools menu, then <b>Options</b>.",
        "<b>Step 2.</b> Under E-mail, click <b>E-mail Options</b>.",
        "<b>Step 3.</b> Under Message handling, click <b>Tracking Options</b>.",
        "<b>Step 4.</b> Tick <b>Read receipt</b> and/or <b>Delivery receipt</b>.",
        "(Menu names are those of the Outlook version in the circular; newer versions place the option under File > Options > Mail > Tracking.)"]:
        story.append(Paragraph(t, BODY))


def annexure5(story):
    story += [Paragraph("Annexure-5", RIGHT),
              Paragraph("Reply to representation / objections made to the demand notice (guidance)", CENTER),
              Paragraph("Reply within 15 days of receipt (do not wait for the full period). The reply must be reasoned, not a ritual rejection.", BODY)]
    rows = [[Paragraph("<b>S.No.</b>", CELL), Paragraph("<b>Possible objection from borrower/owner</b>", CELL),
             Paragraph("<b>Reply of the Bank: explain with reference to</b>", CELL)]]
    rows += [[Paragraph(str(i), CELL), Paragraph(md(a), CELL), Paragraph(md(b), CELL)] for i, (a, b) in enumerate(OBJECTIONS, 1)]
    t = Table(rows, colWidths=[12 * mm, 70 * mm, 88 * mm], repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee"))]))
    story.append(t)


FILES = {  # filename -> (title, builder)
    "Annexure-01_SI-4_Demand_Notice_Borrower.pdf": lambda: form_pdf("SI-4", "Annexure-01_SI-4_Demand_Notice_Borrower.pdf"),
    "Annexure-02_SI-4A_Demand_Notice_Guarantor.pdf": lambda: form_pdf("SI-4A", "Annexure-02_SI-4A_Demand_Notice_Guarantor.pdf"),
    "Annexure-03_Tracking_Notices_by_Post.pdf": lambda: build(OUT / "Annexure-03_Tracking_Notices_by_Post.pdf", "Annexure-3", annexure3),
    "Annexure-04_Tracking_Notices_by_Email.pdf": lambda: build(OUT / "Annexure-04_Tracking_Notices_by_Email.pdf", "Annexure-4", annexure4),
    "Annexure-05_Reply_to_Objections.pdf": lambda: build(OUT / "Annexure-05_Reply_to_Objections.pdf", "Annexure-5", annexure5),
    "Annexure-06_SI-7A_Panchnama_Possession_Delivered.pdf": lambda: form_pdf("SI-7A", "Annexure-06_SI-7A_Panchnama_Possession_Delivered.pdf"),
    "Annexure-07_SI-7B_Panchnama_No_Resistance.pdf": lambda: form_pdf("SI-7B", "Annexure-07_SI-7B_Panchnama_No_Resistance.pdf"),
    "Annexure-08_SI-7C_Panchnama_Resistance.pdf": lambda: form_pdf("SI-7C", "Annexure-08_SI-7C_Panchnama_Resistance.pdf"),
    "Annexure-09_SI-7D_Panchnama_Possession_Not_Possible.pdf": lambda: form_pdf("SI-7D", "Annexure-09_SI-7D_Panchnama_Possession_Not_Possible.pdf"),
    "Annexure-10A_Supplementary_Agreement_OTS.pdf": lambda: form_pdf("ANNEX-10A", "Annexure-10A_Supplementary_Agreement_OTS.pdf"),
    "Annexure-10A-1_Guarantor_Consent_OTS.pdf": lambda: form_pdf("ANNEX-10A-1", "Annexure-10A-1_Guarantor_Consent_OTS.pdf"),
    "Annexure-10B_Supplementary_Agreement_Other_Reasons.pdf": lambda: form_pdf("ANNEX-10B", "Annexure-10B_Supplementary_Agreement_Other_Reasons.pdf"),
    "Annexure-10B-1_Guarantor_Consent_Other_Reasons.pdf": lambda: form_pdf("ANNEX-10B-1", "Annexure-10B-1_Guarantor_Consent_Other_Reasons.pdf"),
    "Annexure-11_Notice_Book_Debts_Details.pdf": lambda: form_pdf("ANNEX-11", "Annexure-11_Notice_Book_Debts_Details.pdf"),
    "Annexure-12_Public_Notice_Book_Debts.pdf": lambda: form_pdf("ANNEX-12", "Annexure-12_Public_Notice_Book_Debts.pdf"),
    "Annexure-13_SI-10_Possession_Notice_Single_Borrower.pdf": lambda: form_pdf("SI-10", "Annexure-13_SI-10_Possession_Notice_Single_Borrower.pdf"),
    "Annexure-14_SI-10A_Possession_Notice_Common_One_AO.pdf": lambda: form_pdf("SI-10A", "Annexure-14_SI-10A_Possession_Notice_Common_One_AO.pdf"),
    "Annexure-15_SI-10B_Possession_Notice_Common_Many_AO.pdf": lambda: form_pdf("SI-10B", "Annexure-15_SI-10B_Possession_Notice_Common_Many_AO.pdf"),
    "Annexure-16_SI-15_Sale_Certificate_Movable.pdf": lambda: form_pdf("SI-15", "Annexure-16_SI-15_Sale_Certificate_Movable.pdf"),
    "Annexure-17_SI-17_Sale_Certificate_Immovable.pdf": lambda: form_pdf("SI-17", "Annexure-17_SI-17_Sale_Certificate_Immovable.pdf"),
    "Draft_SI-6_Pre-Possession_Notice.pdf": lambda: form_pdf("SI-6", "Draft_SI-6_Pre-Possession_Notice.pdf"),
    "Draft_SI-13_Notice_of_Sale.pdf": lambda: form_pdf("SI-13", "Draft_SI-13_Notice_of_Sale.pdf"),
    "Reply_to_13-3A_Representation_Letter.pdf": lambda: form_pdf("REPLY-13-3A", "Reply_to_13-3A_Representation_Letter.pdf"),
}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, f in FILES.items():
        f()
    print(f"built {len(FILES)} PDFs in {OUT}")
