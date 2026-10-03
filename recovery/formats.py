"""Notice / record formats.

Annexure 1-17 texts are transcribed from PNB Recovery Division Circular 31/2017. Bank name and head office
are merge fields (Settings). Forms the circular only *names* (SARFAESI Manual 2008 forms) are listed in
MANUAL_FORMS so they can be tracked, but their wording is not in the circular and is not reproduced.

Template markup (one line each):
  # text        centred bold heading         ## text   centred bold sub-heading
  >> text       right aligned                ** text   bold paragraph
  |a|b|c|       table row (consecutive lines form one table)
  ?flag| text   line included only when boolean field `flag` is ticked
  {{field}}     merge field; blank fields print as ________
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Format:
    key: str
    title: str
    source: str                   # where the wording comes from
    stage: str
    body: str
    fields: tuple[tuple[str, str, object], ...] = ()   # (key, label, default); bool default => checkbox
    draft: bool = False           # wording NOT from the circular: must be conformed to the Manual


S13_8 = ("** Your attention is invited to provisions of sub-section (8) of section 13 of the Act, in respect of "
         "time available to you to redeem the secured assets.")

PANCH_TABLE = """|S.No.|Name of Panch & Father's/Husband Name|Address|Age|Occupation|
|1| | | | |
|2| | | | |"""

_SIGN = """Name | Address | Signature
|1.| | |
|2.| | |
Date: {{possession_date}}
Time: {{possession_time}}
>> Drawn before me
>> {{officer}}, {{designation}}
>> Authorised Officer"""

_FAC = """|Facility|Limit (Rs.)|Balance outstanding as on {{as_on}} (Rs.)|
|{{facility}}|{{limit_amt}}|{{outstanding}}|
|Total| |{{outstanding}}|"""

_TAIL_NOTICE = """** Please take notice that in terms of section 13(13) of the said Act, you shall not, after receipt of this notice, transfer by way of sale, lease or otherwise (other than in the ordinary course of business) any of the secured assets above referred to, without prior written consent of the Bank. You are also put on notice that any contravention of this statutory injunction/restraint, as provided under the said Act, is an offence.
If for any reason, the secured assets are sold or leased out in the ordinary course of business, the sale proceeds or income realised shall be deposited/remitted with/to the Bank. You will have to render proper account of such realisation/income.
?reserve_other|We reserve our rights to enforce other secured assets.
Please comply with this demand under this notice and avoid all unpleasantness. In case of non-compliance, further needful action will be resorted to, holding you liable for all costs and consequences.
?no_prejudice_drt|This notice is issued without prejudice to the Bank taking legal action before DRT/Court, as the case may be.
?no_prejudice_suit|This notice is issued without prejudice to the Bank's rights in the suit/litigation pending before DRT/Court.
Yours faithfully,
For {{bank_name}}
>> {{officer}}
>> {{designation}}
>> AUTHORISED OFFICER
Copy to: {{copy_to}}"""

_COMMON_NOTICE_FIELDS = (
    ("notice_date", "Date of notice", "today"),
    ("recall_letter_date", "Date of earlier recall letter", ""),
    ("copy_to", "Copy to", ""),
    ("reserve_other", "Reserve right to enforce other secured assets", True),
    ("no_prejudice_drt", "Without prejudice to legal action before DRT/Court", True),
    ("no_prejudice_suit", "Without prejudice to pending suit/litigation", False),
)

SI4 = Format("SI-4", "60 days' demand notice to borrower u/s 13(2)", "Annexure-1 (Revised SI-4)", "Demand notice",
f"""># Annexure-1 (Revised SI-4)
# 60 Days' Notice to Borrower
>> Date: {{{{notice_date}}}}
{{{{borrower}}}}
{{{{address}}}}
(Name and address of the borrower who has created security interest)
Dear Sir,
# NOTICE U/S 13(2) of the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act 2002
** Reg: Account No. {{{{account_no}}}} / credit facilities availed by M/s {{{{borrower}}}}
You, M/s {{{{borrower}}}} ({{{{address}}}}) have availed the following credit facilities:
{_FAC}
Due to non payment of instalment/interest/principal debt, the account/s has/have been classified as Non Performing Asset as per Reserve Bank of India guidelines. We have demanded/recalled the entire outstanding together with interest and other charges due under the above facilities, vide letter dated {{{{recall_letter_date}}}}.
The amount due to the Bank as on {{{{as_on}}}} is Rs.{{{{outstanding}}}} ({{{{outstanding_words}}}}) with further interest until payment in full (hereinafter referred to as "secured debt").
To secure the outstandings under the abovesaid facilities, you have, inter alia, created security interest in respect of the following properties/assets:
|Facility|Security|
|{{{{facility}}}}|{{{{security_desc}}}}|
We hereby call upon you to pay the amount of Rs.{{{{outstanding}}}} ({{{{outstanding_words}}}}) with further interest at the contracted rate until payment in full within **60 days (sixty days)** from the date of this notice. In default, besides exercising other rights of the Bank as available under Law, the Bank is intending to exercise any or all of the powers as provided under section 13(4) of the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act 2002 (hereinafter referred to as "the Act"). The details of the secured asset/s intended to be enforced by the Bank, in the event of non payment of secured debt by you are as under:
1. {{{{security_desc}}}}
{S13_8}
{_TAIL_NOTICE}""".replace(">#", "#", 1), _COMMON_NOTICE_FIELDS)

SI4A = Format("SI-4A", "60 days' notice to guarantor/mortgagor u/s 13(2)", "Annexure-2 (Revised SI-4A)", "Demand notice",
f"""# Annexure-2 (Revised SI-4A)
# 60 Days' Notice to Guarantor/Mortgagor
>> Date: {{{{notice_date}}}}
{{{{guarantor}}}}
(Name and address of the guarantor/mortgagor who has created security interest)
Dear Sir,
# NOTICE U/S 13(2) of the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act 2002
** Reg: Account No. {{{{account_no}}}} / credit facilities availed by M/s {{{{borrower}}}}
M/s {{{{borrower}}}} ({{{{address}}}}) have availed the following credit facilities:
{_FAC}
Due to non payment of instalment/interest/principal debt the account/s has/have been classified as Non Performing Asset as per Reserve Bank of India guidelines. We have already demanded/recalled the entire outstanding together with interest and other charges due under the above facilities from the Borrower, vide letter dated {{{{recall_letter_date}}}}, copy of which has already been sent to you. We have invoked the guarantee vide letter dated {{{{invocation_date}}}}.
The amount due to the Bank as on {{{{as_on}}}} is Rs.{{{{outstanding}}}} ({{{{outstanding_words}}}}) with further interest until payment in full (hereinafter referred to as "secured debt").
To secure the outstandings under the abovesaid facilities, you have, inter alia, created security interest in respect of the following properties/assets:
|Facility|Security|
|{{{{facility}}}}|{{{{security_desc}}}}|
We hereby call upon you to pay the amount of Rs.{{{{outstanding}}}} ({{{{outstanding_words}}}}) with further interest at the contracted rate until payment in full within **60 days (sixty days)** from the date of this notice. In default, besides exercising other rights of the Bank available under Law, the Bank is intending to exercise any or all of the powers as provided under section 13(4) of the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act 2002 (hereinafter referred to as "the Act"). The details of the secured asset/s intended to be enforced by the Bank, in the event of non payment of secured debt by you are as under:
1. {{{{security_desc}}}}
{S13_8}
{_TAIL_NOTICE}""", _COMMON_NOTICE_FIELDS + (
    ("guarantor", "Guarantor/mortgagor name & address", "first_guarantor"),
    ("invocation_date", "Date of guarantee invocation letter", ""),
))

REPLY = Format("REPLY-13-3A", "Reply to representation/objection u/s 13(3A)",
               "Para 5 and Annexure-5 guidance", "Reply to representation",
"""# Reply to representation / objection u/s 13(3A) of the SARFAESI Act
>> Date: {{notice_date}}
{{objector}}
Dear Sir,
** Reg: Account No. {{account_no}} - M/s {{borrower}} - your reply/representation dated {{representation_date}} to the notice u/s 13(2) dated {{demand_date}}
We acknowledge your representation/objection dated {{representation_date}} received on {{received_date}}. The same has been considered with due application of mind, as required u/s 13(3A) of the Act. Our position on each point raised is set out below, with reasons.
{{point_wise_reply}}
For the reasons stated above, your representation/objections are not acceptable and the Bank will proceed to enforce its security interest in accordance with law if the secured debt is not paid. This communication is for your information and does not give rise to any right to approach the DRT under section 17 at this stage.
Yours faithfully,
For {{bank_name}}
>> {{officer}}
>> {{designation}}
>> AUTHORISED OFFICER""", (
    ("notice_date", "Date of reply", "today"), ("objector", "Addressee name & address", "borrower_address"),
    ("representation_date", "Date of representation", ""), ("received_date", "Date received", ""),
    ("demand_date", "Date of 13(2) notice", ""),
    ("point_wise_reply", "Point-wise reasoned reply (see Annexure-5 guidance)", ""),
))

SI6 = Format("SI-6", "Pre-possession notice (notice to deliver possession)",
             "Named in circular; wording is a DRAFT, conform to SARFAESI Manual SI-6", "Pre-possession notice",
"""# NOTICE TO DELIVER POSSESSION OF SECURED ASSETS (DRAFT - conform to SARFAESI Manual Form SI-6)
>> Date: {{notice_date}}
{{borrower}}
{{address}}
** Reg: Account No. {{account_no}} - Demand notice u/s 13(2) dated {{demand_date}}
The Bank issued a demand notice u/s 13(2) of the SARFAESI Act on {{demand_date}} calling upon you to pay Rs.{{outstanding}} ({{outstanding_words}}) with interest within 60 days. The period has expired and the amount remains unpaid. {{representation_line}}
You are called upon to hand over possession of the secured assets described below to the Authorised Officer on or before {{possession_date}}, failing which the Bank will take possession u/s 13(4) of the Act read with Rule 8 of the Security Interest (Enforcement) Rules 2002, without further notice, and recover the cost from you.
Secured assets: {{security_desc}}
Your attention is invited to sub-section (8) of section 13 of the Act regarding the time available to redeem the secured assets.
For {{bank_name}}
>> {{officer}}, {{designation}}
>> AUTHORISED OFFICER""", (
    ("notice_date", "Date of notice", "today"), ("demand_date", "Date of 13(2) notice", ""),
    ("possession_date", "Hand-over date (10 days after notice)", ""),
    ("representation_line", "Line on representation (e.g. 'Your representation dated __ was replied on __')", ""),
), draft=True)

_PANCH_INTRO = """WHEREAS We,
""" + PANCH_TABLE + """
the above mentioned Panchs on being called by Shri {{officer}}, the Authorised Officer of {{bank_name}}, under the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act, 2002 were present at {{possession_place}}."""

_PANCH_FIELDS = (
    ("possession_place", "Place", ""), ("demand_date", "Date of demand notice", ""),
    ("possession_date", "Date of possession", ""), ("possession_time", "Time", ""),
    ("hours_from", "Between hours (from)", ""), ("hours_to", "and (to)", ""),
    ("party_name", "Borrower/guarantor/mortgagor name", "borrower"),
)
_S8 = "** The borrower's/guarantor's/mortgagor's attention is invited to provisions of sub-section (8) of section 13 of the Act in respect of time available to redeem the secured assets."
_TRUE = "Therefore, we solemnly declare that the facts of the Panchnama mentioned herein are true & correct to the best of our observations & knowledge."

SI7A = Format("SI-7A", "Panchnama - borrower readily delivers possession", "Annexure-6 (Revised SI-7A)", "Possession (movables/immovables)",
f"""# Annexure-6 (Revised SI-7A)
# PANCHNAMA
## (Minutes/Panchnama when borrower readily delivers possession)
{_PANCH_INTRO}
We declare and state that Shri {{{{officer}}}}, the Authorised Officer demanded payment of the dues mentioned in the Demand Notice dated {{{{demand_date}}}} in respect of loan A/c bearing No. {{{{account_no}}}}, and on its non-payment, in exercise of Powers under Section 13(4) of the said Act, called upon the borrower/guarantor/mortgagor Sh/M/s {{{{party_name}}}} to deliver possession of the secured asset as detailed in the Demand Notice abovesaid. The borrower/guarantor/mortgagor abovesaid has/have handed over the possession of the secured assets, as detailed in the inventory attached to this Panchnama between the hours {{{{hours_from}}}} and {{{{hours_to}}}} in our presence.
{_S8}
{_TRUE}
{_SIGN}""", _PANCH_FIELDS)

SI7B = Format("SI-7B", "Panchnama - Authorised Officer takes possession without resistance", "Annexure-7 (Revised SI-7B)", "Possession (movables/immovables)",
f"""# Annexure-7 (Revised SI-7B)
# PANCHNAMA
## (Minutes/Panchnama when AO takes possession without resistance)
{_PANCH_INTRO}
We declare and state that the Authorised Officer, in exercise of Powers under Section 13(4) of the said Act, today went to/entered the premises of Shri / M/s {{{{party_name}}}} (borrower/guarantor/mortgagor) at {{{{possession_place}}}}, and demanded the payment of the dues mentioned in the Demand Notice dated {{{{demand_date}}}} in respect of loan A/c bearing No. {{{{account_no}}}} and on its non-payment, has taken over possession of secured assets, as detailed in the inventory attached to this Panchnama between the hours {{{{hours_from}}}} and {{{{hours_to}}}} in our presence.
{_S8}
{_TRUE}
{_SIGN}""", _PANCH_FIELDS)

SI7C = Format("SI-7C", "Panchnama - resistance faced but possession taken", "Annexure-8 (Revised SI-7C)", "Possession (movables/immovables)",
f"""# Annexure-8 (Revised SI-7C)
# PANCHNAMA
## (Minutes/Panchnama where Authorised Officer faces resistance but takes possession)
{_PANCH_INTRO}
We declare and state that the Authorised Officer in exercise of powers under Section 13(4) of the said Act today went to/entered the premises of Shri / M/s {{{{party_name}}}} (borrower/guarantor/mortgagor) at {{{{possession_place}}}}, and demanded the payment of the dues mentioned in the Demand Notice dated {{{{demand_date}}}} in respect of loan A/c bearing No. {{{{account_no}}}} and on its non-payment, has taken over possession of the secured assets, as detailed in the Panchnama between the hours {{{{hours_from}}}} and {{{{hours_to}}}} in our presence.
{_S8}
We also hereby state that during takeover of possession {{{{incidents}}}} (details of occurrence of incidents, if any).
{_TRUE}
{_SIGN}""", _PANCH_FIELDS + (("incidents", "Details of incidents", ""),))

SI7D = Format("SI-7D", "Panchnama - possession could not be taken", "Annexure-9 (Revised SI-7D)", "Possession (movables/immovables)",
f"""# Annexure-9 (Revised SI-7D)
# PANCHNAMA
## (Minutes/Panchnama where taking possession is not possible)
{_PANCH_INTRO}
We declare and state that the 'Authorised Officer' in exercise of Powers under Section 13(4) of the said Act today went to/entered the premises of Shri / M/s {{{{party_name}}}} (borrower/guarantor/mortgagor) at {{{{possession_place}}}}, and demanded the payment of the dues mentioned in the Demand Notice dated {{{{demand_date}}}} in respect of loan A/c bearing No. {{{{account_no}}}} and on its non-payment, proceeded to take over possession of secured assets, as described in the schedule hereunder, between the hours {{{{hours_from}}}} and {{{{hours_to}}}} in our presence. There was hue and cry. The 'Authorised Officer' faced lot of resistance from the borrower/guarantor/mortgagor and borrower's/guarantor's/mortgagor's {{{{resisting_persons}}}}. We also hereby state that while trying to take over of possession {{{{incidents}}}} (give details of the incidents).
The 'Authorised Officer' came to the conclusion that possession cannot be taken without use of force. Hence it is decided by the 'Authorised Officer' not to venture further but to seek the assistance of Magistrate, as per the provisions of the Act.
{_TRUE}
## Schedule of Assets
{{{{security_desc}}}}
{_SIGN}""", _PANCH_FIELDS + (("resisting_persons", "Persons who resisted", ""), ("incidents", "Details of incidents", "")))

_POSS_NOTICE_HEAD = """Whereas
The undersigned being the Authorised Officer of {{bank_name}} under the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act, 2002 and in exercise of Powers conferred under Section 13 read with Rule 3 of the Security Interest (Enforcement) Rules, 2002, issued a demand notice dated {{demand_date}} calling upon the Borrower Shri/M/s {{borrower}} to repay the amount mentioned in the notice being Rs.{{outstanding}} (In words {{outstanding_words}}) within 60 days from the date of notice/date of receipt of the said notice.
** The borrower having failed to repay the amount, notice is hereby given to the borrower and the public in general that the undersigned has taken possession of the property described herein below in exercise of powers conferred on him under sub-section (4) of section 13 of Act read with Rule 8 of the Security Interest Enforcement) Rules, 2002 on this the {{possession_day}} day of {{possession_month_year}}.
** The borrower's/guarantor's/mortgagor's attention is invited to provisions of sub-section (8) of section 13 of the Act in respect of time available to redeem the secured assets."""

SI10 = Format("SI-10", "Possession notice - immovable property, one borrower (for publication)", "Annexure-13 (Revised SI-10)", "Possession notice (immovable)",
f"""# Annexure-13 (Revised SI-10)
# POSSESSION NOTICE
## (For Immovable property)
{_POSS_NOTICE_HEAD}
The borrower in particular and the public in general is hereby cautioned not to deal with the property and any dealings with the property will be subject to the charge of {{{{bank_name}}}} for an amount of Rs.{{{{outstanding}}}} and interest thereon.
## Description of immovable property
{{{{property_description}}}}
Bounded: On the North by {{{{north}}}}; On the South by {{{{south}}}}; On the East by {{{{east}}}}; On the West by {{{{west}}}}
DATE: {{{{notice_date}}}}   PLACE: {{{{place}}}}
>> {{{{officer}}}}, {{{{designation}}}}
>> Authorised Officer, {{{{bank_name}}}}""", (
    ("demand_date", "Date of demand notice", ""), ("possession_day", "Possession day (e.g. 12th)", ""),
    ("possession_month_year", "Possession month & year", ""), ("property_description",
     "Description: Flat/Plot No., Survey No., Khasra No., sub-district, district", "security_desc"),
    ("north", "North", ""), ("south", "South", ""), ("east", "East", ""), ("west", "West", ""),
    ("place", "Place", "branch"), ("notice_date", "Date", "today")))

_MULTI_HEAD = """Whereas
{{bank_name}}/ the Authorised Officer/s of {{bank_name}} under the Securitisation and Reconstruction of Financial Assets & Enforcement of Security Interest Act, 2002, and in exercise of powers conferred under Section 13 read with the Security Interest (Enforcement) Rules, 2002, issued demand notice/s on the dates mentioned against each account calling upon the respective borrower/s to repay the amount as mentioned against each account within 60 days from the date of notice(s)/ date of receipt of the said notice(s).
** The borrower having failed to repay the amount, notice is hereby given to the borrower and the public in general that the undersigned has taken possession of the property described herein below in exercise of powers conferred on him under sub-section (4) of Section 13 of Act read with Rule 8 of the Security Interest Enforcement) Rules, 2002 on this the {{possession_day}} day of {{possession_month_year}}.
** The borrower's/guarantor's/mortgagor's attention is invited to provisions of sub-section (8) of section 13 of the Act in respect of time available to redeem the secured assets.
The borrower/s in particular and the public in general is hereby cautioned not to deal with the property/ies and any dealing with the property/ies will be subject to the charge of {{bank_name}} for the amounts and interest thereon.
|S.No.|Name of the branch|Name of the Account|Name of the borrower (Owner of the property mortgaged)|Description of the property mortgaged|Date of demand notice|Date of possession notice affixed|Amount outstanding as on date of demand notice|Name of the Authorised Officer/s|
|1|{{branch}}|{{account_no}}|{{borrower}}|{{security_desc}}|{{demand_date}}|{{possession_date}}|{{outstanding}}|{{officer}}|"""
_MULTI_FIELDS = (("demand_date", "Date of demand notice", ""), ("possession_date", "Date possession notice affixed", ""),
                 ("possession_day", "Possession day", ""), ("possession_month_year", "Month & year", ""),
                 ("place", "Place", "branch"), ("notice_date", "Date", "today"))

SI10A = Format("SI-10A", "Common possession notice - several borrowers, same Authorised Officer", "Annexure-14 (Revised SI-10A)", "Possession notice (immovable)",
f"""# Annexure-14 (Revised SI-10A)
## (For publication purposes)
# POSSESSION NOTICE
## Common Possession Notice for Immovable Properties of more than one borrower by the same Authorised Officer
{_MULTI_HEAD}
Date: {{{{notice_date}}}}   Place: {{{{place}}}}
>> {{{{officer}}}}, {{{{designation}}}}
>> Authorised Officer, {{{{bank_name}}}}""", _MULTI_FIELDS)

SI10B = Format("SI-10B", "Common possession notice - several borrowers, different Authorised Officers", "Annexure-15 (Revised SI-10B)", "Possession notice (immovable)",
f"""# Annexure-15 (Revised SI-10B)
## (For publication purposes)
# POSSESSION NOTICE
## Common Possession Notice for Immovable Properties in case of more than one borrower by the respective Authorised Officers
{_MULTI_HEAD}
Date: {{{{notice_date}}}}   Place: {{{{place}}}}
>> Authorised Officers, {{{{bank_name}}}}""", _MULTI_FIELDS)

SI13 = Format("SI-13", "30-day notice of intended sale to borrower/guarantors", "Named in circular (Rule 8(6)/6(2)); wording is a DRAFT, conform to SARFAESI Manual SI-13", "Sale notice",
"""# NOTICE OF SALE OF SECURED ASSETS (DRAFT - conform to SARFAESI Manual Form SI-13)
>> Date: {{notice_date}}
{{borrower}}
{{address}}
** Reg: Account No. {{account_no}} - sale of secured assets u/s 13(4) of the SARFAESI Act under Rules 6 and 8
Possession of the secured assets was taken by the Bank on {{possession_date}}. The secured debt of Rs.{{outstanding}} ({{outstanding_words}}) with interest remains unpaid.
The Bank intends to sell the secured assets described below by {{mode_of_sale}} on {{sale_date}} at {{sale_time}}, at the Reserve Price of Rs.{{reserve_price}}, on "as is where is, as is what is and whatever there is" basis. Earnest money deposit: Rs.{{emd}}. The sale will be subject to confirmation by the Secured Creditor.
Secured assets: {{security_desc}}
This is a 30 days' notice. You may pay the entire dues with costs and charges before the date of sale and redeem the secured assets (section 13(8)). Dues payable to the Central/State/local Government against the property, if any: {{govt_dues}}
For {{bank_name}}
>> {{officer}}, {{designation}}
>> AUTHORISED OFFICER""", (
    ("notice_date", "Date of notice", "today"), ("possession_date", "Date of possession", ""),
    ("mode_of_sale", "Mode (public auction / e-auction / tender)", "e-auction"), ("sale_date", "Date of sale", ""),
    ("sale_time", "Time", ""), ("reserve_price", "Reserve price (Rs.)", ""), ("emd", "EMD (Rs.)", ""),
    ("govt_dues", "Dues to Govt./local authority", "")), draft=True)

SI15 = Format("SI-15", "Sale certificate - movable property", "Annexure-16 (Revised SI-15), Rule 7(2)", "Sale certificate",
"""# Annexure-16 (Revised SI-15)
## [Rule 7(2)]
# Sale Certificate
## (For movable property)
Whereas the undersigned being the Authorised Officer of {{bank_name}} under the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act, 2002 and in exercise of the powers conferred under Sub Section 4 and 12 of Section 13 read with Rule 6 & 7 of the Security Interest (Enforcement) Rules, 2002 has in consideration of the payment of Rs.{{sale_price}} (Rs. {{sale_price_words}}) sold on behalf of {{bank_name}} in favour of {{purchaser}} (Purchaser), the following movable property secured in favour of {{bank_name}} by {{borrower}} (the names of the borrowers) towards the financial facility {{facility}} (description) offered by/availed from {{bank_name}}. The undersigned acknowledges the receipt of the sale price in full and hands over the delivery and possession of the items listed below.
Description of the movable property: {{security_desc}}
>> {{officer}}, {{designation}}
>> Authorised Officer, {{bank_name}}
Date: {{notice_date}}   Place: {{place}}""", (
    ("sale_price", "Sale price (Rs.)", ""), ("sale_price_words", "Sale price in words", ""),
    ("purchaser", "Purchaser", ""), ("place", "Place", "branch"), ("notice_date", "Date", "today")))

SI17 = Format("SI-17", "Sale certificate - immovable property", "Annexure-17 (Revised SI-17), Rule 9(6)", "Sale certificate",
"""# Annexure-17 (Revised SI-17)
## [Rule 9(6)]
# SALE CERTIFICATE
## (For Immovable property)
Whereas the undersigned being the Authorised Officer of {{bank_name}} (secured creditor) under the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act, 2002 and in exercise of powers conferred under Section 13 read with Rule 8 & 9 of the Security Interest (Enforcement) Rules, 2002 sold on behalf of {{bank_name}} in favour of {{purchaser}} (purchaser), the immovable property shown in the schedule below secured in favour of {{bank_name}} by {{borrower}} (the names of the borrowers) towards the financial facility {{facility}} (description) offered by/availed from {{bank_name}}. The undersigned acknowledges the receipt of the sale price viz., Rs.{{sale_price}} (Rupees {{sale_price_words}} only) in full and hands over the delivery and possession of the scheduled property.
?free_of_encumbrances|The sale of the scheduled property was made free from all encumbrances known to the secured creditor listed below (list I) on deposit of the money demanded by the undersigned.
?not_free|The sale of the scheduled property was made without freeing from encumbrances listed below (list II).
## Description of immovable property
{{property_description}}
Bounded: On the North by {{north}}; On the South by {{south}}; On the East by {{east}}; On the West by {{west}}
List I - List of encumbrances freed from (Encumbrance / Deposit made-amount adjusted): {{list1}}
List II - List of encumbrances not freed from, and subject to which sale made: {{list2}}
>> {{officer}}, {{designation}}
>> Authorised Officer, {{bank_name}}
Date: {{notice_date}}   Place: {{place}}""", (
    ("sale_price", "Sale price (Rs.)", ""), ("sale_price_words", "Sale price in words", ""), ("purchaser", "Purchaser", ""),
    ("property_description", "Description of property", "security_desc"),
    ("north", "North", ""), ("south", "South", ""), ("east", "East", ""), ("west", "West", ""),
    ("free_of_encumbrances", "Sold free from known encumbrances", True), ("not_free", "Sold subject to encumbrances", False),
    ("list1", "List I", ""), ("list2", "List II", ""), ("place", "Place", "branch"), ("notice_date", "Date", "today")))

_SUPP_HEAD = """This Supplementary Agreement is executed at {{place}} on this {{agreement_day}} day of {{agreement_month}} between M/s {{borrower}} ({{constitution}}, {{address}}) (hereinafter referred to as "the Borrower" which term shall include its successors and assigns) and {{bank_name}}, a body corporate constituted under Banking Companies (Acquisition and Transfer of Undertakings) Act, 1970 having its Head Office at {{bank_hq}} and, inter alia, a Branch Office at {{branch}} (hereinafter referred to as "the Bank" which term shall include its successors and assigns).
WHEREAS the Borrower has availed, inter alia, the following facility/ies from the Bank: {{facility}}, limit Rs.{{limit_amt}}.
WHEREAS the above said facility/ies has/have been secured by the following securities: {{security_desc}}.
WHEREAS the Bank, in terms of the provisions of the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act, 2002 (SARFAESI ACT), has issued 60 days notice/have taken further steps, namely {{steps_taken}} in exercise of the powers given under the Act, in respect of the said security (hereafter referred to as 'the said security').
WHEREAS the borrower has shown his / her inability to pay the total outstanding amount under the said credit facilities within the prescribed period."""

_SUPP_COMMON_FIELDS = (("place", "Place", "branch"), ("agreement_day", "Day", ""), ("agreement_month", "Month & year", ""),
                       ("steps_taken", "Steps taken under the Act", ""))
_SUPP_SIGN = """IN WITNESS WHEREOF, the parties hereto have signed these presents on the day, month and year above mentioned.
>> For {{borrower}} (BORROWER)
>> For {{bank_name}} (AUTHORISED SIGNATORY)"""

SUPP_A = Format("ANNEX-10A", "Supplementary agreement - SARFAESI action held in abeyance for OTS", "Annexure-10-A", "Abeyance",
f"""# Annexure-10-A
# SUPPLEMENTARY AGREEMENT
## (In case OTS)
{_SUPP_HEAD}
WHEREAS the borrower proposed to enter into a compromise / one time settlement in the account.
WHEREAS the Borrower has requested the Bank to hold on the enforcement of security interest in respect of the said security.
WHEREAS the Bank has agreed to the proposal of the borrower for compromise on the following terms and conditions and also to hold on enforcement of security interest during implementation of compromise proposal.
NOW, THIS AGREEMENT WITNESSETH:
1. The Borrower agrees and acknowledges that the amount outstanding in respect of the abovesaid facility/ies as on {{{{as_on}}}} is Rs.{{{{outstanding}}}} (Rupees {{{{outstanding_words}}}}) as under: {{{{facility}}}}.
2. The Bank and the Borrower have agreed that if and only if the borrower pays without default Rs.{{{{ots_amount}}}} (Rupees {{{{ots_words}}}}) along with interest @ {{{{ots_interest}}}} from time to time as per the following time schedule, Bank will hold on the enforcement of security interest. Time schedule: {{{{time_schedule}}}}
3. Further if and only if the Borrower pays the amount without default as above said, all the amount due to the bank, as stated in clause 1 above, will stand discharged.
?possession_restored|4. The Bank and the Borrower agree that possession notice earlier issued by the Bank be treated as not having acted upon. The Borrower confirms that the possession of the secured asset taken by the Bank, has been restored back to him / them in good condition as was taken by the Bank.
?possession_retained|4. (OR) The Borrower agrees that the security is taken possession of by the Bank as per procedure prescribed under the Security Interest (Enforcement) Rules, 2002 and the Bank will not proceed further for sale, to facilitate the fulfillment of compromise terms by the Borrower.
5. The Borrower confirms the continuance of the said security and other securities as before.
6. The borrower agrees that in the event of any default in payment of the compromise amount by the borrower: a) All concessions granted as above, shall lapse and the Bank shall be entitled to recover entire amount with further interest and costs as stated in the clause 1 above. b) Bank will be entitled to resume process of taking possession / sale of the security from the point where it was 'held on' and Bank's decision in this regard will be final and binding upon borrower.
7. The Borrower agrees that all other terms and conditions as contained in the loan and security documents continue to be in force and be binding, save and except those modified as above.
8. This Supplementary Agreement is in addition to the loan and security documents executed by the Borrower.
{_SUPP_SIGN}""", _SUPP_COMMON_FIELDS + (
    ("ots_amount", "OTS amount (Rs.)", ""), ("ots_words", "OTS amount in words", ""), ("ots_interest", "Interest rate", ""),
    ("time_schedule", "Time schedule", ""), ("possession_restored", "Possession restored to borrower", True),
    ("possession_retained", "Bank retains possession, no sale", False)))

CONSENT_A = Format("ANNEX-10A-1", "Guarantor's letter of consent (OTS)", "Annexure-10-A-1 (stamp as an agreement; not to be attested/witnessed)", "Abeyance",
"""# Annexure-10A-1
## NOTE: To be stamped as an agreement. Not to be Attested/Witnessed
# LETTER OF CONSENT FROM GUARANTOR
>> PLACE: {{place}}   DATE: {{notice_date}}
The Branch Manager, {{bank_name}}, BO: {{branch}}
Dear Sir,
** Reg: M/s {{borrower}} (Borrower), Facility {{facility}} Account No. {{account_no}}
The Borrower has been availing the credit facility/ies as above said. The above credit facility/ies, inter alia, has/have been guaranteed by me/us vide guarantee deed / letter of guarantee dated {{guarantee_date}}.
The Bank has issued demand notice to borrower u/s 13(2) of SARFAESI Act / has taken further steps namely {{steps_taken}} in terms of the provisions of the Act.
The Borrower has entered into a compromise / one time settlement with the Bank. In terms of the compromise the Bank and the borrower has agreed that if and only if the borrower pays without default a sum of Rs.{{ots_amount}} (Rupees {{ots_words}} only) along with interest @ {{ots_interest}} PA from time to time as per the time schedule agreed upon between the bank and the borrower, bank will hold on the enforcement of the security interest, as stated in supplementary agreement dated {{agreement_date}}.
I/We give consent to the arrangement as above said as per the Supplementary Agreement/s dated {{agreement_date}}.
I/We agree that the Guarantee/s dated {{guarantee_date}} already executed by me/us will continue to be in force and binding on us.
I/We confirm and acknowledge that the mortgage/hypothecation security, as created/executed by me/us continues to be in force and secures the above facility/ies availed/being availed by the Borrower.
Thanking you,
Yours faithfully,
>> [GUARANTOR(S)] {{guarantor}}""", (
    ("place", "Place", "branch"), ("notice_date", "Date", "today"), ("guarantee_date", "Guarantee deed date", ""),
    ("steps_taken", "Steps taken", ""), ("ots_amount", "OTS amount (Rs.)", ""), ("ots_words", "In words", ""),
    ("ots_interest", "Interest %", ""), ("agreement_date", "Supplementary agreement date", ""),
    ("guarantor", "Guarantor name", "first_guarantor")))

SUPP_B = Format("ANNEX-10B", "Supplementary agreement - SARFAESI action held in abeyance (reasons other than OTS)", "Annexure-10-B", "Abeyance",
f"""# Annexure-10-B
# SUPPLEMENTARY AGREEMENT
## (SARFAESI Action kept in Abeyance - Reasons other than OTS)
{_SUPP_HEAD}
WHEREAS the Borrower has requested the Bank to hold on the enforcement of security interest in respect of the said security due to the reason {{{{reason}}}}.
Whereas the bank has agreed to the justification/reason given by the borrower and also to hold on enforcement of security interest {{{{hold_period}}}} (not exceeding a period of 60 days).
NOW, THIS AGREEMENT WITNESSETH:
1. The Borrower agrees and acknowledges that the amount outstanding in respect of the abovesaid facility/ies is Rs.{{{{outstanding}}}} (Rupees {{{{outstanding_words}}}} only) on {{{{as_on}}}} as under: {{{{facility}}}}.
?possession_restored|2. The Bank and the Borrower agree that possession notice earlier issued by the Bank be treated as not having acted upon. The Borrower confirms that the possession of the secured asset taken by the Bank, has been restored back to him / them in good condition as was taken by the Bank.
?possession_retained|2. (OR) The Borrower agrees that the security is taken possession of by the Bank as per procedure prescribed under the Security Interest (Enforcement) Rules, 2002 and the Bank will not proceed further for sale due to the reason mentioned as above.
3. The Borrower confirms the continuance of the said security and other securities as before.
4. In the event of any default/unable to sort out the reasons to hold on SARFAESI action within prescribed period, Bank will be entitled to resume process of taking possession / sale of the security from the point where it was 'held on'. The Borrower agrees that in that eventuality, no fresh notice of possession will be issued by the Bank.
5. The Borrower agrees that all other terms and conditions as contained in the loan and security documents continue to be in force and be binding, save and except those modified as above.
6. This Supplementary Agreement is in addition to the loan and security documents executed by the Borrower.
{_SUPP_SIGN}""", _SUPP_COMMON_FIELDS + (
    ("reason", "Reason for holding on", ""), ("hold_period", "Hold-on period", ""),
    ("possession_restored", "Possession restored to borrower", True), ("possession_retained", "Bank retains possession, no sale", False)))

CONSENT_B = Format("ANNEX-10B-1", "Guarantor's letter of consent (reasons other than OTS)", "Annexure-10-B-1 (stamp as an agreement; not to be attested/witnessed)", "Abeyance",
"""# Annexure-10B-1
## NOTE: To be stamped as an agreement. Not to be Attested/Witnessed
# LETTER OF CONSENT FROM GUARANTOR
>> PLACE: {{place}}   DATE: {{notice_date}}
The Branch Manager, {{bank_name}}, BO: {{branch}}
Dear Sir,
** Reg: M/s {{borrower}} (Borrower), Facility {{facility}} Account No. {{account_no}}
The Borrower has been availing the credit facility/ies as above said. The above credit facility/ies, inter alia, has/have been guaranteed by me/us vide guarantee deed / letter of guarantee dated {{guarantee_date}}.
The Bank has issued demand notice / has taken further steps namely {{steps_taken}} in terms of the provisions of the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act, 2002 (SARFAESI ACT).
To sort out the reason/justification given by the borrower within {{hold_period}} (period) acceptable to the Bank and bank has agreed to hold on SARFAESI action as stated in the supplementary agreement, I/We give consent to the arrangement as above said as per the Supplementary Agreement/s dated {{agreement_date}}.
I/We agree that the Guarantee/s dated {{guarantee_date}} already executed by me/us will continue to be in force and binding on us.
I/We confirm and acknowledge that the mortgage/hypothecation security, as created/executed by me/us continues to be in force and secures the above facility/ies availed/being availed by the Borrower.
Thanking you,
Yours faithfully,
>> [GUARANTOR(S)] {{guarantor}}""", (
    ("place", "Place", "branch"), ("notice_date", "Date", "today"), ("guarantee_date", "Guarantee deed date", ""),
    ("steps_taken", "Steps taken", ""), ("hold_period", "Period", ""), ("agreement_date", "Supplementary agreement date", ""),
    ("guarantor", "Guarantor name", "first_guarantor")))

ANNEX11 = Format("ANNEX-11", "Notice to borrower for details of book debts and receivables", "Annexure-11", "Book debts",
"""# Annexure-11
## (Notice to the Borrower for providing details of Book Debts and Receivables)
## {{bank_name}}
## BO: {{branch}}  (Telephone No. {{branch_phone}}; Email {{branch_email}})
To, Sh. / M/s {{borrower}}
{{address}}
>> Date: {{notice_date}}
** Reg: Your NPA A/c {{account_no}}
Sir,
You, Sh./ M/s {{borrower}} availed credit facilities from {{bank_name}}, BO: {{branch}} and have failed to pay the amount due to the Bank in respect of the secured debt amounting to Rs.{{outstanding}} as on {{as_on}} and further interest payable thereunder for the period commencing immediately after the said date.
You hypothecated with the bank your present and future book debts and other money receivables by way of first charge as continuing security to the bank for due repayment of the debts.
Further, as per the terms and conditions of loan/credit facilities availed by you, You are required to submit statement of book-debts hypothecated to Bank on the prescribed format provided to you in time and regularly at the {{stipulated_period}} intervals. You submitted the statement lastly on {{last_statement_date}} for the month {{last_statement_month}}. However, thereafter, You have not submitted the statement and got the books of accounts/register inspected and verified by the bank officials.
You are requested to submit/provide the details of all the book-debts and receivables within 15 days without fail to the Branch as under:
|S.No.|Name & Address of the Debtor|Amount Due|Date Since When Due|
|1| | | |
|2| | | |
>> BRANCH MANAGER""", (
    ("notice_date", "Date", "today"), ("branch_phone", "Branch phone", ""), ("branch_email", "Branch e-mail", ""),
    ("stipulated_period", "Stipulated periodicity (e.g. monthly)", "monthly"),
    ("last_statement_date", "Statement last submitted on", ""), ("last_statement_month", "For the month", "")))

ANNEX12 = Format("ANNEX-12", "Public notice to borrower and its debtors (book debts)", "Annexure-12", "Book debts",
"""# Annexure-12
## (Notice To M/s {{borrower}} (Borrower) and the Debtors of M/s {{borrower}} (Borrower))
## {{bank_name}}
## BO: {{branch}}  (Telephone No. {{branch_phone}}; Email {{branch_email}})
# PUBLIC NOTICE
Whereas M/s {{borrower}} (herein after called the borrower) having Registered Office at {{address}} availed credit facilities from {{bank_name}}, BO: {{branch}}. On account of default committed by the borrower accounts of the borrower have been classified as Non Performing Assets by the Bank with outstanding balance of Rs.{{outstanding}} as on {{as_on}}.
Demand Notice U/s 13(2) of the Securitisation and Reconstruction of Financial Asset and Enforcement of Security Interest Act (SARFAESI Act) 2002 on {{demand_date}} has been issued to the borrower to discharge its liability in full. The Book Debts and other receivables of the borrower are hypothecated/ charged with the Bank as a security and as such are secured asset of the Bank.
Notice is hereby given to M/s. {{borrower}} (Borrower) prohibiting and restraining it from recovering the debts due from its debtors and interest thereon and all the Debtors of M/S. {{borrower}} (the borrower) are prohibited and restrained from making payment of the said debt or any part thereof or any interest thereon to the borrower or to any person whomsoever, otherwise than to the undersigned. The Debtors are hereby called upon and directed to make payment to the undersigned. The payment made to the undersigned shall give valid discharge as if payment has been made to the Borrower.
Further, any contravention of the Provisions of SARFAESI Act, 2002/Rules is an offence in terms of Section 29 of the said Act.
In case of any query please contact the undersigned personally.
For {{bank_name}}
Date: {{notice_date}}   Place: {{place}}
>> {{designation}}
>> AUTHORISED OFFICER {{officer}}""", (
    ("notice_date", "Date", "today"), ("demand_date", "Date of 13(2) notice", ""), ("place", "Place", "branch"),
    ("branch_phone", "Branch phone", ""), ("branch_email", "Branch e-mail", "")))

FORMATS: dict[str, Format] = {f.key: f for f in (
    SI4, SI4A, REPLY, SI6, SI7A, SI7B, SI7C, SI7D, SI10, SI10A, SI10B, SI13, SI15, SI17,
    SUPP_A, CONSENT_A, SUPP_B, CONSENT_B, ANNEX11, ANNEX12)}

# Forms named in the circular but whose wording lives in the SARFAESI Manual 2008 (not reproduced here).
MANUAL_FORMS = {
    "SI-2": "Branch Head's note for recall / sanction of SARFAESI action",
    "SI-8": "Inventory of movables (Rule 4(2))",
    "SI-9": "Inventory of immovables",
    "SI-14": "Proclamation of Sale (public notice)",
    "SI-16": "Receipt for sale price (movables, when no certificate wanted)",
    "SI-18A": "Bidders' acceptance of terms and conditions of auction",
    "SI-19": "Bid sheet",
    "SI-20": "Bio-data of highest bidder",
    "SI-21": "Communication of acceptance of bid",
    "SI-22": "Confirmation of sale by secured creditor (immovables)",
    "SI-23": "Agreement to sell",
    "SI-24": "Invitation for tender",
    "SI-25": "Tender terms and conditions",
    "SI-26": "Covering letter for sealed tender",
    "SI-28": "Notice to debtors of the borrower (book debts)",
    "SEC14": "Application and affidavit to DM/CMM u/s 14",
}

OBJECTIONS = [  # Annexure-5 guidance
    ("Denial that account has been NPA", "Explain how account has been classified as NPA as per extant guidelines of RBI/Bank."),
    ("Denial of loan", "Deny and refer to loan application and loan documents executed supported with proof of end utilization, and particulars of specific release etc."),
    ("Denial of execution of loan documents", "Loan documents executed supported with other correspondence, if any."),
    ("Denial of creation of charge / mortgage", "Loan/security documents like hypothecation agreements/mortgage charge created, and if registered/filed with statutory authorities (Sub-Registrar, ROC, RTO, Central Registry under SARFAESI Act), be referred to."),
    ("Denial of guarantee by guarantors and resort to borrower's securities first", "Liability of the guarantors is joint, several and co-extensive with that of the borrower and bank can resort to any security."),
    ("Claim barred by limitation", "Deny and refer to operations in the account (debit/credit transactions or last instalment deposited), loan documents executed, recall notice served, invocation of guarantee, balance confirmation letter or the balance sheet of the party, if available."),
    ("Rate of interest not correctly charged / penal interest wrongly charged / rate is high", "Explain that interest has been charged as per sanction letter, loan documents and various circulars and is not contrary to RBI guidelines/Bank's policy."),
    ("Debits of various charges / expenses disputed", "Deny, refer to enabling clauses in the loan documents and Bank guidelines."),
    ("Claim is not correct", "Deny and refer to balance confirmation letters executed or the balance sheet of the party, if available."),
    ("Statement of account not furnished / received", "State that statement of account furnished from time to time. However furnish a copy of statement of account again to the borrower."),
    ("Bank cannot take action without filing suit or take possession without order of the court", "No such bar is prescribed under SARFAESI Act. Civil Court has no jurisdiction for steps taken under this Act."),
    ("Simultaneous action under SARFAESI cannot be resorted to as Civil Case/DRT case is pending", "Supreme Court in Transcore v/s Union of India (judgment dt. 29.11.2006) held that remedies under DRT Act and Securitization Act can be simultaneously resorted to."),
    ("Requests for time, tagging, restructuring, rescheduling, rephasement, OTS", "Consider on merits as per extant guidelines and decide quickly at the appropriate level; inform the borrower, subject to executing a Supplementary Agreement to keep further action under SARFAESI in abeyance."),
]
