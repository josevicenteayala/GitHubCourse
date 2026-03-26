import re


def normalize_username(name: str) -> str:
    """Normalize a username.

    Rules:
    - Trim outer whitespace.
    - Convert to lowercase.
    - Replace one or more spaces with a single underscore.
    - Remove any character that is not a-z, 0-9, or underscore.
    - Strip leading/trailing underscores.
    """
    normalized = name.strip().lower()
    normalized = re.sub(r"\s+", "_", normalized)
    normalized = re.sub(r"[^a-z0-9_]", "", normalized)
    return normalized.strip("_")

def build_slug(title: str) -> str:
    """Convert a title into a URL-friendly slug.

    Rules:
    - Lowercase.
    - Keep letters and digits.
    - Replace any sequence of non-alphanumeric characters with a single '-'.
    - Strip leading/trailing '-'.
    """
    # Extract alphanumeric word chunks, then join with single hyphens.
    words = re.findall(r"[a-z0-9]+", title.lower())
    return "-".join(words)