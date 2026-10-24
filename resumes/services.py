import re

import pymupdf


def extract_text_from_pdf(file):
    """
    Extract text from an uploaded PDF.
    """

    document = pymupdf.open(
        stream=file.read(),
        filetype="pdf",
    )

    text = []

    for page in document:
        text.append(page.get_text())

    document.close()

    return "\n".join(text).strip()


def normalize_text(text):
    """
    Normalize text for keyword matching.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9+#.\s-]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def extract_keywords(text):
    """
    Convert text into normalized keyword tokens.
    """

    normalized = normalize_text(text)

    return set(
        normalized.split()
    )


def calculate_ats_score(
    resume_text,
    job_requirements="",
    preferred_qualifications="",
):
    """
    Calculate a basic rule-based ATS score.

    Required qualifications have higher weight
    than preferred qualifications.
    """

    if not resume_text:
        return {
            "score": 0.0,
            "matched_required": [],
            "missing_required": [],
            "matched_preferred": [],
            "missing_preferred": [],
        }

    resume_keywords = extract_keywords(
        resume_text
    )

    required_keywords = extract_keywords(
        job_requirements
    )

    preferred_keywords = extract_keywords(
        preferred_qualifications
    )

    matched_required = sorted(
        resume_keywords
        & required_keywords
    )

    missing_required = sorted(
        required_keywords
        - resume_keywords
    )

    matched_preferred = sorted(
        resume_keywords
        & preferred_keywords
    )

    missing_preferred = sorted(
        preferred_keywords
        - resume_keywords
    )

    required_score = (
        len(matched_required)
        / len(required_keywords)
        * 70
        if required_keywords
        else 0
    )

    preferred_score = (
        len(matched_preferred)
        / len(preferred_keywords)
        * 30
        if preferred_keywords
        else 0
    )

    score = required_score + preferred_score

    return {
        "score": round(score, 2),
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
    }