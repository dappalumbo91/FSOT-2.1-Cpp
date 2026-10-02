#!/usr/bin/env python3
"""Citation / identifier check across the FSOT-2.1-Lean hub (docs + JSON reference fields).

Scans, at the hub commit given by AUTHORITY_PIN.json "ledger_b_data_commit":
  * text docs: *.md / *.tex / *.bib / *.txt under docs/, papers/, predictions/, results/ and the repo root
  * every data/*.json: all string values (identifiers anywhere) and the values of citation-like keys
Extracts DOIs, arXiv ids and URLs, resolves each distinct identifier once:
  * DOI   -> doi.org handle API (exists?), then Crossref or DataCite metadata (title, year)
  * arXiv -> export.arxiv.org API (title, first-version year)
  * URL   -> HTTP status (HEAD, then GET), only URLs inside citation-like JSON fields and docs
Writes a TSV of every occurrence (file:line, identifier, status, resolved title/year, context) and a
JSON summary.  Network results are cached in --cache so reruns are cheap.  Read-only on the hub.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOI_RE = re.compile(r'\b(10\.\d{4,9}/[^\s"<>\]\}\\,;|`\']+)', re.I)
ARXIV_RE = re.compile(r'arxiv(?:\.org/(?:abs|pdf)/|[:\s]\s*)((?:\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}))(v\d+)?', re.I)
URL_RE = re.compile(r'https?://[^\s"<>\)\]\}\\`\'|,]+')
CITE_KEYS = re.compile(r'(reference|citation|doi|bibliograph|paper|literature)', re.I)
TEXT_GLOBS = ["docs/**/*", "papers/**/*", "predictions/**/*", "results/**/*.md", "*.md"]
TEXT_EXT = {".md", ".tex", ".bib", ".txt", ".rst"}
UA = "fsot-cpp-citation-check/1.0 (mailto:dappalumbo91@users.noreply.github.com)"


def clean_doi(d: str) -> str:
    d = d.rstrip(".:")
    while d.endswith(")") and d.count("(") < d.count(")"):
        d = d[:-1]
    return d


def http(url: str, method: str = "GET", timeout: float = 20.0):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read() if method == "GET" else b""
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:  # noqa: BLE001
        return f"ERR:{type(e).__name__}", b""


def resolve_doi(doi: str) -> dict:
    st, body = http("https://doi.org/api/handles/" + urllib.parse.quote(doi, safe="/"))
    out = {"kind": "doi", "id": doi, "handle_status": st}
    rc = None
    if body:
        try:
            rc = json.loads(body).get("responseCode")
        except Exception:  # noqa: BLE001
            pass
    out["exists"] = rc == 1
    if not out["exists"]:
        out["status"] = "NOT_FOUND" if (rc == 100 or st == 404) else f"UNKNOWN({st},{rc})"
        return out
    st, body = http("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
    if st == 200 and body:
        m = json.loads(body)["message"]
        out["registry"] = "crossref"
        out["title"] = (m.get("title") or [""])[0]
        dp = (m.get("issued") or {}).get("date-parts") or [[None]]
        out["year"] = dp[0][0]
        out["container"] = (m.get("container-title") or [""])[0]
        out["authors"] = "; ".join(a.get("family", a.get("name", "")) for a in (m.get("author") or [])[:3])
    else:
        st, body = http("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe=""))
        if st == 200 and body:
            a = json.loads(body)["data"]["attributes"]
            out["registry"] = "datacite"
            out["title"] = (a.get("titles") or [{}])[0].get("title", "")
            out["year"] = a.get("publicationYear")
            out["container"] = a.get("publisher", "")
            out["authors"] = "; ".join(c.get("familyName", c.get("name", "")) for c in (a.get("creators") or [])[:3])
        else:
            out["registry"] = "other"
    out["status"] = "OK"
    return out


def resolve_arxiv(ids: list[str], cache: dict) -> None:
    todo = [i for i in ids if "arxiv:" + i not in cache]
    for k in range(0, len(todo), 20):
        batch = todo[k:k + 20]
        url = "http://export.arxiv.org/api/query?max_results=50&id_list=" + ",".join(batch)
        st, body = http(url, timeout=60)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        found = {}
        if st == 200:
            for e in ET.fromstring(body).findall("a:entry", ns):
                eid = (e.findtext("a:id", "", ns) or "").split("/abs/")[-1]
                eid = re.sub(r"v\d+$", "", eid)
                title = " ".join((e.findtext("a:title", "", ns) or "").split())
                if not title or title == "Error":
                    continue
                found[eid] = {"title": title, "year": int((e.findtext("a:published", "", ns) or "0")[:4] or 0),
                              "authors": "; ".join(a.findtext("a:name", "", ns).split()[-1] for a in e.findall("a:author", ns)[:3])}
        for i in batch:
            if st != 200:
                cache["arxiv:" + i] = {"kind": "arxiv", "id": i, "status": f"UNKNOWN({st})"}
            elif i in found:
                cache["arxiv:" + i] = {"kind": "arxiv", "id": i, "status": "OK", **found[i]}
            else:
                cache["arxiv:" + i] = {"kind": "arxiv", "id": i, "status": "NOT_FOUND"}
        time.sleep(3.1)


def resolve_url(u: str) -> dict:
    st, _ = http(u, method="HEAD", timeout=15)
    if st != 200:
        st2, _ = http(u, method="GET", timeout=20)
        st = st2 if st2 == 200 or not isinstance(st, int) else st
    ok = isinstance(st, int) and st < 400
    return {"kind": "url", "id": u, "http": st, "status": "OK" if ok else ("BLOCKED_OR_AUTH" if st in (401, 403, 405, 429) else "HTTP_ERROR")}


def url_category(u: str) -> str:
    if re.search(r"github\.com/dappalumbo91/[^/]+/(tree|blob)/[^/]+/[A-Za-z]:/", u):
        return "self_link_with_local_windows_path"
    if "github.com/dappalumbo91/" in u:
        return "self_link"
    if "{" in u or re.search(r"(^https?://api\.|/api/|/tap/|/sync\b|/rest/|datagetter|/v\d+/?$|\?)", u, re.I):
        return "api_endpoint_or_template"
    return "web_reference"


def scan(hub: Path):
    occ = []  # (file, line, kind, id, context, field)
    files = set()
    for g in TEXT_GLOBS:
        for p in hub.glob(g):
            if p.is_file() and p.suffix.lower() in TEXT_EXT:
                files.add(p)
    for p in sorted(files):
        for ln, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
            ctx = line.strip()[:300]
            for m in DOI_RE.finditer(line):
                occ.append((str(p.relative_to(hub)), ln, "doi", clean_doi(m.group(1)), ctx, "text"))
            for m in ARXIV_RE.finditer(line):
                occ.append((str(p.relative_to(hub)), ln, "arxiv", m.group(1), ctx, "text"))
            for m in URL_RE.finditer(line):
                u = m.group(0).rstrip(".:;")
                if "doi.org/" in u or "arxiv.org/" in u:
                    continue
                occ.append((str(p.relative_to(hub)), ln, "url", u, ctx, "text"))
    ref_fields = {"total": 0, "with_identifier": 0, "distinct": set(), "distinct_with_identifier": set()}
    for p in sorted((hub / "data").glob("*.json")):
        text = p.read_text(errors="replace")
        lines = text.splitlines()
        for ln, line in enumerate(lines, 1):
            km = re.match(r'\s*"([^"]+)"\s*:\s*"(.*)"\s*,?\s*$', line)
            key, val = (km.group(1), km.group(2)) if km else ("", "")
            is_cite = bool(km and CITE_KEYS.search(key) and not key.endswith(("_pct", "_ms", "_s", "_ns")))
            has_id = False
            for m in DOI_RE.finditer(line):
                occ.append((str(p.relative_to(hub)), ln, "doi", clean_doi(m.group(1)), line.strip()[:300], key)); has_id = True
            for m in ARXIV_RE.finditer(line):
                occ.append((str(p.relative_to(hub)), ln, "arxiv", m.group(1), line.strip()[:300], key)); has_id = True
            if is_cite:
                for m in URL_RE.finditer(val):
                    u = m.group(0).rstrip(".:;")
                    if "doi.org/" in u or "arxiv.org/" in u:
                        continue
                    occ.append((str(p.relative_to(hub)), ln, "url", u, line.strip()[:300], key)); has_id = True
                ref_fields["total"] += 1
                ref_fields["distinct"].add(val)
                if has_id:
                    ref_fields["with_identifier"] += 1
                    ref_fields["distinct_with_identifier"].add(val)
    return occ, ref_fields


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hub", required=True)
    ap.add_argument("--out", default=str(ROOT / "audit" / "citations.tsv"))
    ap.add_argument("--summary", default=str(ROOT / "audit" / "citations_summary.json"))
    ap.add_argument("--cache", default=str(ROOT / "audit" / ".citation_cache.json"))
    ap.add_argument("--no-urls", action="store_true")
    a = ap.parse_args()
    hub = Path(a.hub)
    pin = json.loads((ROOT / "AUTHORITY_PIN.json").read_text())
    head = subprocess.run(["git", "-C", str(hub), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != pin["ledger_b_data_commit"]:
        print(f"hub HEAD {head} != ledger_b_data_commit {pin['ledger_b_data_commit']}", file=sys.stderr)
        return 2
    occ, rf = scan(hub)
    cache_p = Path(a.cache)
    cache = json.loads(cache_p.read_text()) if cache_p.exists() else {}
    dois = sorted({o[3] for o in occ if o[2] == "doi"}, key=str.lower)
    for i, d in enumerate(dois):
        if "doi:" + d.lower() not in cache:
            cache["doi:" + d.lower()] = resolve_doi(d)
            time.sleep(0.2)
            if i % 20 == 0:
                cache_p.parent.mkdir(parents=True, exist_ok=True); cache_p.write_text(json.dumps(cache, indent=1))
    resolve_arxiv(sorted({o[3] for o in occ if o[2] == "arxiv"}), cache)
    urls = sorted({o[3] for o in occ if o[2] == "url"})
    if not a.no_urls:
        for u in urls:
            if "url:" + u not in cache:
                cache["url:" + u] = resolve_url(u)
    cache_p.parent.mkdir(parents=True, exist_ok=True)
    cache_p.write_text(json.dumps(cache, indent=1, sort_keys=True))

    def res(kind, i):
        return cache.get(f"{kind}:{i.lower() if kind == 'doi' else i}", {"status": "UNCHECKED"})

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        f.write(f"#hub_commit\t{head}\n#file\tline\tfield\tkind\tidentifier\tstatus\tyear\ttitle\tcontext\n")
        for o in sorted(occ, key=lambda o: (o[2], o[3].lower(), o[0], o[1])):
            r = res(o[2], o[3])
            st = r.get("status")
            if o[2] == "url":
                st = (f"{st}({r.get('http')})" if st != "UNCHECKED" else st) + ":" + url_category(o[3])
            f.write("\t".join(map(str, [o[0], o[1], o[5], o[2], o[3], st, r.get("year", ""),
                                         (r.get("title") or "").replace("\t", " ")[:160], o[4].replace("\t", " ")])) + "\n")
    summ = {"hub_commit": head}
    cats = {}
    for u in sorted({o[3] for o in occ if o[2] == "url"}):
        c = url_category(u)
        st = res("url", u).get("status")
        cats.setdefault(c, {}).setdefault(st, 0)
        cats[c][st] += 1
    summ["url_by_category"] = cats
    for kind in ("doi", "arxiv", "url"):
        ids = sorted({o[3].lower() if kind == "doi" else o[3] for o in occ if o[2] == kind})
        by = {}
        for i in ids:
            by.setdefault(res(kind, i).get("status"), []).append(i)
        summ[kind] = {"occurrences": sum(1 for o in occ if o[2] == kind), "distinct": len(ids),
                      "by_status": {k: len(v) for k, v in by.items()},
                      "not_ok": {k: v for k, v in by.items() if k != "OK"}}
    summ["json_citation_fields"] = {"values": rf["total"], "values_with_identifier": rf["with_identifier"],
                                    "distinct_values": len(rf["distinct"]),
                                    "distinct_with_identifier": len(rf["distinct_with_identifier"])}
    Path(a.summary).write_text(json.dumps(summ, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: (v if k == "hub_commit" or k == "json_citation_fields" else {kk: vv for kk, vv in v.items() if kk != "not_ok"}) for k, v in summ.items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
