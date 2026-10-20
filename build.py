#!/usr/bin/env python3
"""Genera le pagine del sito AFIPS da src/*.html.

Ogni file in src/ inizia con un blocco di intestazione:
  <!--
  title: Titolo della pagina
  description: Descrizione per Google e anteprime social
  nav: chiave del menu da evidenziare (opzionale)
  -->
seguito dal contenuto della pagina (solo il <main>).
Uso:  python3 build.py
"""
import re, pathlib, html, json, datetime

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
SITE_URL = "https://www.afips.it"
EMAIL = "centrocoppiafamiglia@gmail.com"
TEL = "+39 366 531 7960"
TEL_LINK = "+393665317960"

NAV = [
    ("home", "Home", "index.html", None),
    ("chi", "Chi siamo", None, [
        ("Storia e attività", "chi-siamo.html"),
        ("Soci e collaboratori", "soci.html"),
    ]),
    ("clinica", "Attività clinica", None, [
        ("Centro Coppia e Famiglia", "centro-coppia-famiglia.html"),
        ("Sportello d'ascolto per bambini e adolescenti", "centro-coppia-famiglia.html#sportello"),
        ("Consultazione psicologica “A scuola”", "a-scuola.html"),
        ("Supervisione psicologico-clinica", "supervisione.html"),
    ]),
    ("formazione", "Formazione", None, [
        ("Corso biennale di Psicodiagnostica", "corso-psicodiagnostica.html"),
        ("Master “La Consulenza PsicoSociale”", "master-consulenza-psicosociale.html"),
    ]),
    ("scientifica", "Attività scientifica", None, [
        ("Laboratorio di Letture Psicoanalitiche", "laboratorio-letture-psicoanalitiche.html"),
        ("Eventi", "eventi.html"),
    ]),
    ("contatti", "Contatti", "contatti.html", None),
]


def nav_html(active):
    out = []
    for key, label, href, children in NAV:
        if children:
            cur = ' aria-current="true"' if key == active else ""
            items = "".join(f'<li><a href="{h}">{l}</a></li>' for l, h in children)
            out.append(f'<div class="dd"><button type="button" aria-expanded="false"{cur}>{label}</button><ul>{items}</ul></div>')
        else:
            cur = ' aria-current="page"' if key == active else ""
            out.append(f'<a href="{href}"{cur}>{label}</a>')
    out.append('<a class="cta" href="contatti.html#appuntamento">Richiedi un appuntamento</a>')
    return "\n      ".join(out)


TEMPLATE = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_full}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AFIPS">
<meta property="og:locale" content="it_IT">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/assets/img/og-afips.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="assets/img/favicon.png">
<link rel="stylesheet" href="assets/style.css">{extra_head}
</head>
<body>
<a class="skip" href="#contenuto">Vai al contenuto</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="index.html" aria-label="AFIPS – Home"><img src="assets/img/logo-afips-360.png" alt="AFIPS – Associazione per la Formazione e l'Intervento PsicoSociale" width="64" height="71"></a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav class="nav" id="nav" aria-label="Menu principale">
      {nav}
    </nav>
  </div>
</header>
<main id="contenuto">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot">
      <div>
        <strong class="name">AFIPS</strong>
        <p>Associazione per la Formazione e l'Intervento PsicoSociale</p>
        <p>Via L. Maremonti, 41 – I piano, interno 3<br>73100 Lecce</p>
      </div>
      <div>
        <h4>Informazioni e appuntamenti</h4>
        <ul>
          <li><a href="mailto:{email}">{email}</a></li>
          <li><a href="tel:{tel_link}">{tel}</a></li>
          <li><a href="contatti.html#appuntamento">Richiedi un appuntamento</a></li>
        </ul>
      </div>
      <div>
        <h4>Il sito</h4>
        <ul>
          <li><a href="centro-coppia-famiglia.html">Centro Coppia e Famiglia</a></li>
          <li><a href="chi-siamo.html">Chi siamo</a></li>
          <li><a href="eventi.html">Eventi</a></li>
          <li><a href="privacy.html">Privacy e cookie</a></li>
        </ul>
      </div>
    </div>
    <div class="legal">
      <span>© AFIPS – Associazione per la Formazione e l'Intervento PsicoSociale</span>
      <a href="privacy.html">Informativa privacy e cookie</a>
    </div>
  </div>
</footer>
<script src="assets/site.js"></script>
</body>
</html>
"""


# Dati strutturati per Google (solo in home)
ORG_JSONLD = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "AFIPS – Associazione per la Formazione e l'Intervento PsicoSociale",
    "alternateName": "AFIPS",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/assets/img/logo-afips.png",
    "email": EMAIL,
    "telephone": TEL,
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Via L. Maremonti, 41",
        "postalCode": "73100",
        "addressLocality": "Lecce",
        "addressRegion": "LE",
        "addressCountry": "IT",
    },
}


def build():
    pages = sorted(SRC.glob("*.html"))
    sitemap = []
    for p in pages:
        raw = p.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--(.*?)-->\s*", raw, re.S)
        meta = {}
        if m:
            for line in m.group(1).strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = raw[m.end():]
        else:
            body = raw
        title = meta.get("title", "AFIPS")
        title_full = "AFIPS – Associazione per la Formazione e l'Intervento PsicoSociale" if p.stem == "index" else f"{title} – AFIPS"
        url = f"{SITE_URL}/" if p.stem == "index" else f"{SITE_URL}/{p.name}"
        extra = ""
        if meta.get("robots"):
            extra += f'\n<meta name="robots" content="{meta["robots"]}">'
        elif p.stem != "404":
            sitemap.append(url)
        if p.stem == "index":
            extra += '\n<script type="application/ld+json">' + json.dumps(ORG_JSONLD, ensure_ascii=False) + '</script>'
        out = TEMPLATE.format(
            title_full=html.escape(title_full, quote=False),
            og_title=html.escape(title_full),
            desc=html.escape(meta.get("description", ""), quote=True),
            url=url, site=SITE_URL, extra_head=extra,
            nav=nav_html(meta.get("nav", "")),
            body=body.strip(), email=EMAIL, tel=TEL, tel_link=TEL_LINK,
        )
        (ROOT / p.name).write_text(out, encoding="utf-8")
        print("ok", p.name)
    today = datetime.date.today().isoformat()
    urls = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in sitemap)
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    print("ok sitemap.xml, robots.txt")


if __name__ == "__main__":
    build()
