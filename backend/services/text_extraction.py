import re
from bs4 import BeautifulSoup


def extract_sections_from_filing(text: str):
    """Extract Risk Factors and MD&A from an SEC filing."""

    # --------------------------------------------------
    # 1. Convert HTML to plain text
    # --------------------------------------------------

    soup = BeautifulSoup(text, "html.parser")

    text = soup.get_text(" ", strip=True)

    # --------------------------------------------------
    # 2. Normalize whitespace
    # --------------------------------------------------

    text = re.sub(r'\s+', ' ', text).strip()

    # --------------------------------------------------
    # 3. Extract Risk Factors - Item 1A
    # --------------------------------------------------

    risk_pattern = re.compile(
        r'''
        Item\s+1A\.?\s+
        Risk\s+Factors
        (.*?)
        (?=
            Item\s+1B\b
            |
            Item\s+2\b
            |
            $
        )
        ''',
        re.IGNORECASE | re.DOTALL | re.VERBOSE
    )

    risk_matches = list(risk_pattern.finditer(text))

    risk_factors = None

    if risk_matches:

        # Remove obvious Table of Contents matches.
        # Real Risk Factors sections are usually very large.
        valid_risk_matches = [
            match
            for match in risk_matches
            if len(match.group(1)) > 1000
        ]

        if valid_risk_matches:
            risk_match = max(
                valid_risk_matches,
                key=lambda match: len(match.group(1))
            )

            risk_factors = risk_match.group(1).strip()

    # --------------------------------------------------
    # 4. Extract MD&A - Item 7
    # --------------------------------------------------

    # Find where Item 1A (Risk Factors) begins.
    # This helps skip Item 7 references inside Risk Factors.
    item1a_match = re.search(
        r'Item\s+1A\.?\s+Risk\s+Factors',
        text,
        re.IGNORECASE
    )

    item1a_position = item1a_match.start() if item1a_match else 0

    # Find every "Item 7" occurrence.
    item7_pattern = re.compile(
        r'Item\s+7\.?',
        re.IGNORECASE
    )

    item7_matches = list(item7_pattern.finditer(text))

    # Only consider Item 7 occurrences after Item 1A.
    valid_item7_matches = [
        match
        for match in item7_matches
        if match.start() > item1a_position
    ]

    mda_candidates = []

    for match in valid_item7_matches:

        # Start looking immediately after "Item 7".
        start = match.end()

        # Look at the next 300 characters for the MD&A heading.
        heading_area = text[start:start + 300]

        heading_area_clean = re.sub(
            r'\s+',
            ' ',
            heading_area
        )

        # Check for "Management's Discussion and Analysis".
        heading_match = re.search(
            r"Management\W?s\s+Discussion\s+and\s+Analysis",
            heading_area_clean,
            re.IGNORECASE
        )

        if not heading_match:
            continue

        # --------------------------------------------------
        # Find the actual MD&A content
        # --------------------------------------------------

        content_area = text[start:start + 1000]

        content_anchor = re.search(
            r'The\s+following\s+discussion',
            content_area,
            re.IGNORECASE
        )

        if not content_anchor:
            continue

        section_start = start + content_anchor.start()

        # --------------------------------------------------
        # Find the end of MD&A
        # --------------------------------------------------

        # Try Item 7A first.
        item7a_match = re.search(
            r'Item\s+7A\.?',
            text[section_start:],
            re.IGNORECASE
        )

        if not item7a_match:

            # Use Item 8 as a fallback.
            item8_match = re.search(
                r'Item\s+8\.?',
                text[section_start:],
                re.IGNORECASE
            )

            if not item8_match:
                continue

            section_end = section_start + item8_match.start()

        else:
            section_end = section_start + item7a_match.start()

        # Extract the MD&A content.
        candidate = text[section_start:section_end].strip()

        # Ignore very short matches.
        if len(candidate) > 800:
            mda_candidates.append(candidate)

    # --------------------------------------------------
    # 5. Choose the best MD&A candidate
    # --------------------------------------------------

    mda = None

    if mda_candidates:

        good_candidates = []
        fallback_candidates = []

        for candidate in mda_candidates:

            has_anchor = bool(
                re.search(
                    r'The\s+following\s+discussion',
                    candidate,
                    re.IGNORECASE
                )
            )

            if has_anchor:
                good_candidates.append(candidate)
            else:
                fallback_candidates.append(candidate)

        if good_candidates:
            mda = max(
                good_candidates,
                key=len
            )

        elif fallback_candidates:
            mda = max(
                fallback_candidates,
                key=len
            )

    # --------------------------------------------------
    # 6. Return results
    # --------------------------------------------------

    return {
        "riskFactors": risk_factors,
        "mda": mda
    }