"""Generate the SARFAESI recovery timeline & document register PDF.

Source: PNB Recovery Division Circular No. 31/2017 dated 30.06.2017
("SARFAESI Act - Consolidation of Important Aspects").

Usage: python3 docs/build_sarfaesi_timeline.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).parent / "SARFAESI_Recovery_Timeline_and_Document_Register.pdf"

NAVY = colors.HexColor("#1f3a5f")
LIGHT = colors.HexColor("#e8eef6")
AMBER = colors.HexColor("#fff4d6")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=18, textColor=NAVY, spaceAfter=4)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12.5, textColor=NAVY, spaceBefore=6, spaceAfter=5)
BODY = ParagraphStyle("B", parent=ss["BodyText"], fontSize=8.8, leading=11.5)
CELL = ParagraphStyle("C", parent=BODY, fontSize=7.8, leading=9.8)
CELLB = ParagraphStyle("CB", parent=CELL, fontName="Helvetica-Bold")
HEAD = ParagraphStyle("H", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)
SMALL = ParagraphStyle("S", parent=BODY, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#444444"))


def P(t, s=CELL):
    return Paragraph(t, s)


def table(header, rows, widths, band_rows=()):
    data = [[P(h, HEAD) for h in header]]
    for r in rows:
        data.append([c if not isinstance(c, str) else P(c) for c in r])
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9aa7b8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fb")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]
    for i in band_rows:
        style.append(("BACKGROUND", (0, i + 1), (-1, i + 1), LIGHT))
        style.append(("SPAN", (0, i + 1), (-1, i + 1)))
    t.setStyle(TableStyle(style))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(12 * mm, 7 * mm, "Derived from PNB Recovery Division Circular No. 31/2017 (30.06.2017). Verify against current law / Law Division circulars before issue.")
    canvas.drawRightString(landscape(A4)[0] - 12 * mm, 7 * mm, f"Page {doc.page}")
    canvas.restoreState()


# ---------------------------------------------------------------- content
TIMELINE_HDR = ["Day*", "Step / action", "Form / Annexure", "By whom", "Basis / key rule", "Record to keep", "Target date"]
W = [17, 78, 30, 26, 52, 50, 20]

timeline = [
    # (band?, row)
    ("Phase 1 - Initiation and demand notice", None),
    (None, ["Day 1", "Account becomes NPA. Branch Head prepares note for recall and SARFAESI action and obtains administrative sanction. Needed in every case, whatever the scale.", "SI-2 (SARFAESI Manual) with draft 13(2) notice", "Branch Head", "Board Res. 36 of 26.06.2012. Branches headed by Scale IV and above: the Branch Head, as Authorized Officer, acts and keeps Circle Head/ZM informed.", "Signed SI-2, sanction note"]),
    (None, ["Day 2 / 4", "Issue 60-day Demand Notice u/s 13(2) / recall notice to every borrower, co-borrower and mortgagor. Issue invocation notice to guarantors. The notice must carry the Rule 3(5) clause on s.13(8) (right to redeem). For hypothecated book debts, state that the Bank will also enforce its security over them.", "Annexure-1 (revised SI-4, borrowers); Annexure-2 (revised SI-4A, guarantors)", "Designated Authorized Officer (DGM/AGM/CM; Circle Office issues within 3 days of draft)", "S.13(2); Rule 3(1) and 3(5). Rank at least Chief Manager (Rule 2(a)). Send to ALL known addresses, by more than one mode: Regd. Post AD / Speed Post / Courier / Hand delivery / e-mail.", "Dispatch proofs: postal receipts, AD cards, POD, printed e-mail with read/delivery receipt"]),
    (None, ["By Day 9 / 11", "Check service. Track delivery on the India Post website instead of waiting for AD cards or returns. Normal delivery is about 7 days. If service failed on any obligant, take substituted service now: affix on the outer door of the house or business premises, and publish the notice in two newspapers (one vernacular).", "Annexure-3 (post tracking); Annexure-4 (e-mail receipts)", "Authorized Officer", "Proviso to Rule 3. Do not hold back further steps waiting for a postal report.", "Tracking print-outs, returned envelopes (unopened), newspaper cuttings, affixation memo"]),
    (None, ["By Day 69 / 71", "Reply to any representation or objection from the borrower or guarantor under s.13(3A). A reasoned reply is mandatory: no ritual rejection, and the reasons must be communicated. Statutory limit is 15 days from receipt of the representation. Do not wait for the 15 days. Get high-value replies vetted by the Law Officer without letting that delay the reply.", "Annexure-5 (guidance on common objections)", "Authorized Officer", "S.13(3A); Mardia Chemicals (SC, 08.04.2004). Possession notice must NOT be issued before this reply is sent.", "Representation, point-wise comments, signed reply and its dispatch proof"]),
    ("Phase 2 - Steps after the s.13(2) notice (finish together by Day 69 / 71)", None),
    (None, ["By Day 69 / 71", "Take the Circle Head / ZM's permission to engage a Supporting Agency. Issue its engagement letter. The agency makes a pre-possession survey and report. Authorized Officer examines the report and proceeds only if everything is in order.", "Engagement letter (per policy); survey report", "Authorized Officer", "Visit the site with banners of the Bank in a four-wheeler. In consortium / multiple banking, get consent of secured creditors holding 60% in value before s.13(4) action.", "Permission note, engagement letter, survey report"]),
    (None, ["Day 69 / 71", "Issue Pre-Possession Notice (notice to deliver possession) giving reasonable time to hand over the secured assets, once service is confirmed complete and any s.13(3A) representation has been replied to. Not a legal requirement, but advised.", "SI-6 (SARFAESI Manual)", "Authorized Officer", "Check there is NO stay from DRT / Court / High Court. Honour any court order received at any stage after examining its intent.", "Copy of SI-6, dispatch proof, no-stay certificate/note on file"]),
    ("Phase 3 - Possession u/s 13(4)", None),
    (None, ["Day 79 / 81", "Take possession u/s 13(4) on or after the date given in the Pre-Possession Notice (10 days after it). Immovables: deliver Possession Notice to the borrower, affix it on the outer door or a conspicuous place, prepare inventory. Movables: take possession, prepare Panchnama and inventory, deliver a copy to the person entitled (or send by AD post / courier if he refuses). Take the valuer along. Where vacant possession cannot be had, affixing the notice is Symbolic Possession and is valid.", "Immovables: Annexure-13/14/15 (SI-10 / 10A / 10B) and inventory SI-9. Movables: Annexures 6-9 (SI-7A/7B/7C/7D Panchnama) and inventory SI-8", "Authorized Officer", "Rule 4 and Rule 8. New Rule 4(2A): send the borrower a notice enclosing the Panchnama and inventory, with the s.13(8) redemption sentence. Notices may also be served electronically (Rule 4(2B)). Photograph/video the affixation widely, with witnesses.", "Panchnama, inventory, affixation photos/video, delivery proof"]),
    (None, ["Day 79 / 81 (file with possession)", "If the borrower resists, or as a rule where physical possession matters, file the application before the DM / CMM for physical possession simultaneously with the s.13(4) notice. Follow it up. File a writ if the DM delays.", "Application and affidavit u/s 14", "Authorized Officer / Counsel", "S.14: DM/CMM to pass orders within 30 days, extendable to 60 days in aggregate for recorded reasons. Para 14.9: file together with 13(4) notice.", "Filed application, DM/CMM order, follow-up log"]),
    (None, ["Publication by Day 82 / 84", "Publish the Possession Notice in two leading newspapers, one in the vernacular, within 7 days of taking possession. Immovables only. Use SI-10 for a single NPA account, SI-10A for multiple accounts and one Authorized Officer, SI-10B for multiple accounts and more than one Authorized Officer.", "SI-10 / SI-10A / SI-10B (Annexures 13-15)", "Authorized Officer", "Rule 8(2). The 7-day limit must be strictly adhered to or the action may be stayed.", "Newspaper cuttings, invoices (debit to 'Law charges')"]),
    (None, ["By Day 82 / 84", "Obtain valuation from a Board-approved valuer. Do not wait for actual possession of immovables.", "Valuation report", "Authorized Officer", "Rule 5 and 8(5). Report relied on should normally be not more than 1 year old.", "Valuation report"]),
    ("Phase 4 - Reserve price and sale", None),
    (None, ["By Day 84 / 86", "Send recommendation and valuation to COCESI (ZM for LCBs) to fix the Reserve Price and the mode of sale. COCESI finalises within 2 days. The committee may fix a sale period of up to 6 months, after which concurrence is sought again. Any downward revision needs fresh concurrence.", "Recommendation note, committee minutes", "Authorized Officer, COCESI / ZM", "Para 7. COCESI: Circle Head (Chair), Deputy Circle Head, CM/SM Recovery, Sr Mgr (Law). LCB committee: Branch Head, second in command, Relationship Manager.", "Committee minutes with reserve price and mode of sale"]),
    (None, ["By Day 87 / 89", "Issue 30-day Notice of Intended Sale to the borrower, mortgagor and guarantors (movables and immovables). Publish the Sale Notice / Proclamation of Sale (or Invitation for Tender) in two leading newspapers, one in the vernacular. For immovables, also affix on a conspicuous part of the property. Also post on www.pnbindia.in and www.tenders.gov.in. For e-auction also on www.pnbindia.biz, at least 30 days before sale.", "SI-13 (notice of sale); SI-14 (proclamation); SI-24 (invitation for tender). Ready the tender documents SI-25 and SI-26", "Authorized Officer", "Rule 6 and Rule 8. Gap of at least 30 days between publication and auction / tender opening. Sale notice must say 'subject to confirmation by the Secured Creditor'. Show full address with pin code and dues of local authorities per property (MoF letter 20.11.2015). No sale on a holiday.", "SI-13 dispatch proof, cuttings, website print-outs, affixation photos"]),
    (None, ["Day 121 / 123", "Auction / tender opening. Check there is no stay. Auction: collect EMD (generally 10% of reserve price), take SI-18A signed by bidders, record bids on the bid sheet, declare the highest bidder. Tenders: open in the presence of bidders and record on the bid sheet. No bid below the reserve price may be confirmed. Start the bidding above the reserve price. Take the highest bidder's bio-data. On receipt of the initial deposit, send the communication of acceptance.", "SI-18A (auction terms); SI-19 (bid sheet); SI-20 (bio-data); SI-21 (acceptance of bid); for tenders SI-25 and SI-26", "Authorized Officer", "Rule 9. Initial deposit of 25% of the price (including EMD), on the same day or next working day. Default means the property is sold again.", "Signed bid sheet, EMD receipts, SI-18A/SI-25 forms, SI-20, SI-21"]),
    (None, ["Within 15 days of the auction", "Immovables only: take the Committee of Officers' (COCESI / LCB committee) confirmation of sale as Secured Creditor, then communicate it to the highest bidder. If sale is not confirmed, record reasons in the minutes, tell the purchaser at once and return the deposit. Not needed for movables. Execute the Agreement to Sell.", "SI-22 (confirmation of sale); SI-23 (agreement to sell)", "Authorized Officer, Committee of Officers", "Rule 9(2), 9(6). Sale price below Reserve Price cannot be confirmed (a sale at that price needs both borrower's and secured creditor's consent).", "Minutes of Committee of Officers, SI-22, SI-23"]),
    (None, ["Balance 75% by Day 136 / 138", "Receive the balance 75% within 15 days of confirmation of sale, or a longer period agreed in writing, not exceeding 3 months. On default, forfeit the deposit and resell. A resale needs a fresh notice of not less than 15 days to the borrower, served, affixed and published.", "SI-23 terms; fresh SI-13 for resale", "Authorized Officer", "Rule 9(4), 9(5); Rule 6 second proviso (15-day notice for any subsequent sale).", "Receipts, forfeiture note if any"]),
    (None, ["On full payment and delivery", "Issue the Certificate of Sale. Movables: SI-15, or receipt SI-16 if the purchaser does not want a certificate. Immovables: SI-17. Where the occupant is a lawful tenant, give symbolic possession by affixing a copy of the Certificate of Sale and proclaiming by beat of drum.", "Annexure-16 (revised SI-15); SI-16; Annexure-17 (revised SI-17)", "Authorized Officer", "Rule 9(6). A certificate may attract stamp duty.", "Certificate of Sale, delivery record"]),
    (None, ["After sale", "Apply the proceeds in this order: (1) costs of the SARFAESI action (postage, publication, watch and ward, insurance, godown, agency fees); (2) principal dues of the NPA account; (3) interest as per Circular 26/2013 dated 04.06.2013; (4) surplus to the person entitled. SARFAESI ACTION CONCLUDES. Update the SARFAESI portal.", "-", "Branch / Authorized Officer", "Para 14.13: update the SARFAESI portal regularly. Publication expenses are debited to 'Law charges' and kept in memoranda dues.", "Appropriation statement, portal update"]),
]

timeline_rows, bands = [], []
for band, row in timeline:
    if band:
        bands.append(len(timeline_rows))
        timeline_rows.append([P(f"<b>{band}</b>", CELL), "", "", "", "", "", ""])
    else:
        row = list(row) + [""]
        row[0] = P(f"<b>{row[0]}</b>")
        timeline_rows.append(row)

# --------------------------------------------------------------- registers
FORMS_HDR = ["Form", "Purpose", "Used at stage", "Where in circular"]
FW = [28, 116, 70, 58]
forms = [
    ["SI-2", "Branch Head's note seeking approval and sanction to initiate SARFAESI action, with draft 13(2) notice", "Day 1", "SARFAESI Manual"],
    ["SI-4 (revised)", "60-day Demand Notice u/s 13(2) to borrower / mortgagor, with s.13(8) redemption clause", "Day 2/4", "Annexure-1"],
    ["SI-4A (revised)", "Notice u/s 13(2) / invocation of guarantee to guarantor", "Day 2/4", "Annexure-2"],
    ["Substituted service", "Affixation on door plus publication in two newspapers when personal service fails", "By Day 9/11 if needed", "Para 4(f); Annexure-3, 4 for tracking"],
    ["Reply to s.13(3A) objection", "Reasoned reply to the borrower's representation (guidance on common objections)", "Within 15 days of receipt (aim by Day 69/71)", "Annexure-5"],
    ["SI-6", "Pre-Possession Notice, to deliver possession", "Day 69/71", "SARFAESI Manual"],
    ["SI-7A / 7B / 7C / 7D (revised)", "Panchnama on taking possession of movables, with s.13(8) sentence", "Day 79/81", "Annexures 6, 7, 8, 9"],
    ["SI-8", "Inventory of movables (Rule 4(2))", "Day 79/81", "SARFAESI Manual"],
    ["SI-9", "Inventory of immovables", "Day 79/81", "SARFAESI Manual"],
    ["SI-10 (revised)", "Possession Notice, immovables, single NPA account", "Day 79/81, publish by 82/84", "Annexure-13"],
    ["SI-10A (revised)", "Possession Notice, multiple NPA accounts, one Authorized Officer", "As above", "Annexure-14"],
    ["SI-10B (revised)", "Possession Notice, multiple NPA accounts, more than one Authorized Officer", "As above", "Annexure-15"],
    ["Application u/s 14", "Application and affidavit to DM / CMM for physical possession", "With 13(4) notice", "Para 6(iii); Para 14.9"],
    ["Valuation report", "From Board-approved valuer; not older than 1 year", "By Day 82/84", "Para 7.3"],
    ["COCESI / ZM minutes", "Fix reserve price, mode and period of sale", "By Day 84/86", "Para 7"],
    ["SI-13", "30-day notice of intended sale to borrower and guarantors (15 days for any subsequent sale)", "By Day 87/89", "SARFAESI Manual"],
    ["SI-14", "Proclamation of Sale / public notice for auction", "By Day 87/89", "SARFAESI Manual"],
    ["SI-24", "Invitation for Tender (public notice for tender sale)", "By Day 87/89", "SARFAESI Manual"],
    ["SI-25 / SI-26", "Tender terms and conditions form; covering letter for sealed tender with EMD", "From publication; opening Day 121/123", "SARFAESI Manual"],
    ["SI-18A", "Bidders' acceptance of terms and conditions of auction", "Day 121/123", "SARFAESI Manual"],
    ["SI-19", "Bid sheet, signed by bidders", "Day 121/123", "SARFAESI Manual"],
    ["SI-20", "Bio-data of highest bidder", "Day 121/123", "SARFAESI Manual"],
    ["SI-21", "Communication of acceptance of bid", "On initial deposit", "SARFAESI Manual"],
    ["SI-22", "Confirmation of sale by secured creditor (immovables)", "Within 15 days", "SARFAESI Manual (Appendix B)"],
    ["SI-23", "Agreement to Sell", "After confirmation", "SARFAESI Manual"],
    ["SI-15 / SI-16 (revised)", "Certificate of Sale (movables) / receipt if no certificate wanted", "On full payment", "Annexure-16; SI-16"],
    ["SI-17 (revised)", "Certificate of Sale (immovables)", "On full payment", "Annexure-17"],
    ["Annexure-10A / 10A-1", "Supplementary agreement on OTS, with guarantor's consent letter, to hold action in abeyance safely", "If SARFAESI is put on hold for OTS", "Annexures 10-A, 10-A-1"],
    ["Annexure-10B / 10B-1", "Supplementary agreement for reasons other than OTS, with guarantor's consent letter", "If SARFAESI is put on hold for other reasons", "Annexures 10-B, 10-B-1"],
    ["Annexure-11", "Notice to borrower asking for details of book debts / receivables", "Book-debt accounts", "Annexure-11"],
    ["SI-28", "Notice to each debtor of the borrower: pay to the Authorized Officer, not the borrower (s.13(4)(d))", "After 60 days, book-debt accounts", "SARFAESI Manual 2008"],
    ["Annexure-12", "Public Notice (model) when the list of debtors is not available", "Book-debt accounts", "Annexure-12"],
]

CHECK_HDR = ["#", "Compliance checkpoint (do not miss)", "Source"]
CW = [8, 200, 64]
checks = [
    "Check for a stay from DRT / DRAT / Court / High Court before every stage (possession, sale, confirmation). Honour all court orders received. File a CAVEAT where large stakes are involved.",
    "Notice must be served on ALL borrowers, guarantors and mortgagors, at all known addresses, by more than one mode. Plain UPC / ordinary post is a ground for stay.",
    "The 13(2) notice must carry the s.13(8) redemption clause (Rule 3(5)); the Panchnama and inventory notice carries the same sentence (Rule 4(2A)).",
    "Reply to every s.13(3A) representation within 15 days with real reasons. Issue no possession notice before that reply.",
    "Only an Authorized Officer (Chief Manager or above) may issue notices, take possession and sell.",
    "Publish the Possession Notice within 7 days in two newspapers, one in the vernacular. Immovables only.",
    "Gap of at least 30 days between sale publication / notice and the auction or tender opening. The 30-day notice goes to the borrower and guarantors. Immovables: affix on the property too.",
    "Sale notices must say 'subject to confirmation by the Secured Creditor' (Rule 9(2)), never 'by the Authorized Officer'. In mixed movable / immovable accounts use the same wording throughout.",
    "Reserve price: approved by COCESI (ZM for LCBs) on a Board-approved valuer's report, normally not older than 1 year. No sale below reserve price. A downward revision needs fresh concurrence.",
    "Deposit of 25% (EMD included) on the same day or next working day; balance 75% within 15 days of confirmation, extendable by written agreement to 3 months at most. Default: forfeit and resell.",
    "Confirmation of sale by the Committee of Officers is compulsory for immovables and not required for movables. Certificate of Sale only on full payment.",
    "Failed sale: for any subsequent sale serve, affix and publish a notice of not less than 15 days.",
    "Private treaty only after other methods fail: 1 attempt for assets up to Rs.1 crore, 2 attempts above Rs.1 crore. If recovery is below the assessed value / reserve price and the bank is not fully repaid, ZM approval is needed. The borrower's consent is not necessary.",
    "Consortium / multiple banking: consent of secured creditors holding 60% in value is needed before s.13(4) action (s.13(9)). Lead bank acts for all. Where PNB is not the leader, submit consent to the leader without waiting. Dues of Rs.50 lakh and above: monitoring authority is Head Office Recovery Division.",
    "Hold in abeyance (OTS, regularisation) for not more than 60 more days, by the authority that permitted the action, with reasons recorded. Take a supplementary agreement and guarantor consent so that action can resume from the same point.",
    "Hypothecated book debts: state in the 13(2) notice that book debts will be enforced; after 60 days serve SI-28 on each debtor. If the borrower collects debts after notice, file a criminal complaint u/s 29.",
    "Keep every proof: dispatch receipts, tracking print-outs, AD cards, e-mail receipts, cuttings, photographs/video of possession, minutes.",
    "Monthly review meeting of COCESI at Circle Office (committee at LCB level). Update the SARFAESI portal regularly.",
    "Publication costs are necessary expenditure, debited to 'Law charges' and recorded in memoranda dues for recovery from sale proceeds. Sale is prohibited on holidays.",
    "Educational institutions: take possession in vacation periods. In DRT appeals, officials and counsel attend the hearing so that the appeal is disposed of within 4 months.",
]
checks_rows = [[str(i + 1), c, s] for i, (c, s) in enumerate(zip(checks, [
    "Work flow chart p.9; Para 16", "Para 4(c); Para 16 item 1", "Para 3; Para 6(iv)", "Para 5; Para 16 item 2", "Para 2", "Para 16 item 5; Rule 8(2)",
    "Para 8(ii); Para 16 item 6", "Para 9.1", "Para 7.3", "Para 8(iii)", "Para 8(iii)(d), 8(iv)", "Para 8(ii)(d); Para 15.4", "Para 15; 15.1-15.4",
    "Para 13", "Para 10", "Para 12", "Para 4(d), (e); Para 16 item 3-4", "Para 7.1(c); Para 14.13", "Para 11; Para 8", "Para 16 item 10; Para 16 advice (iii)"]))]

REC_HDR = ["Record / register", "What it must hold"]
RW = [70, 202]
records = [
    ["SARFAESI account file", "SI-2 with sanction; NPA date; security and mortgage documents; proof that a valid mortgage exists; consortium consent (if any)."],
    ["Notice dispatch register", "For every notice: date, addressee, address, mode, receipt / AD / POD number, tracking print-out, returned cover, e-mail read/delivery receipt, substituted-service proof."],
    ["s.13(3A) objection register", "Date of receipt of each representation, point-wise comments, reply date (within 15 days), vetting by Law Officer where taken, copy of reply."],
    ["Possession file", "Pre-possession survey report, SI-6, Panchnama, inventory, possession notice, affixation photos/video, witnesses, DM/CMM application and order, newspaper publication within 7 days."],
    ["Valuation and reserve price file", "Valuer's report (age under 1 year), recommendation, COCESI / ZM minutes with reserve price, mode and validity period, any revision."],
    ["Sale file", "SI-13 dispatch proof, publications, website postings, bidder list, EMD receipts, SI-18A, SI-19 bid sheet, SI-20, SI-21, SI-22 minutes, SI-23, receipts for the 25% and 75% instalments, certificate of sale."],
    ["Court / stay tracker", "Every SA / IA / writ: forum, number, next date, stay status, reply filed, counsel, who attended."],
    ["Expense and appropriation ledger", "Publication, postage, agency, watch and ward, insurance and godown costs; proceeds appropriated costs-principal-interest-surplus; memoranda dues."],
    ["Monthly review minutes", "COCESI / LCB committee review of every open SARFAESI account against this timeline."],
]

# ----------------------------------------------------------------- build
doc = SimpleDocTemplate(
    str(OUT), pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
    topMargin=12 * mm, bottomMargin=14 * mm,
    title="SARFAESI Recovery Timeline and Document Register",
    author="Recovery Division",
)
story = [
    Paragraph("SARFAESI Recovery: Timeline and Document Register", H1),
    Paragraph("Working schedule for the Recovery Head, from PNB Recovery Division Circular No. 31/2017 dated 30.06.2017 (SARFAESI Act - Consolidation of Important Aspects). "
              "The circular replaces Circulars 37/2015 and 18/2016. It reflects the Security Interest (Enforcement) Rules amendment of 03.11.2016.", BODY),
    Spacer(1, 3),
    Paragraph("* <b>How to read the days.</b> Day 1 is the day the account becomes NPA. The circular gives two day numbers for most steps (for example 2nd/4th, 69th/71st). "
              "The first is the standard timeline; the second is the outer limit when the notice goes out on Day 4 instead of Day 2. Fill the last column with the actual date for each case.", BODY),
    Spacer(1, 4),
    Paragraph("1. Master timeline", H2),
    table(TIMELINE_HDR, timeline_rows, W, band_rows=bands),
    PageBreak(),
    Paragraph("2. Notices, forms and records to be prepared", H2),
    table(FORMS_HDR, forms, FW),
    Spacer(1, 6),
    Paragraph("3. Compliance checkpoints", H2),
    table(CHECK_HDR, checks_rows, CW),
    Spacer(1, 8),
    Paragraph("4. Files and registers to maintain for every account", H2),
    table(REC_HDR, records, RW),
    Spacer(1, 8),
    Paragraph("<b>Notes.</b> (1) The SI-series forms themselves are in the SARFAESI Manual 2008, apart from the revised forms reproduced as Annexures 1-17 of the circular. "
              "Fill them with the account's own borrower, security and amount details; they are not reproduced here. "
              "(2) This is a 2017 circular. Check later Law Division and Recovery Division circulars and current statute before issuing a notice. "
              "(3) Rules are paraphrased for working use; the circular and the Act prevail.", SMALL),
]
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
