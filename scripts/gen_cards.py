#!/usr/bin/env python3
"""Generate profile SVG cards from the GitHub API.

Self-hosted on purpose: github-readme-stats / trophy / activity-graph are all
chronically 503 or DEPLOYMENT_DISABLED, which left the README full of broken
images. Rendering here means the cards are plain files in the repo.
"""
import collections, json, os, sys, urllib.request

USER = os.environ.get("GH_USER", "manaskumar3003")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

# GitHub dark, the colours the site itself uses
BG, PANEL, LINE = "#0d1117", "#161b22", "#30363d"
FG, DIM, FAINT = "#e6edf3", "#7d8590", "#484f58"
BLUE, GREEN, PURPLE, ORANGE, PINK = "#58a6ff", "#3fb950", "#a371f7", "#d29922", "#f778ba"
MONO = "ui-monospace,'SF Mono','JetBrains Mono','Cascadia Code',Menlo,Consolas,monospace"

QUERY = """
{ user(login:"%s") {
    contributionsCollection { totalCommitContributions totalPullRequestContributions
      totalIssueContributions totalPullRequestReviewContributions
      contributionCalendar { totalContributions } }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false) { totalCount
      nodes { stargazerCount languages(first:10, orderBy:{field:SIZE, direction:DESC}) {
        edges { size node { name color } } } } }
    followers { totalCount }
} }""" % USER


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY}).encode(),
        headers={"Authorization": "bearer " + TOKEN, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        sys.exit("GraphQL: " + json.dumps(body["errors"]))
    u = body["data"]["user"]
    c, repos = u["contributionsCollection"], u["repositories"]

    sizes, colors = collections.Counter(), {}
    for repo in repos["nodes"]:
        for e in repo["languages"]["edges"]:
            sizes[e["node"]["name"]] += e["size"]
            colors[e["node"]["name"]] = e["node"]["color"] or DIM
    total = sum(sizes.values()) or 1
    langs = [(n, 100 * s / total, colors[n]) for n, s in sizes.most_common(6)]

    return {
        "contribs": c["contributionCalendar"]["totalContributions"],
        "commits": c["totalCommitContributions"],
        "prs": c["totalPullRequestContributions"],
        "issues": c["totalIssueContributions"],
        "reviews": c["totalPullRequestReviewContributions"],
        "repos": repos["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos["nodes"]),
        "followers": u["followers"]["totalCount"],
        "langs": langs,
    }


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def chrome(w, h, title):
    """Terminal window frame shared by both cards."""
    return f"""<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="11" fill="{BG}" stroke="{LINE}"/>
<path d="M .5 11.5 A 11 11 0 0 1 11.5 .5 H {w-11.5} A 11 11 0 0 1 {w-.5} 11.5 V 40 H .5 Z" fill="{PANEL}"/>
<line x1="0" y1="40" x2="{w}" y2="40" stroke="{LINE}"/>
<circle cx="20" cy="20.5" r="5.5" fill="#ff5f57"/><circle cx="39" cy="20.5" r="5.5" fill="#febc2e"/>
<circle cx="58" cy="20.5" r="5.5" fill="#28c840"/>
<text x="{w/2}" y="25" font-size="12.5" fill="{DIM}" text-anchor="middle">{esc(title)}</text>"""


def hero():
    w, h = 900, 226
    cmd = "whoami --verbose"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{MONO}">
<defs>
<linearGradient id="nm" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{BLUE}"/><stop offset=".55" stop-color="{PURPLE}"/><stop offset="1" stop-color="{PINK}"/>
</linearGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
  <circle cx="1" cy="1" r="1" fill="{FG}" fill-opacity=".05"/></pattern>
<clipPath id="cut"><rect x="0" y="40" width="{w}" height="{h-40}"/></clipPath>
<clipPath id="tw"><rect x="132" y="64" width="0" height="22">
  <animate attributeName="width" values="0;0;175;175;0" keyTimes="0;.08;.5;.92;1" dur="6s" repeatCount="indefinite"/>
</rect></clipPath>
</defs>
{chrome(w, h, f"{USER} — zsh — 92x24")}
<g clip-path="url(#cut)"><rect y="40" width="{w}" height="{h-40}" fill="url(#dots)"/></g>

<text x="28" y="80" font-size="15" fill="{GREEN}">➜</text>
<text x="48" y="80" font-size="15" fill="{BLUE}">~</text>
<text x="66" y="80" font-size="15" fill="{DIM}">$</text>
<g clip-path="url(#tw)"><text x="86" y="80" font-size="15" fill="{FG}">{cmd}</text></g>
<rect x="86" y="66" width="8.5" height="18" fill="{FG}" fill-opacity=".75">
  <animate attributeName="opacity" values="1;1;0;0;1" dur="1.1s" repeatCount="indefinite"/>
  <animate attributeName="x" values="86;86;261;261;86" keyTimes="0;.08;.5;.92;1" dur="6s" repeatCount="indefinite"/>
</rect>

<text x="28" y="134" font-size="40" font-weight="700" fill="url(#nm)" letter-spacing="-.5">Manas Kumar</text>
<text x="30" y="162" font-size="13.5" fill="{DIM}">full-stack engineer · backend · agentic systems</text>
<text x="30" y="188" font-size="13" fill="{FAINT}">TypeScript · Go · Java · C++ · Next.js · Postgres · Docker</text>

<g transform="translate(752 138)">
  <circle r="62" fill="none" stroke="{LINE}"/><circle r="40" fill="none" stroke="{LINE}"/>
  <circle r="5" fill="{PURPLE}"/>
  <g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="16s" repeatCount="indefinite"/>
    <circle cx="62" cy="0" r="3.5" fill="{BLUE}"/></g>
  <g><animateTransform attributeName="transform" type="rotate" from="180" to="540" dur="10s" repeatCount="indefinite"/>
    <circle cx="40" cy="0" r="3" fill="{GREEN}"/></g>
</g>
</svg>"""


def stats(d):
    w, h = 900, 318
    rows = [("contributions", d["contribs"], GREEN), ("repositories", d["repos"], BLUE),
            ("pull requests", d["prs"], PURPLE), ("commits", d["commits"], ORANGE),
            ("code reviews", d["reviews"], BLUE), ("followers", d["followers"], PINK)]

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{MONO}">',
           chrome(w, h, f"{USER} — gh stats")]

    out.append(f'<text x="28" y="72" font-size="13.5" fill="{DIM}">$</text>'
               f'<text x="46" y="72" font-size="13.5" fill="{FG}">gh profile --stats</text>')

    for i, (label, val, col) in enumerate(rows):
        x, y = 34 + (i % 2) * 430, 108 + (i // 2) * 40
        out.append(
            f'<text x="{x}" y="{y}" font-size="13" fill="{DIM}">{label}</text>'
            f'<text x="{x+250}" y="{y}" font-size="17" font-weight="700" fill="{col}" text-anchor="end">{val:,}</text>')

    out.append(f'<line x1="28" y1="222" x2="{w-28}" y2="222" stroke="{LINE}"/>')
    out.append(f'<text x="28" y="250" font-size="13.5" fill="{DIM}">$</text>'
               f'<text x="46" y="250" font-size="13.5" fill="{FG}">gh lang --top</text>')

    # single stacked bar, then a legend row
    bx, bw = 28, w - 56
    out.append(f'<clipPath id="bar"><rect x="{bx}" y="266" width="{bw}" height="12" rx="6"/></clipPath>'
               f'<g clip-path="url(#bar)">')
    cur = bx
    for name, pct, col in d["langs"]:
        seg = bw * pct / 100
        out.append(f'<rect x="{cur:.1f}" y="266" width="{seg+1:.1f}" height="12" fill="{col}"/>')
        cur += seg
    out.append(f'<rect x="{cur:.1f}" y="266" width="{bx+bw-cur:.1f}" height="12" fill="{LINE}"/></g>')

    lx = bx
    for name, pct, col in d["langs"]:
        label = f"{name} {pct:.1f}%"
        out.append(f'<circle cx="{lx+5}" cy="300" r="4.5" fill="{col}"/>'
                   f'<text x="{lx+16}" y="304" font-size="11.5" fill="{DIM}">{esc(label)}</text>')
        lx += 16 + len(label) * 6.95 + 20
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("set GITHUB_TOKEN")
    d = fetch()
    os.makedirs(OUT, exist_ok=True)
    for name, svg in (("hero.svg", hero()), ("stats.svg", stats(d))):
        with open(os.path.join(OUT, name), "w") as f:
            f.write(svg)
        print("wrote", name)
