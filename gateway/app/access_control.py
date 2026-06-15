"""
Access Control Matrix — defines which ministry can read which other ministry's data.

Core principle: A ministry can ONLY update its own data, and can only READ
data from ministries explicitly listed here. Citizens can read ALL their own data.
"""

# ministry → list of ministries it is allowed to READ
ACCESS_MATRIX: dict[str, list[str]] = {
    "health":    ["civil", "social"],
    "finance":   ["civil", "social", "property"],
    "justice":   ["civil", "transport"],
    "transport": ["civil", "justice"],
    "social":    ["civil", "finance", "employment"],
    "education": ["civil"],
    "defense":   ["civil", "health"],
    "property":  ["civil", "finance"],
}

# Roles that bypass the access matrix
BYPASS_ROLES = {"admin", "citizen"}


def can_access(requester_ministry: str, target_ministry: str) -> bool:
    """Check if requester_ministry is allowed to read target_ministry's data."""
    if requester_ministry == target_ministry:
        return True  # A ministry can always read its own data
    allowed = ACCESS_MATRIX.get(requester_ministry, [])
    return target_ministry in allowed


def get_readable_ministries(ministry: str) -> list[str]:
    """Return the list of ministries this ministry can read (including itself)."""
    readable = [ministry]
    readable.extend(ACCESS_MATRIX.get(ministry, []))
    return readable


# Human-readable labels
MINISTRY_LABELS: dict[str, str] = {
    "civil":     "Civil Status",
    "education": "Education",
    "defense":   "Defense",
    "health":    "Health",
    "justice":   "Justice",
    "finance":   "Finance",
    "social":    "Social Affairs",
    "transport": "Transport",
    "property":  "Property",
}
