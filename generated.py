#### Shared helpers for pull_games.py and pull_photos.py

BEGIN = "<!-- BEGIN GENERATED"
END = "<!-- END GENERATED -->"


def generated_section(html):
    """Return the (start, end) positions of the text between the BEGIN GENERATED and END GENERATED comments."""
    start = html.index("-->", html.index(BEGIN)) + len("-->")
    end = html.index(END)
    return start, end


def replace_generated(html, content):
    """Return html with everything between the BEGIN GENERATED and END GENERATED comments replaced by content."""
    start, end = generated_section(html)
    return html[:start] + content + "        " + html[end:]
