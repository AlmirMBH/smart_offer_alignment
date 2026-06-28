import unicodedata


def sanitize_export_text(export_text: str) -> str:
    normalized_text = unicodedata.normalize("NFC", export_text)
    sanitized_characters: list[str] = []
    for character in normalized_text:
        if character == "\ufffd":
            continue
        if unicodedata.category(character) == "Cc":
            continue
        sanitized_characters.append(character)
    return "".join(sanitized_characters)


def sanitize_export_cell_value(cell_value: str | float | int | None) -> str | float | int:
    if cell_value is None:
        return ""
    if isinstance(cell_value, str):
        return sanitize_export_text(cell_value)
    return cell_value
