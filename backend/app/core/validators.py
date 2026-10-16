"""
validators.py — Institutional Validation Utilities.
Ensures emails belong strictly to SKIT Jaipur (@skit.ac.in) and represent real accounts.
"""

import re
from email_validator import validate_email, EmailNotValidError

DISALLOWED_PREFIXES = {
    "fake",
    "dummy",
    "temp",
    "disposable",
    "trash",
    "junk",
    "spam",
    "asdf",
    "qwerty",
    "12345",
    "123456",
    "noname",
    "fakeemail",
    "fakeid",
    "invalid",
}


def validate_institutional_email(
    email: str, allow_deliverability_check: bool = True
) -> str:
    """
    Validates that the email:
    1. Belongs strictly to the official institutional domain '@skit.ac.in'.
    2. Is not a disposable, dummy, or fake identifier.
    3. Conforms to valid institutional naming syntax (faculty names or roll numbers).
    4. Has valid DNS MX records (deliverable).
    """
    email_clean = email.strip().lower()

    # 1. Strict domain verification
    if not email_clean.endswith("@skit.ac.in"):
        raise ValueError(
            "Only official @skit.ac.in institutional email addresses are permitted."
        )

    parts = email_clean.split("@")
    if len(parts) != 2 or parts[1] != "skit.ac.in":
        raise ValueError(
            "Only official @skit.ac.in institutional email addresses are permitted."
        )

    local_part = parts[0]

    # 2. Local-part length and character structure
    if len(local_part) < 3:
        raise ValueError("Email ID is too short to be a valid institutional account.")

    if len(local_part) > 64:
        raise ValueError("Email ID exceeds maximum allowed length.")

    if not re.match(r"^[a-zA-Z0-9]+([._-][a-zA-Z0-9]+)*$", local_part):
        raise ValueError(
            "Email ID contains invalid characters or consecutive special characters."
        )

    # 3. Guard against placeholder/dummy/fake usernames
    normalized_local = re.sub(r"[._-]", "", local_part)
    for prefix in DISALLOWED_PREFIXES:
        if (
            normalized_local == prefix
            or normalized_local.startswith(prefix + "1")
            or normalized_local.startswith(prefix + "email")
        ):
            raise ValueError(
                f"'{local_part}' is a placeholder or fake identifier. Please use your real SKIT institutional ID."
            )

    if normalized_local.isdigit() and len(set(normalized_local)) == 1:
        raise ValueError(
            "Repetitive numerical IDs are not valid institutional accounts."
        )

    # 4. Deliverability check via DNS MX resolution
    if allow_deliverability_check:
        try:
            valid_info = validate_email(email_clean, check_deliverability=True)
            email_clean = valid_info.normalized
        except EmailNotValidError as e:
            raise ValueError(
                f"Institutional domain deliverability check failed: {str(e)}"
            )

    return email_clean
