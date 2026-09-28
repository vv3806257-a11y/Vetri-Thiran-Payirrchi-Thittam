import html
import re


def sanitize_text(text: str) -> str:
    """Normalize text for predictable document export."""
    if not text:
        return ""

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\u2022": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def split_terms(terms: str) -> list[str]:
    """Split semicolon-separated terms into clean clauses."""
    return [
        item.strip(" -\t")
        for item in terms.replace("\n", ";").split(";")
        if item.strip()
    ]


def format_html_preview(text: str) -> str:
    """Turn plain text into a safe, readable HTML preview."""
    safe = html.escape(sanitize_text(text))
    paragraphs = safe.split("\n\n")

    rendered = []
    for paragraph in paragraphs:
        lines = paragraph.splitlines()
        if not lines:
            continue

        first = lines[0].strip()
        if (
            len(first) < 100
            and (
                first.isupper()
                or re.match(r"^\d+[\.\)]\s+", first)
            )
        ):
            rendered.append(f"<h3>{first}</h3>")
            if len(lines) > 1:
                rendered.append(
                    "<p>" + "<br>".join(lines[1:]) + "</p>"
                )
        else:
            rendered.append(
                "<p>" + "<br>".join(lines) + "</p>"
            )

    return "\n".join(rendered)
