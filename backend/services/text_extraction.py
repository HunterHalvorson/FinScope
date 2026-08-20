import re
from bs4 import BeautifulSoup


def extract_sections_from_filing(text: str, form: str = "10-K"):
    """
    Robust SEC filing extractor.

    10-K:
        Item 1A -> Risk Factors
        Item 7  -> MD&A

    10-Q:
        Item 1A -> Risk Factors
        Item 2  -> MD&A

    Uses multiple extraction strategies because SEC filings
    can have very different HTML structures.
    """

    form = form.upper().strip()

    # ============================================================
    # 1. HTML -> text
    # ============================================================

    soup = BeautifulSoup(text, "html.parser")

    for tag in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "iframe",
        "object",
        "embed"
    ]):
        tag.decompose()

    # Use separator so headings that are separated by HTML
    # don't get smashed together.
    text = soup.get_text(" ", strip=True)

    text = text.replace("\xa0", " ")

    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return {
            "riskFactors": None,
            "mda": None
        }

    # ============================================================
    # 2. Normalize common SEC formatting
    # ============================================================

    # Normalize curly apostrophes
    text = text.replace("’", "'")
    text = text.replace("‘", "'")

    # Normalize weird spaces
    text = text.replace("\u200b", " ")
    text = text.replace("\ufeff", " ")

    text = re.sub(r"\s+", " ", text).strip()

    # ============================================================
    # 3. Normalize Item headings
    #
    # Handles:
    #
    # ITEM 1A
    # Item 1A.
    # ITEM 1A:
    # Item   1A
    # Item 7
    # ITEM 7.
    # ============================================================

    item_regex = re.compile(
        r"\bITEM\s+"
        r"(1A|1B|7A|"
        r"1|2|3|4|5|6|7|8|9|"
        r"10|11|12|13|14|15|16)"
        r"\b",
        re.IGNORECASE
    )

    # ============================================================
    # 4. Find ALL item occurrences
    # ============================================================

    item_matches = []

    for match in item_regex.finditer(text):

        item = match.group(1).upper()

        # Get text immediately after Item heading.
        after = text[
            match.end():
            match.end() + 250
        ]

        after = re.sub(
            r"\s+",
            " ",
            after
        ).strip()

        item_matches.append({
            "item": item,
            "start": match.start(),
            "end": match.end(),
            "after": after
        })

    # ============================================================
    # 5. Utility: detect likely TOC
    # ============================================================

    def toc_score(value):

        lower = value.lower()

        score = 0

        if "table of contents" in lower:
            score += 20

        # SEC TOCs often contain many "Item X" references.
        item_count = len(
            re.findall(
                r"\bitem\s+(?:1A|1B|7A|[0-9]{1,2})\b",
                lower
            )
        )

        if item_count >= 5:
            score += 8

        if item_count >= 10:
            score += 8

        # Lots of page references
        page_refs = len(
            re.findall(
                r"\b(?:page|pages)\s+\d+\b",
                lower
            )
        )

        if page_refs >= 3:
            score += 5

        # Dot leaders
        dots = len(
            re.findall(
                r"\.{3,}",
                value
            )
        )

        if dots >= 3:
            score += 5

        return score

    # ============================================================
    # 6. Risk scoring
    # ============================================================

    def score_risk(candidate):

        lower = candidate.lower()

        score = 0

        length = len(candidate)

        # Size
        if length > 1000:
            score += 5

        if length > 3000:
            score += 5

        if length > 7000:
            score += 7

        if length > 15000:
            score += 7

        # Risk vocabulary
        terms = [
            "risk",
            "risks",
            "uncertainty",
            "uncertain",
            "adverse",
            "material adverse",
            "volatility",
            "exposure",
            "competition",
            "competitive",
            "regulatory",
            "regulation",
            "litigation",
            "lawsuit",
            "environmental",
            "commodity",
            "commodity prices",
            "dependence",
            "dependent",
            "could adversely",
            "may adversely",
            "could affect",
            "may affect",
            "could materially",
            "may materially",
            "subject to",
        ]

        for term in terms:

            count = lower.count(term)

            if count >= 1:
                score += 2

            if count >= 5:
                score += 2

            if count >= 15:
                score += 3

        # Penalize TOC
        score -= toc_score(candidate[:5000]) * 3

        return score

    # ============================================================
    # 7. MD&A scoring
    # ============================================================

    def score_mda(candidate):

        lower = candidate.lower()

        score = 0

        length = len(candidate)

        if length > 1000:
            score += 5

        if length > 3000:
            score += 5

        if length > 7000:
            score += 7

        if length > 15000:
            score += 7

        strong_terms = [
            "management's discussion",
            "discussion and analysis",
            "results of operations",
            "financial condition",
            "liquidity",
            "capital resources",
            "cash flows",
            "cash flow",
            "operating activities",
            "investing activities",
            "financing activities",
            "critical accounting",
            "critical accounting policies",
            "known trends",
            "known uncertainties",
        ]

        for term in strong_terms:

            count = lower.count(term)

            if count >= 1:
                score += 7

            if count >= 3:
                score += 3

            if count >= 10:
                score += 4

        financial_terms = [
            "revenue",
            "revenues",
            "net income",
            "net loss",
            "operating income",
            "operating loss",
            "earnings",
            "expenses",
            "cash",
            "cash flow",
            "liquidity",
            "capital resources",
            "assets",
            "liabilities",
            "debt",
            "sales",
            "production",
            "merchandise",
            "inventory",
            "gross margin",
            "operating margin",
            "interest expense",
            "depreciation",
            "amortization",
        ]

        financial_count = sum(
            lower.count(term)
            for term in financial_terms
        )

        if financial_count >= 5:
            score += 5

        if financial_count >= 15:
            score += 7

        if financial_count >= 30:
            score += 10

        if financial_count >= 60:
            score += 10

        score -= toc_score(candidate[:5000]) * 3

        return score

    # ============================================================
    # 8. Generic section extraction
    # ============================================================

    def extract_between_items(
        start_items,
        end_items,
        minimum_length=500
    ):

        candidates = []

        for i, match in enumerate(item_matches):

            if match["item"] not in start_items:
                continue

            start = match["end"]

            # ----------------------------------------------------
            # Try every possible ending Item.
            #
            # This is important because a TOC Item 8 can otherwise
            # cause us to stop too early.
            # ----------------------------------------------------

            for next_match in item_matches[i + 1:]:

                if next_match["item"] not in end_items:
                    continue

                end = next_match["start"]

                if end <= start:
                    continue

                candidate = text[start:end].strip()

                if len(candidate) < minimum_length:
                    continue

                candidates.append(candidate)

                # Only the nearest valid ending is normally useful.
                break

        return candidates

    # ============================================================
    # 9. Risk Factors
    # ============================================================

    risk_candidates = extract_between_items(
        {"1A"},
        {"1B", "2"},
        minimum_length=500
    )

    # ============================================================
    # 10. Direct Risk Factors search
    #
    # This catches filings where the Item heading isn't detected
    # cleanly.
    # ============================================================

    risk_heading_patterns = [
        r"\bITEM\s+1A\s*[\.\:\-]?\s*RISK\s+FACTORS\b",
        r"\bITEM\s+1A\b",
        r"\bRISK\s+FACTORS\b"
    ]

    for pattern in risk_heading_patterns:

        matches = list(
            re.finditer(
                pattern,
                text,
                re.IGNORECASE
            )
        )

        for match in matches:

            start = match.end()

            end_match = re.search(
                r"\bITEM\s+(?:1B|2)\b",
                text[start:],
                re.IGNORECASE
            )

            if not end_match:
                continue

            end = start + end_match.start()

            candidate = text[start:end].strip()

            if len(candidate) >= 500:
                risk_candidates.append(candidate)

    # Remove duplicates
    risk_candidates = list(
        dict.fromkeys(risk_candidates)
    )

    # ============================================================
    # 11. Choose Risk Factors
    # ============================================================

    risk_factors = None

    if risk_candidates:

        risk_candidates.sort(
            key=lambda x: (
                score_risk(x),
                len(x)
            ),
            reverse=True
        )

        risk_factors = risk_candidates[0]

    # ============================================================
    # 12. MD&A configuration
    # ============================================================

    if form == "10-Q":

        mda_start_items = {"2"}
        mda_end_items = {"3", "4"}

    else:

        mda_start_items = {"7"}
        mda_end_items = {"7A", "8"}

    # ============================================================
    # 13. MD&A candidates
    # ============================================================

    mda_candidates = extract_between_items(
        mda_start_items,
        mda_end_items,
        minimum_length=500
    )

    # ============================================================
    # 14. Direct MD&A heading search
    # ============================================================

    mda_patterns = [
        r"\bITEM\s+7\s*[\.\:\-]?\s*"
        r"MANAGEMENT['’]?S\s+DISCUSSION\s+AND\s+ANALYSIS",

        r"\bITEM\s+7\b",

        r"MANAGEMENT['’]?S\s+DISCUSSION\s+AND\s+ANALYSIS",

        r"DISCUSSION\s+AND\s+ANALYSIS\s+OF\s+FINANCIAL\s+CONDITION",

        r"RESULTS\s+OF\s+OPERATIONS"
    ]

    if form == "10-Q":

        end_pattern = (
            r"\bITEM\s+(?:3|4)\b"
        )

    else:

        end_pattern = (
            r"\bITEM\s+(?:7A|8)\b"
        )

    for pattern in mda_patterns:

        matches = list(
            re.finditer(
                pattern,
                text,
                re.IGNORECASE
            )
        )

        for match in matches:

            start = match.end()

            end_match = re.search(
                end_pattern,
                text[start:],
                re.IGNORECASE
            )

            if not end_match:
                continue

            end = start + end_match.start()

            candidate = text[start:end].strip()

            if len(candidate) >= 500:

                mda_candidates.append(
                    candidate
                )

    # Remove duplicates
    mda_candidates = list(
        dict.fromkeys(mda_candidates)
    )

    # ============================================================
    # 15. Choose MD&A
    # ============================================================

    mda = None

    if mda_candidates:

        mda_candidates.sort(
            key=lambda x: (
                score_mda(x),
                len(x)
            ),
            reverse=True
        )

        mda = mda_candidates[0]

    # ============================================================
    # 16. Final cleanup
    # ============================================================

    if risk_factors:

        risk_factors = re.sub(
            r"\s+",
            " ",
            risk_factors
        ).strip()

    if mda:

        mda = re.sub(
            r"\s+",
            " ",
            mda
        ).strip()

    # ============================================================
    # 17. Return
    # ============================================================

    return {
        "riskFactors": risk_factors,
        "mda": mda
    }