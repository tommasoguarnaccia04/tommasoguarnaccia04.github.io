"""Build the portfolio as portable static HTML."""

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
ASSETS = ROOT / "assets"
NAME = "Tommaso Guarnaccia"
NAV = {
    "": "Home", "about": "About", "education": "Education", "research": "Research",
    "essays": "Essays", "projects": "Projects", "reading": "Reading", "cv": "CV",
    "contact": "Contact",
}
AMERICAN = "projects/american-mind"
SYNVERA = "projects/synvera-flow"
THESIS = "research/psychiatric-medication-access"
COLLECTIONS = {
    "essay": ("essays", "Essays"),
    "research": ("research", "Research"),
    "project": ("projects", "Projects"),
    "reading": ("reading", "Reading"),
    "video": ("essays", "Videos"),
}


def load(path):
    return json.loads((ROOT / "content" / path).read_text(encoding="utf-8"))


PROFILE = load("profile.json")
AM = load("american-mind.json")
WORK = load("work.json")
TH, SY = WORK["thesis"], WORK["synvera"]


def paragraphs(value):
    return "".join(f"<p>{escape(p.strip())}</p>" for p in value.split("\n\n") if p.strip())


def slug(value):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ValueError(f"Use lowercase letters, numbers, and single hyphens in {value!r}.")
    return value


def external(url):
    if urlsplit(url).scheme != "https" or not urlsplit(url).hostname:
        raise ValueError(f"Expected a full HTTPS URL, received {url!r}")
    return escape(url, quote=True)


def load_entries():
    result = []
    for path in sorted((ROOT / "content" / "entries").glob("*.json")):
        entry = load(path.relative_to(ROOT / "content"))
        section, _ = COLLECTIONS[entry["type"]]
        date.fromisoformat(entry["date"])
        entry["url"] = f"{section}/entries/{slug(path.stem)}"
        if entry["type"] == "video":
            external(entry["link"])
        result.append(entry)
    return sorted(result, key=lambda entry: entry["date"], reverse=True)


ENTRIES = load_entries()


def link(href, label, style="text-link", arrow="→"):
    return f'<a class="{style}" href="{href}">{escape(label)} <span aria-hidden="true">{arrow}</span></a>'


def url(prefix, route):
    return f"{prefix}{route}/" if route else (prefix or "./")


def head(title, summary, label=None):
    kicker = f'<p class="kicker">{escape(label)}</p>' if label else ""
    lead = f'<p class="lead">{escape(summary)}</p>' if summary else ""
    return f'<header class="page-head">{kicker}<h1>{escape(title)}</h1>{lead}</header>'


def section(title, body, anchor=None):
    attr = f' id="{anchor}"' if anchor else ""
    return f'<section class="section"{attr}><h2>{escape(title)}</h2>{body}</section>'


def rich(text, prefix):
    completed = subprocess.run(
        ["pandoc", "--from=commonmark-raw_html", "--to=html5",
         "--lua-filter=editorial.lua", "--shift-heading-level-by=1"],
        cwd=ROOT, input=text, text=True, capture_output=True, check=True,
        env={**os.environ, "PORTFOLIO_PREFIX": prefix},
    )
    return completed.stdout


def education():
    return "".join(
        f'<article class="ed-item"><p class="meta">{escape(item["date"])}</p>'
        f'<h3>{escape(item["institution"])}</h3><p>{escape(item["degree"])}</p>'
        f'<p>{escape(" · ".join(filter(None, [item.get("school"), item.get("details")])) )}</p></article>'
        for item in PROFILE["education"]
    )


def cover(path, alt, portrait=False):
    if (ASSETS / path).is_file():
        loading = ' fetchpriority="high"' if portrait else ' loading="lazy"'
        source = escape(quote(path, safe="/"))
        return f'<img src="__ROOT__assets/{source}" alt="{escape(alt)}"{loading} decoding="async">'
    return ""


def project_art():
    return cover("capitol.webp", "Illustration of the United States Capitol dome")


def profile_portrait():
    portrait = (PROFILE.get("portrait") or "").removeprefix("/assets/").lstrip("/")
    if portrait and ".." not in Path(portrait).parts:
        photo = cover(portrait, NAME, portrait=True)
        if photo:
            return f'<figure class="hero-photo">{photo}<figcaption>{NAME}</figcaption></figure>'
    return '<div class="hero-photo" aria-hidden="true"><div class="fallback"><span>TG</span></div></div>'


def home():
    given, family = PROFILE["name"].split(" ", 1)
    photo = profile_portrait()
    art = project_art() or '<div class="fallback" aria-hidden="true">The American Mind</div>'
    return f"""
<section class="hero">
  <div>
    <h1><span>{escape(given)}</span><span>{escape(family)}</span></h1>
    <p class="lead">{escape(PROFILE["intro"])}</p>
    <div class="actions">
      {link("__ROOT__about/", "About me", "button")}
      {link("__ROOT__cv/", "View CV")}
    </div>
  </div>
  {photo}
</section>
<section class="section" aria-labelledby="featured">
  <div class="section-title"><h2 id="featured">Featured work</h2></div>
  <article class="feature">
    <div class="feature-copy">
      <p class="kicker">Independent research · In development</p>
      <h3>{escape(AM["title"])}</h3>
      <p>{escape(AM["summary"])}</p>
      {link(f"__ROOT__{AMERICAN}/", "Explore the project")}
    </div>
    <div class="feature-photo">{art}</div>
  </article>
  <div class="work-grid featured-secondary">
    {work_card(TH, THESIS, "Bocconi thesis · 2026", "Read the overview")}
    {work_card(SY, SYNVERA, "ASU team project · 2026", "View the project")}
  </div>
</section>
<section class="section" aria-labelledby="education">
  <div class="section-title">
    <h2 id="education">Education</h2>{link("__ROOT__education/", "Academic background")}
  </div>
  <div class="ed-grid">{education()}</div>
</section>"""


def work_card(work, route, meta, action):
    return (f'<article class="work-card"><p class="kicker">{escape(meta)}</p>'
            f'<h3>{escape(work["title"])}</h3><p>{escape(work["summary"])}</p>'
            f'{link(f"__ROOT__{route}/", action)}</article>')


def item(title, summary, href, meta=""):
    label = f'<p class="kicker">{escape(meta)}</p>' if meta else ""
    return (f'<li>{label}<h3><a href="{href}">{escape(title)}</a></h3>'
            f'<p>{escape(summary)}</p></li>')


def books():
    return "<ul class='listing'>" + "".join(
        item(book["title"], f'{book["author"]} · {book["year"]}', external(book["url"]))
        for book in AM["reading"]
    ) + "</ul>"


def listing(entries, empty):
    if not entries:
        return f'<p class="lead">{escape(empty)}</p>'
    return '<ul class="listing">' + "".join(
        item(entry["title"], entry["summary"], f'__ROOT__{entry["url"]}/',
             date.fromisoformat(entry["date"]).strftime("%B %d, %Y").replace(" 0", " "))
        for entry in entries
    ) + "</ul>"


def by_type(*types, project=None):
    return [e for e in ENTRIES if e["type"] in types and
            (project is None or e.get("american_mind") is project)]


def american_page():
    art = project_art()
    overview = (f'<figure class="project-image">{art}<figcaption>U.S. Capitol · Editorial illustration</figcaption></figure>'
                if art else "")
    questions = "<ol>" + "".join(f"<li>{escape(q)}</li>" for q in AM["questions"]) + "</ol>"
    return (head(AM["title"], AM["summary"], "Independent research · In development")
            + '<nav class="jump" aria-label="Project sections">'
              '<a href="#questions">Research questions</a><a href="#references">References</a>'
              '<a href="#writing">Writing &amp; research</a><a href="#videos">Videos</a></nav>'
            + section("Overview", overview + f'<div class="prose">{paragraphs(AM["overview"])}</div>')
            + section("Research questions", f'<div class="prose">{questions}</div>', "questions")
            + section("References", books(), "references")
            + section("Writing & research", listing(by_type("essay", "research", "reading", project=True),
                                                       "No essays or research notes have been published in this series yet."), "writing")
            + section("Videos", listing(by_type("video", project=True), "No videos have been published in this series yet."), "videos"))


def article(entry):
    body = rich(entry.get("body") or "", "../" * len(entry["url"].split("/")))
    if entry["type"] == "video":
        body = link(external(entry["link"]), "Watch video") + body
    category = COLLECTIONS[entry["type"]][1]
    label = f'{category} · {date.fromisoformat(entry["date"]).strftime("%B %Y")}'
    return head(entry["title"], entry["summary"], label) + f'<article class="prose">{body}</article>'


def export_page(route, active, title, description, body, base, *, preview=False):
    # Keep internal links relative to support both GitHub user sites and project sites.
    prefix = "../" * len(route.split("/")) if route else ""
    page_url = f"{base}/{route}/" if route else f"{base}/"
    if route == "404":
        prefix = f'{urlsplit(base).path.rstrip("/")}/'
    site_title = NAME if not route else f"{title} | {NAME}"
    navigation = "".join(
        f'<a href="{url(prefix, path)}"'
        + (' aria-current="page"' if active == path else "")
        + f'>{label}</a>' for path, label in NAV.items()
    )
    indexing = ('<meta name="robots" content="noindex, nofollow">'
                if preview or route == "404" else
                f'<link rel="canonical" href="{escape(page_url)}"><meta property="og:url" content="{escape(page_url)}">')
    social_image = ""
    if not preview and route == AMERICAN and (ASSETS / "capitol.webp").is_file():
        social_image = f'<meta property="og:image" content="{escape(base)}/assets/capitol.webp">'
    body = body.replace("__ROOT__", prefix)
    markup = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(site_title)}</title>
<meta name="description" content="{escape(description)}">
<meta property="og:title" content="{escape(site_title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:type" content="{'article' if '/entries/' in route else 'website'}">
<meta property="og:site_name" content="{NAME}">
<meta name="theme-color" content="#f8f6ef">
{indexing}
{social_image}
<link rel="icon" href="{prefix}assets/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <div class="masthead">
      <a class="brand" href="{url(prefix, '')}"><span class="seal" aria-hidden="true">TG</span>{NAME}</a>
      <span class="location">{escape(PROFILE["location"])}</span>
    </div>
    <nav class="nav" aria-label="Main navigation">{navigation}</nav>
  </div>
</header>
<main id="main" class="wrap{' page' if route else ''}" tabindex="-1">{body}</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <p>© {date.today().year} {NAME}</p>
    {link(url(prefix, 'contact'), 'Get in touch')}
  </div>
</footer>
</body>
</html>
"""
    target = OUT / route / "index.html" if route != "404" else OUT / "404.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markup, encoding="utf-8")
    return page_url


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="")
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    if not args.preview:
        external(base)
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ASSETS, OUT / "assets")
    ess = listing(by_type("essay", "video"), "No essays have been published yet.")
    to_am = link(f"__ROOT__{AMERICAN}/", "Explore The American Mind")
    email = PROFILE.get("email", "")
    email_link = (f'<p class="contact-email"><a href="mailto:{quote(email, safe="@")}">{escape(email)}</a></p>'
                  if email else "")
    links = PROFILE.get("links", [])
    contact_links = ("<ul>" + "".join(f'<li><a href="{external(i["url"])}">{escape(i["label"])}</a></li>'
                                       for i in links) + "</ul>") if links else ""
    cv_link = '<a class="button" href="__ROOT__assets/Tommaso_Guarnaccia_CV.pdf" download>Download CV (PDF) <span aria-hidden="true">↓</span></a>'
    pages = {
        "": ("", NAME, "Italian graduate student at Arizona State University. Portfolio of research, writing, and academic projects.", home()),
        "about": ("about", "About", "Academic background, intellectual interests, and professional aims.",
                  head("About", "I’m an Italian graduate student based in Tempe, Arizona.") +
                  f'<div class="prose">{paragraphs(PROFILE["about"])}</div>'),
        "education": ("education", "Education", "Graduate study at Arizona State University and undergraduate study at Bocconi University.",
                      head("Education", "Arizona State University and Bocconi University") +
                      f'<div class="ed-grid">{education()}</div>' +
                      section("Selected coursework at Bocconi", f'<div class="prose">{paragraphs(PROFILE["coursework"])}</div>')),
        "research": ("research", "Research", "Academic research, comparative policy analysis, and independent inquiries.",
                     head("Research", "Academic research and independent projects on institutions and policy.") +
                     '<ul class="listing">' + item(TH["title"], TH["summary"], f"__ROOT__{THESIS}/", "Undergraduate thesis · 2026") +
                     item(AM["title"], AM["summary"], f"__ROOT__{AMERICAN}/", "Independent research · In development") +
                     '</ul>' + (section("Research notes", listing(by_type("research"), "")) if by_type("research") else "")),
        "essays": ("essays", "Essays", "Original writing on philosophy, psychology, politics, economics, and society.",
                   head("Essays", "Original writing on philosophy, psychology, politics, economics, and society.") + ess +
                   (f'<div class="actions">{to_am}</div>' if not by_type("essay", "video") else "")),
        "projects": ("projects", "Projects", "Selected independent and graduate team projects.",
                     head("Projects", "Independent and graduate team projects.") + '<ul class="listing">' +
                     item(AM["title"], AM["summary"], f"__ROOT__{AMERICAN}/", "Independent research · In development") +
                     item(SY["title"], SY["summary"], f"__ROOT__{SYNVERA}/", "Graduate team project · 2026") + '</ul>' +
                     (section("Additional projects", listing(by_type("project"), "")) if by_type("project") else "")),
        "reading": ("reading", "Reading", "Reading lists, book reviews, and intellectual influences.",
                    head("Reading", "Reading lists, book reviews, and intellectual influences.") +
                    section("The American Mind reading list", books() + f'<div class="actions">{to_am}</div>') +
                    (section("Book reviews and reading notes", listing(by_type("reading"), "")) if by_type("reading") else "")),
        "cv": ("cv", "Curriculum vitae", "Academic CV and downloadable PDF.",
               head("Curriculum vitae", NAME) + f'<div class="cv-actions">{cv_link}</div>' +
               section("Education", f'<div class="ed-grid">{education()}</div>') +
               section("Research and projects", '<ul class="listing">' +
                       item(TH["title"], TH["summary"], f"__ROOT__{THESIS}/") +
                       item(SY["title"], SY["summary"], f"__ROOT__{SYNVERA}/") + '</ul>') +
               section("Methods and languages", f'<div class="prose">{paragraphs(PROFILE["methods"])}{paragraphs(PROFILE["languages"])}</div>')),
        "contact": ("contact", "Contact", "Professional contact information for Tommaso Guarnaccia.",
                    head("Contact", "For academic and professional correspondence.") + email_link + contact_links),
        AMERICAN: ("projects", AM["title"], AM["summary"], american_page()),
        THESIS: ("research", TH["title"], TH["summary"],
                 head(TH["title"], TH["summary"], "Undergraduate thesis · Bocconi University · 2026") +
                 f'<div class="prose">{paragraphs(TH["body"])}</div>'),
        SYNVERA: ("projects", SY["title"], SY["summary"],
                  head(SY["title"], SY["summary"], "Graduate team project · Arizona State University · 2026") +
                  f'<div class="prose">{paragraphs(SY["body"])}</div>'),
        "404": (None, "Page not found", "This page may have moved.",
                head("Page not found", "This page may have moved.") + link("__ROOT__", "Return home")),
    }
    for entry in ENTRIES:
        active = COLLECTIONS[entry["type"]][0]
        pages[entry["url"]] = (active, entry["title"], entry["summary"], article(entry))
    locations = []
    for route, page in pages.items():
        location = export_page(route, *page, base, preview=args.preview)
        if route != "404":
            locations.append(location)
    if args.preview:
        (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    else:
        sitemap = "\n".join(f"<url><loc>{escape(loc)}</loc></url>" for loc in locations)
        (OUT / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap}\n</urlset>\n',
            encoding="utf-8",
        )
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(pages)} pages.")


if __name__ == "__main__":
    main()
