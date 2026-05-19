import os
import shutil
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
STATIC_SOURCE = BASE_DIR / "homepage" / "static"
STATIC_TARGET = DOCS_DIR / "static"
BASE_PATH = os.environ.get("GITHUB_PAGES_BASE_PATH", "/Bio-page").rstrip("/")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "david_home.settings")
os.environ.setdefault("DJANGO_STATIC_URL", f"{BASE_PATH}/static/")
os.environ.setdefault("DJANGO_DEBUG", "True")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "testserver,localhost,127.0.0.1")
sys.path.insert(0, str(BASE_DIR))

import django
from django.test import Client


def write_page(client, route, output_path):
    response = client.get(route)
    if response.status_code != 200:
        raise RuntimeError(f"{route} returned HTTP {response.status_code}")
    html = response.content.decode("utf-8")
    html = html.replace('href="/"', f'href="{BASE_PATH}/"')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def main():
    django.setup()

    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)

    shutil.copytree(STATIC_SOURCE, STATIC_TARGET)
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")

    client = Client()
    write_page(client, "/", DOCS_DIR / "index.html")

    print(f"Exported GitHub Pages site to {DOCS_DIR}")


if __name__ == "__main__":
    main()
