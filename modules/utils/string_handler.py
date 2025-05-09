import unicodedata


def normalize_string(text: str):
    # Normalize the string to remove inconsistencies in character representation
    normalized_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    return normalized_text
