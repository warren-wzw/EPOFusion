"""Copy referenced assets into docs for GitHub Pages' /docs publishing source.

Edit assets/ as the source of truth, then run this script before committing.
The generated docs/assets files must be committed for branch-based Pages builds.
"""
from html.parser import HTMLParser
from pathlib import Path
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("src", "href") and value:
                path = urlsplit(value).path
                if path.startswith("assets/"):
                    self.paths.add(path)


def main():
    parser = Assets()
    parser.feed((ROOT / "docs/index.html").read_text())
    for relative in sorted(parser.paths):
        source = ROOT / relative
        destination = ROOT / "docs" / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    print(f"Synced {len(parser.paths)} referenced assets into docs/assets")


if __name__ == "__main__":
    main()
