#!/usr/bin/env python3
"""Generate static brand landing pages with brand-specific Open Graph data.

The storefront is a single index.html, but link previews need real HTML with
per-brand meta tags. Each generated <brand>/index.html is a copy of the
storefront with brand metadata and <base href="/"> so every relative asset
still loads from the site root.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://goel-store.github.io"

BRANDS = {
    "godderob": {
        "name": "Godderob",
        "title": "Godderob — христианская одежда",
        "description": "Godderob — белорусский бренд христианской одежды: футболки, свитшоты, худи и аксессуары. Заказать на платформе GO’EL.",
        "image": "img/godderob/shepherd-emerald-01.jpg",
    },
    "sote": {
        "name": "Sote_m",
        "title": "Sote_m — одежда с христианскими принтами",
        "description": "Sote_m — белорусский бренд одежды с христианскими принтами: футболки, худи, лонгсливы. Заказать на платформе GO’EL.",
        "image": "img/sote/jesus-01.jpg",
    },
    "art": {
        "name": "Jesus Saves",
        "title": "Jesus Saves — христианская одежда",
        "description": "Jesus Saves — российский бренд христианской одежды: футболки и свитшоты с христианскими принтами. Заказать на платформе GO’EL.",
        "image": "img/art/women-strength-black-white-03.jpg",
    },
    "amenshop": {
        "name": "AMENSHOP",
        "title": "AMENSHOP — христианская одежда",
        "description": "AMENSHOP — российский бренд христианской одежды: свитшоты и футболки с христианскими принтами. Заказать на платформе GO’EL.",
        "image": "img/amenshop/proverbs-sweatshirt-beige-01.jpg",
    },
}

DROP_PATTERNS = [
    r'\n\s*<meta name="description"[^>]*>',
    r'\n\s*<link rel="canonical"[^>]*>',
    r'\n\s*<meta property="og:[^"]+"[^>]*>',
    r'\n\s*<meta name="twitter:[^"]+"[^>]*>',
    r'\n\s*<title[^>]*>.*?</title>',
]


def build_page(html: str, slug: str, brand: dict) -> str:
    url = f"{SITE}/{slug}/"
    image = f"{SITE}/{brand['image']}"
    for pattern in DROP_PATTERNS:
        html = re.sub(pattern, "", html, count=0 if "og:" in pattern or "twitter:" in pattern else 1)
    meta = (
        '<base href="/">\n'
        '  <meta name="description" content="{description}">\n'
        '  <link rel="canonical" href="{url}">\n'
        '  <meta property="og:type" content="website">\n'
        '  <meta property="og:site_name" content="GO’EL">\n'
        '  <meta property="og:url" content="{url}">\n'
        '  <meta property="og:title" content="{title}">\n'
        '  <meta property="og:description" content="{description}">\n'
        '  <meta property="og:image" content="{image}">\n'
        '  <meta property="og:locale" content="ru_RU">\n'
        '  <meta name="twitter:card" content="summary_large_image">\n'
        '  <meta name="twitter:title" content="{title}">\n'
        '  <meta name="twitter:description" content="{description}">\n'
        '  <meta name="twitter:image" content="{image}">\n'
        '  <title>{title} | GO’EL</title>\n'
        '  <script>window.__brandSharePage = "{slug}";</script>'
    ).format(**{**brand, 'url': url, 'image': image, 'slug': slug})
    html = html.replace("<head>", "<head>\n  " + meta, 1)
    return html


def main() -> None:
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    for slug, brand in BRANDS.items():
        target_dir = ROOT / slug
        target_dir.mkdir(exist_ok=True)
        (target_dir / "index.html").write_text(build_page(source, slug, brand), encoding="utf-8")
        print(f"wrote {slug}/index.html")


if __name__ == "__main__":
    main()
