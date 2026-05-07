#!/usr/bin/env python3
"""
Audit LaTeX citations and BibTeX entries for the current thesis.

Default mode is local and fast:
  python _audit_refs.py

Online mode verifies entries against Crossref/OpenAlex metadata:
  python _audit_refs.py --online

The online audit is intentionally conservative. "Not found" means
"verify manually", not automatically "fake".
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
BIB_PATH = ROOT / "bibliography.bib"
CACHE_PATH = ROOT / ".ref_audit_cache.json"

CITE_RE = re.compile(
    r"\\(?:cite|citep|citet|citealp|citealt|citeauthor|citeyear|citeyearpar|nocite)"
    r"\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]+)\}"
)


@dataclass
class BibEntry:
    kind: str
    key: str
    fields: dict[str, str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_latex_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        out = []
        escaped = False
        for ch in line:
            if ch == "%" and not escaped:
                break
            out.append(ch)
            escaped = ch == "\\" and not escaped
            if ch != "\\":
                escaped = False
        lines.append("".join(out))
    return "\n".join(lines)


def tex_files() -> list[Path]:
    files = [ROOT / "thesis.tex"]
    files.extend(sorted((ROOT / "chapters").glob("*.tex")))
    return [path for path in files if path.exists()]


def collect_citation_keys() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for path in tex_files():
        text = strip_latex_comments(read_text(path))
        rel = str(path.relative_to(ROOT))
        for match in CITE_RE.finditer(text):
            for raw_key in match.group(1).split(","):
                key = raw_key.strip()
                if key:
                    found.setdefault(key, []).append(rel)
    return found


def find_bib_entries(text: str) -> list[tuple[str, str, str]]:
    entries = []
    i = 0
    n = len(text)
    while i < n:
        at = text.find("@", i)
        if at < 0:
            break
        kind_match = re.match(r"@([A-Za-z]+)\s*\{", text[at:])
        if not kind_match:
            i = at + 1
            continue
        kind = kind_match.group(1)
        start = at + kind_match.end() - 1
        depth = 0
        end = start
        while end < n:
            ch = text[end]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end += 1
                    break
            end += 1
        body = text[start + 1 : end - 1]
        comma = body.find(",")
        if comma >= 0:
            key = body[:comma].strip()
            entries.append((kind, key, body[comma + 1 :]))
        i = end
    return entries


def parse_bib_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    i = 0
    n = len(body)
    while i < n:
        while i < n and (body[i].isspace() or body[i] == ","):
            i += 1
        name_match = re.match(r"([A-Za-z][A-Za-z0-9_-]*)\s*=", body[i:])
        if not name_match:
            break
        name = name_match.group(1).lower()
        i += name_match.end()
        while i < n and body[i].isspace():
            i += 1
        if i >= n:
            break
        if body[i] == "{":
            i += 1
            depth = 1
            start = i
            while i < n and depth > 0:
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                    if depth == 0:
                        value = body[start:i]
                        i += 1
                        break
                i += 1
            else:
                value = body[start:]
        elif body[i] == '"':
            i += 1
            start = i
            escaped = False
            while i < n:
                if body[i] == '"' and not escaped:
                    value = body[start:i]
                    i += 1
                    break
                escaped = body[i] == "\\" and not escaped
                if body[i] != "\\":
                    escaped = False
                i += 1
            else:
                value = body[start:]
        else:
            start = i
            while i < n and body[i] != ",":
                i += 1
            value = body[start:i].strip()
        fields[name] = clean_bib_value(value)
    return fields


def parse_bibliography() -> dict[str, BibEntry]:
    text = read_text(BIB_PATH)
    entries: dict[str, BibEntry] = {}
    for kind, key, body in find_bib_entries(text):
        entries[key] = BibEntry(kind=kind.lower(), key=key, fields=parse_bib_fields(body))
    return entries


def clean_bib_value(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_doi(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip().strip("{}")
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.I)
    value = re.sub(r"^doi:\s*", "", value, flags=re.I)
    return value.strip()


def has_url_like(entry: BibEntry) -> bool:
    for field in ("url", "howpublished", "note"):
        value = entry.fields.get(field, "")
        if re.search(r"https?://", value, flags=re.I):
            return True
    return False


def latex_to_text(value: str) -> str:
    value = re.sub(r"\\url\{([^}]*)\}", r"\1", value)
    value = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", value)
    value = value.replace("{", "").replace("}", "")
    value = value.replace("``", '"').replace("''", '"')
    value = value.replace("--", "-")
    value = re.sub(r"\\[A-Za-z]+", "", value)
    value = value.replace("\\&", "&")
    return re.sub(r"\s+", " ", value).strip()


def comparable(value: str) -> str:
    value = latex_to_text(value).lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def similarity(a: str, b: str) -> float:
    a_tokens = set(comparable(a).split())
    b_tokens = set(comparable(b).split())
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


def author_surnames(author_field: str) -> set[str]:
    text = latex_to_text(author_field)
    parts = re.split(r"\s+\band\b\s+", text)
    surnames: set[str] = set()
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "," in part:
            surname = part.split(",", 1)[0].strip()
        else:
            bits = part.split()
            surname = bits[-1] if bits else ""
        surname = comparable(surname)
        if surname and len(surname) > 2:
            surnames.add(surname)
    return surnames


def author_score(expected: set[str], found: set[str]) -> float:
    if not expected or not found:
        return 0.0
    return len(expected & found) / len(expected)


def load_cache() -> dict[str, object]:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(read_text(CACHE_PATH))
    except Exception:
        return {}


def save_cache(cache: dict[str, object]) -> None:
    CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def http_json(url: str, cache: dict[str, object], delay: float) -> dict[str, object] | None:
    if url in cache:
        return cache[url]  # type: ignore[return-value]
    time.sleep(delay)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "thesis-reference-audit/1.0 (mailto:example@example.com)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        data = {"_error": str(exc)}
    cache[url] = data
    return data


def first(value: object) -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    if value is None:
        return ""
    return str(value)


def crossref_authors(item: dict[str, object]) -> set[str]:
    people = item.get("author", [])
    found = set()
    for person in people if isinstance(people, list) else []:
        if isinstance(person, dict):
            family = comparable(str(person.get("family", "")))
            if family:
                found.add(family)
    return found


def openalex_authors(item: dict[str, object]) -> set[str]:
    authorships = item.get("authorships", [])
    found = set()
    for authorship in authorships if isinstance(authorships, list) else []:
        if not isinstance(authorship, dict):
            continue
        author = authorship.get("author", {})
        if not isinstance(author, dict):
            continue
        display_name = comparable(str(author.get("display_name", "")))
        if display_name:
            bits = display_name.split()
            if bits:
                found.add(bits[-1])
    return found


def entry_year(entry: BibEntry) -> str:
    return re.sub(r"\D", "", entry.fields.get("year", ""))[:4]


def crossref_by_doi(doi: str, cache: dict[str, object], delay: float) -> dict[str, str] | None:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    data = http_json(url, cache, delay)
    if not data or data.get("_error") or data.get("status") != "ok":
        return None
    msg = data.get("message", {})
    if not isinstance(msg, dict):
        return None
    published = msg.get("published-print") or msg.get("published-online") or msg.get("issued") or {}
    year = ""
    if isinstance(published, dict):
        parts = published.get("date-parts")
        if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
            year = str(parts[0][0])
    return {
        "source": "Crossref DOI",
        "title": first(msg.get("title")),
        "year": year,
        "doi": str(msg.get("DOI", "")),
    }


def crossref_search_title(
    title: str, expected_authors: set[str], cache: dict[str, object], delay: float
) -> dict[str, str] | None:
    params = urllib.parse.urlencode({"query.title": latex_to_text(title), "rows": "3"})
    data = http_json("https://api.crossref.org/works?" + params, cache, delay)
    if not data or data.get("_error") or data.get("status") != "ok":
        return None
    msg = data.get("message", {})
    items = msg.get("items", []) if isinstance(msg, dict) else []
    best = None
    best_score = 0.0
    for item in items:
        if not isinstance(item, dict):
            continue
        cand_title = first(item.get("title"))
        score = similarity(title, cand_title)
        if score > best_score:
            issued = item.get("issued", {})
            year = ""
            if isinstance(issued, dict):
                parts = issued.get("date-parts")
                if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
                    year = str(parts[0][0])
            found_authors = crossref_authors(item)
            best_score = score
            best = {
                "source": "Crossref search",
                "title": cand_title,
                "year": year,
                "doi": str(item.get("DOI", "")),
                "score": f"{score:.2f}",
                "author_score": f"{author_score(expected_authors, found_authors):.2f}",
            }
    if not best or best_score < 0.72:
        return None
    if expected_authors and float(best.get("author_score", "0")) == 0.0:
        return None
    return best


def openalex_search_title(
    title: str, expected_authors: set[str], cache: dict[str, object], delay: float
) -> dict[str, str] | None:
    params = urllib.parse.urlencode({"search": latex_to_text(title), "per-page": "3"})
    data = http_json("https://api.openalex.org/works?" + params, cache, delay)
    if not data or data.get("_error"):
        return None
    results = data.get("results", [])
    best = None
    best_score = 0.0
    for item in results if isinstance(results, list) else []:
        if not isinstance(item, dict):
            continue
        cand_title = str(item.get("title", ""))
        score = similarity(title, cand_title)
        if score > best_score:
            found_authors = openalex_authors(item)
            best_score = score
            best = {
                "source": "OpenAlex search",
                "title": cand_title,
                "year": str(item.get("publication_year", "")),
                "doi": str(item.get("doi", "")).replace("https://doi.org/", ""),
                "score": f"{score:.2f}",
                "author_score": f"{author_score(expected_authors, found_authors):.2f}",
            }
    if not best or best_score < 0.72:
        return None
    if expected_authors and float(best.get("author_score", "0")) == 0.0:
        return None
    return best


def verify_entry_online(entry: BibEntry, cache: dict[str, object], delay: float) -> tuple[str, str]:
    title = entry.fields.get("title", "")
    doi = normalize_doi(entry.fields.get("doi"))
    if not doi and entry.kind in {"manual", "misc"} and has_url_like(entry):
        return "OK", "manual/web source with URL; scholarly metadata lookup skipped"
    expected_year = entry_year(entry)
    expected_authors = author_surnames(entry.fields.get("author", ""))
    result = crossref_by_doi(doi, cache, delay) if doi else None
    if result is None and title:
        result = crossref_search_title(title, expected_authors, cache, delay)
    if result is None and title:
        result = openalex_search_title(title, expected_authors, cache, delay)
    if result is None:
        if has_url_like(entry):
            return "URL", "not indexed in Crossref/OpenAlex; URL is present for manual check"
        return "VERIFY", "not found in Crossref/OpenAlex by DOI or title"

    title_score = similarity(title, result.get("title", ""))
    found_year = result.get("year", "")
    notes = [result["source"]]
    if result.get("doi") and not doi:
        notes.append("DOI found: " + result["doi"])
    if title_score < 0.72:
        return "CHECK", f"title mismatch? score={title_score:.2f}; found={result.get('title', '')[:90]}"
    if expected_year and found_year and expected_year != found_year:
        return "CHECK", f"year differs: bib={expected_year}, found={found_year}; {'; '.join(notes)}"
    return "OK", "; ".join(notes)


def print_section(title: str, rows: Iterable[str]) -> None:
    rows = list(rows)
    print(f"\n{title}")
    print("-" * len(title))
    if not rows:
        print("OK")
    else:
        for row in rows:
            print(row)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Audit thesis citations and bibliography entries.")
    parser.add_argument("--online", action="store_true", help="verify references with Crossref/OpenAlex")
    parser.add_argument("--no-cache", action="store_true", help="ignore cached online results")
    parser.add_argument("--delay", type=float, default=0.15, help="delay between online requests")
    args = parser.parse_args(argv)

    citations = collect_citation_keys()
    entries = parse_bibliography()
    cited = set(citations)
    bib_keys = set(entries)

    missing = sorted(cited - bib_keys)
    unused = sorted(bib_keys - cited)

    print(f"Root: {ROOT}")
    print(f"TeX files scanned: {len(tex_files())}")
    print(f"Citation keys used: {len(cited)}")
    print(f"BibTeX entries: {len(entries)}")

    print_section(
        "Missing BibTeX Entries",
        (f"{key}  cited in {', '.join(sorted(set(citations[key])))}" for key in missing),
    )
    print_section("Unused BibTeX Entries", unused)

    incomplete = []
    no_external_id = []
    titles: dict[str, list[str]] = {}
    for key, entry in entries.items():
        fields = entry.fields
        required = ["title", "year"]
        if entry.kind not in {"misc", "manual"}:
            required.append("author")
        missing_fields = [name for name in required if not fields.get(name)]
        if missing_fields:
            incomplete.append(f"{key}: missing {', '.join(missing_fields)}")
        if not normalize_doi(fields.get("doi")) and not has_url_like(entry):
            no_external_id.append(f"{key}: no DOI/URL")
        title_norm = comparable(fields.get("title", ""))
        if title_norm:
            titles.setdefault(title_norm, []).append(key)

    duplicates = [", ".join(keys) for keys in titles.values() if len(keys) > 1]
    print_section("Incomplete Entries", incomplete)
    print_section("Entries Without DOI/URL", no_external_id)
    print_section("Duplicate Titles", duplicates)

    exit_code = 1 if missing or incomplete else 0

    if args.online:
        cache = {} if args.no_cache else load_cache()
        online_rows = []
        for key in sorted(entries):
            status, note = verify_entry_online(entries[key], cache, args.delay)
            online_rows.append(f"{status:6} {key}: {note}")
            if status in {"CHECK", "VERIFY"}:
                exit_code = 1
        save_cache(cache)
        print_section("Online Metadata Check", online_rows)
        print(f"\nCache: {CACHE_PATH}")

    print("\nResult:", "PASS" if exit_code == 0 else "CHECK NEEDED")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
