from __future__ import annotations

import json
from pathlib import Path

from bs4 import BeautifulSoup, Comment


ROOT = Path(__file__).resolve().parents[1]
SOURCE_HTML = ROOT / "legacy-source.html"
SRC = ROOT / "src"
PUBLIC = ROOT / "public"


def main() -> None:
    soup = BeautifulSoup(SOURCE_HTML.read_text(encoding="utf-8"), "html.parser")
    scripts = []

    for script in list(soup.find_all("script")):
        attributes = {key: " ".join(value) if isinstance(value, list) else str(value) for key, value in script.attrs.items()}
        scripts.append(
            {
                "src": attributes.get("src"),
                "attributes": attributes,
                "content": script.string or script.get_text(),
            }
        )
        script.decompose()

    SRC.mkdir(exist_ok=True)
    body_markup = "".join(str(child) for child in soup.body.contents if not isinstance(child, Comment))
    (SRC / "legacy-body.html").write_text(body_markup, encoding="utf-8", newline="\n")
    (SRC / "legacy-scripts.json").write_text(json.dumps(scripts, indent=2), encoding="utf-8", newline="\n")

    head_markup = "\n".join(str(child) for child in soup.head.contents if getattr(child, "name", None))
    # WordPress tolerates these malformed fragments, while Vite's HTML/CSS parser is strict.
    head_markup = head_markup.replace("</link>", "").replace("</meta>", "").replace("{}", "")
    react_entry = f"""<!doctype html>
<html lang=\"en-US\">
<head>
{head_markup}
<meta name=\"theme-color\" content=\"#ffffff\">
</head>
<body>
  <div id=\"root\"></div>
  <script type=\"module\" src=\"/src/main.jsx\"></script>
</body>
</html>
"""
    (ROOT / "index.html").write_text(react_entry, encoding="utf-8", newline="\n")

    PUBLIC.mkdir(exist_ok=True)
    print(f"Extracted {len(scripts)} legacy scripts into React source")


if __name__ == "__main__":
    main()
