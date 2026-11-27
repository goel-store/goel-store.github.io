#!/usr/bin/env python3
"""Generate static share pages with brand/product-specific Open Graph data.

The storefront is a single index.html. Link previews, however, need real HTML
with per-page meta tags. This script copies index.html into:
  <brand>/index.html
  <brand>/<product>/index.html
Each copy gets <base href="/"> so relative assets keep loading from the root.
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

ITEM_PATTERN = re.compile(r'name:\s*"([^"]+)"\s*,\s*\n\s*slug:\s*"([^"]+)"')
PHOTO_PATTERN = re.compile(r'photos:\s*\[\s*"([^"]+)"|photo:\s*"([^"]+)"')
PRICE_PATTERN = re.compile(r'price:\s*"([^"]+)"')


def brand_sections(source: str) -> dict[str, str]:
    start = source.index("const brands = {")
    end = source.index("\n};\n\n    Object.keys(brands)", start)
    block = source[start:end]
    starts = [(match.group(1), match.start()) for match in re.finditer(r'\n  ([a-z][a-z0-9_-]*): \{', block)]
    sections = {}
    for index, (slug, position) in enumerate(starts):
        if slug not in BRANDS:
            continue
        next_position = starts[index + 1][1] if index + 1 < len(starts) else len(block)
        sections[slug] = block[position:next_position]
    return sections


def extract_products(source: str, slug: str) -> list[dict]:
    section = brand_sections(source).get(slug, "")
    products = []
    for match in ITEM_PATTERN.finditer(section):
        name, item_slug = match.group(1), match.group(2)
        tail = section[match.end():match.end() + 4000]
        photo = PHOTO_PATTERN.search(tail)
        price = PRICE_PATTERN.search(tail)
        image = (photo.group(1) or photo.group(2)) if photo else ""
        products.append({
            "slug": item_slug,
            "name": name,
            "image": image,
            "price": price.group(1) if price else "",
        })
    return products


def build_page(html: str, page: dict) -> str:
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
        '  <script>window.__brandSharePage = "{flag}";</script>'
    ).format(**page)
    return html.replace("<head>", "<head>\n  " + meta, 1)


def main() -> None:
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    for slug, brand in BRANDS.items():
        target_dir = ROOT / slug
        target_dir.mkdir(exist_ok=True)
        page = {
            "title": brand["title"],
            "description": brand["description"],
            "image": f"{SITE}/{brand['image']}",
            "url": f"{SITE}/{slug}/",
            "flag": slug,
        }
        (target_dir / "index.html").write_text(build_page(source, page), encoding="utf-8")
        products = extract_products(source, slug)
        for product in products:
            if not product["image"]:
                continue
            price = f" Цена: {product['price']}." if product["price"] else ""
            page = {
                "title": f"{product['name']} — {brand['name']}",
                "description": f"{product['name']} от {brand['name']}.{price} Заказать на платформе GO’EL.",
                "image": f"{SITE}/{product['image']}",
                "url": f"{SITE}/{slug}/{product['slug']}/",
                "flag": slug,
            }
            product_dir = target_dir / product["slug"]
            product_dir.mkdir(exist_ok=True)
            (product_dir / "index.html").write_text(build_page(source, page), encoding="utf-8")
        print(f"{slug}: brand page + {len(products)} product pages")


if __name__ == "__main__":
    main()
