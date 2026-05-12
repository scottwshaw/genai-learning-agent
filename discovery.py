#!/usr/bin/env python3
"""
discovery.py — Pre-retrieval engine for scholarly research discovery.

Queries Semantic Scholar, OpenAlex, and arXiv APIs to find recent papers
relevant to a topic before the main research generation step. Outputs
structured JSON of candidate papers to stdout.

This runs BEFORE run_research.py — its output is fed into the research
prompt as additional context so Claude has scholarly candidates that
web search alone would miss.

Usage:
    python discovery.py --topic safety-assurance-and-governance
    python discovery.py --topic safety-assurance-and-governance --days 60
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TOPICS_FILE = SCRIPT_DIR / "topics.json"


def log(msg: str) -> None:
    print(f"[discovery] {msg}", file=sys.stderr, flush=True)


@dataclass
class Paper:
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str = ""
    abstract: str = ""
    url: str = ""
    citation_count: int | None = None
    source: str = ""
    paper_id: str = ""
    published_date: str = ""

    def key(self) -> str:
        return self.title.lower().strip()[:80]


class RateLimiter:
    def __init__(self, delay: float = 1.1):
        self._delay = delay
        self._last_call: dict[str, float] = {}

    def wait(self, api: str) -> None:
        now = time.time()
        last = self._last_call.get(api, 0)
        elapsed = now - last
        if elapsed < self._delay:
            time.sleep(self._delay - elapsed)
        self._last_call[api] = time.time()


rate_limiter = RateLimiter()


def _fetch_json(url: str, api_name: str, headers: dict | None = None) -> dict | list | None:
    rate_limiter.wait(api_name)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "ResearchAgent/1.0 (scholarly discovery)")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            log(f"{api_name}: rate limited (429), backing off 10s")
            time.sleep(10)
            rate_limiter.wait(api_name)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode())
            except Exception:
                log(f"{api_name}: retry also failed for {url}")
                return None
        log(f"{api_name}: HTTP {e.code} for {url}")
        return None
    except Exception as e:
        log(f"{api_name}: error fetching {url}: {e}")
        return None


def _fetch_xml(url: str, api_name: str) -> ET.Element | None:
    rate_limiter.wait(api_name)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "ResearchAgent/1.0 (scholarly discovery)")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return ET.fromstring(resp.read())
    except Exception as e:
        log(f"{api_name}: error fetching {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# Semantic Scholar
# ---------------------------------------------------------------------------

S2_BASE = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "paperId,title,authors,year,venue,abstract,citationCount,url,publicationDate,externalIds"


def s2_search(query: str, year_from: int | None = None, limit: int = 10) -> list[Paper]:
    params = {"query": query, "limit": limit, "fields": S2_FIELDS}
    if year_from:
        params["year"] = f"{year_from}-"
    url = f"{S2_BASE}/paper/search?{urllib.parse.urlencode(params)}"
    data = _fetch_json(url, "semantic_scholar")
    if not data or "data" not in data:
        return []
    return [_s2_to_paper(p) for p in data["data"] if p]


def s2_paper(paper_id: str) -> Paper | None:
    url = f"{S2_BASE}/paper/{urllib.parse.quote(paper_id, safe='')}?fields={S2_FIELDS}"
    data = _fetch_json(url, "semantic_scholar")
    if not data or "paperId" not in data:
        return None
    return _s2_to_paper(data)


def s2_citations(paper_id: str, limit: int = 20) -> list[Paper]:
    url = (f"{S2_BASE}/paper/{urllib.parse.quote(paper_id, safe='')}/citations"
           f"?fields={S2_FIELDS}&limit={limit}")
    data = _fetch_json(url, "semantic_scholar")
    if not data or "data" not in data:
        return []
    return [_s2_to_paper(c["citingPaper"]) for c in data["data"]
            if c.get("citingPaper", {}).get("title")]


def s2_references(paper_id: str, limit: int = 20) -> list[Paper]:
    url = (f"{S2_BASE}/paper/{urllib.parse.quote(paper_id, safe='')}/references"
           f"?fields={S2_FIELDS}&limit={limit}")
    data = _fetch_json(url, "semantic_scholar")
    if not data or "data" not in data:
        return []
    return [_s2_to_paper(r["citedPaper"]) for r in data["data"]
            if r.get("citedPaper", {}).get("title")]


def s2_author_search(name: str) -> str | None:
    url = f"{S2_BASE}/author/search?query={urllib.parse.quote(name)}&limit=1"
    data = _fetch_json(url, "semantic_scholar")
    if not data or not data.get("data"):
        return None
    return data["data"][0].get("authorId")


def s2_author_papers(author_id: str, year_from: int | None = None,
                     limit: int = 10) -> list[Paper]:
    params = {"fields": S2_FIELDS, "limit": limit}
    if year_from:
        params["year"] = f"{year_from}-"
    url = (f"{S2_BASE}/author/{author_id}/papers"
           f"?{urllib.parse.urlencode(params)}")
    data = _fetch_json(url, "semantic_scholar")
    if not data or "data" not in data:
        return []
    return [_s2_to_paper(p) for p in data["data"] if p.get("title")]


def _s2_best_url(data: dict) -> str:
    ext = data.get("externalIds") or {}
    if ext.get("ArXiv"):
        return f"https://arxiv.org/abs/{ext['ArXiv']}"
    if ext.get("DOI"):
        return f"https://doi.org/{ext['DOI']}"
    return data.get("url", "")


def _s2_to_paper(data: dict) -> Paper:
    authors = [a.get("name", "") for a in data.get("authors", []) if a.get("name")]
    return Paper(
        title=data.get("title", ""),
        authors=authors[:5],
        year=data.get("year"),
        venue=data.get("venue", ""),
        abstract=(data.get("abstract") or "")[:500],
        url=_s2_best_url(data),
        citation_count=data.get("citationCount"),
        source="semantic_scholar",
        paper_id=data.get("paperId", ""),
        published_date=data.get("publicationDate") or "",
    )


# ---------------------------------------------------------------------------
# OpenAlex
# ---------------------------------------------------------------------------

OA_BASE = "https://api.openalex.org"


def oa_search(query: str, from_date: str | None = None,
              limit: int = 10, mailto: str = "") -> list[Paper]:
    params: dict[str, str] = {
        "search": query,
        "per_page": str(limit),
        "sort": "publication_date:desc",
        "select": "id,title,authorships,publication_year,publication_date,"
                  "primary_location,abstract_inverted_index,cited_by_count",
    }
    if from_date:
        params["filter"] = f"from_publication_date:{from_date}"
    if mailto:
        params["mailto"] = mailto
    url = f"{OA_BASE}/works?{urllib.parse.urlencode(params)}"
    data = _fetch_json(url, "openalex")
    if not data or "results" not in data:
        return []
    return [_oa_to_paper(w) for w in data["results"]]


def oa_author_works(author_name: str, from_date: str | None = None,
                    limit: int = 10, mailto: str = "") -> list[Paper]:
    author_params: dict[str, str] = {
        "search": author_name,
        "per_page": "1",
        "select": "id,display_name",
    }
    if mailto:
        author_params["mailto"] = mailto
    author_url = f"{OA_BASE}/authors?{urllib.parse.urlencode(author_params)}"
    author_data = _fetch_json(author_url, "openalex")
    if not author_data or not author_data.get("results"):
        return []

    author_id = author_data["results"][0]["id"]
    oa_id = author_id.split("/")[-1]

    params: dict[str, str] = {
        "filter": f"author.id:{oa_id}",
        "per_page": str(limit),
        "sort": "publication_date:desc",
        "select": "id,title,authorships,publication_year,publication_date,"
                  "primary_location,abstract_inverted_index,cited_by_count",
    }
    if from_date:
        params["filter"] += f",from_publication_date:{from_date}"
    if mailto:
        params["mailto"] = mailto
    url = f"{OA_BASE}/works?{urllib.parse.urlencode(params)}"
    data = _fetch_json(url, "openalex")
    if not data or "results" not in data:
        return []
    return [_oa_to_paper(w) for w in data["results"]]


def _oa_reconstruct_abstract(inverted_index: dict | None) -> str:
    if not inverted_index:
        return ""
    word_positions: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    text = " ".join(w for _, w in word_positions)
    return text[:500]


def _oa_to_paper(data: dict) -> Paper:
    authors = []
    for a in data.get("authorships", [])[:5]:
        name = a.get("author", {}).get("display_name", "")
        if name:
            authors.append(name)

    venue = ""
    loc = data.get("primary_location") or {}
    source = loc.get("source") or {}
    venue = source.get("display_name", "")

    url = ""
    oa_id = data.get("id", "")
    if oa_id:
        url = oa_id

    return Paper(
        title=data.get("title", "") or "",
        authors=authors,
        year=data.get("publication_year"),
        venue=venue,
        abstract=_oa_reconstruct_abstract(data.get("abstract_inverted_index")),
        url=url,
        citation_count=data.get("cited_by_count"),
        source="openalex",
        paper_id=oa_id,
        published_date=data.get("publication_date") or "",
    )


# ---------------------------------------------------------------------------
# arXiv
# ---------------------------------------------------------------------------

ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


def arxiv_search(query: str, categories: list[str] | None = None,
                 max_results: int = 10) -> list[Paper]:
    search_parts = []
    if categories:
        cat_query = "+OR+".join(f"cat:{c}" for c in categories)
        search_parts.append(f"({cat_query})")
    if query:
        terms = urllib.parse.quote(query)
        search_parts.append(f"all:{terms}")

    search_query = "+AND+".join(search_parts)
    url = (f"http://export.arxiv.org/api/query"
           f"?search_query={search_query}"
           f"&sortBy=submittedDate&sortOrder=descending"
           f"&max_results={max_results}")

    root = _fetch_xml(url, "arxiv")
    if root is None:
        return []

    papers = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        title = (entry.findtext("atom:title", "", ARXIV_NS) or "").strip()
        title = " ".join(title.split())
        if not title:
            continue

        authors = []
        for author in entry.findall("atom:author", ARXIV_NS):
            name = author.findtext("atom:name", "", ARXIV_NS)
            if name:
                authors.append(name.strip())

        abstract = (entry.findtext("atom:summary", "", ARXIV_NS) or "").strip()
        abstract = " ".join(abstract.split())[:500]

        link = ""
        for link_el in entry.findall("atom:link", ARXIV_NS):
            if link_el.get("type") == "text/html" or link_el.get("rel") == "alternate":
                link = link_el.get("href", "")
                break

        published = entry.findtext("atom:published", "", ARXIV_NS)[:10]
        year = int(published[:4]) if published else None

        arxiv_id = entry.findtext("atom:id", "", ARXIV_NS)
        if arxiv_id:
            arxiv_id = arxiv_id.split("/abs/")[-1]

        papers.append(Paper(
            title=title,
            authors=authors[:5],
            year=year,
            venue="arXiv",
            abstract=abstract,
            url=link or f"https://arxiv.org/abs/{arxiv_id}",
            source="arxiv",
            paper_id=arxiv_id or "",
            published_date=published,
        ))
    return papers


def arxiv_recent_by_category(categories: list[str],
                             max_results: int = 20) -> list[Paper]:
    return arxiv_search("", categories=categories, max_results=max_results)


# ---------------------------------------------------------------------------
# Seed paper ID resolution
# ---------------------------------------------------------------------------

def _resolve_seed_id(seed: dict) -> str | None:
    """Resolve a seed paper entry by title search on Semantic Scholar."""
    title = seed.get("title", "")
    if not title:
        return None
    results = s2_search(title, limit=1)
    if results:
        return results[0].paper_id
    return None


def build_arxiv_queries(topic: dict) -> list[str]:
    """Build small, high-yield arXiv queries from topic metadata.

    The category-only query is useful for broad recall, but combining broad
    categories with a literal topic label like "Agentic Systems" is too
    narrow and times out too often. Prefer several targeted queries using
    high-signal concept synonyms that already exist in topics.json.
    """
    queries: list[str] = []
    topic_label = (topic.get("label") or "").strip()
    if topic_label:
        queries.append(topic_label)

    for concept in topic.get("concept_synonyms", [])[:6]:
        concept = concept.strip()
        if concept and concept not in queries:
            queries.append(concept)

    return queries


# ---------------------------------------------------------------------------
# Discovery orchestration
# ---------------------------------------------------------------------------

def deduplicate(papers: list[Paper]) -> list[Paper]:
    seen: set[str] = set()
    result = []
    for p in papers:
        k = p.key()
        if k and k not in seen:
            seen.add(k)
            result.append(p)
    return result


def filter_recent(papers: list[Paper], days: int) -> list[Paper]:
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    cutoff_year = date.today().year
    result = []
    for p in papers:
        if p.published_date and p.published_date >= cutoff:
            result.append(p)
        elif not p.published_date and p.year and p.year >= cutoff_year:
            result.append(p)
    return result


def run_discovery(topic: dict, config: dict, days: int | None = None) -> dict:
    recency_days = days or config.get("recency_days", 90)
    max_results = config.get("max_results_per_query", 20)
    mailto = config.get("contact_email", "")
    year_from = date.today().year - 1
    from_date = (date.today() - timedelta(days=recency_days)).isoformat()

    all_papers: list[Paper] = []
    stats = {
        "topic": topic.get("slug", ""),
        "seed_paper_citations": 0,
        "author_papers": 0,
        "concept_searches": 0,
        "arxiv_papers": 0,
        "errors": 0,
    }

    # --- Stream 1: Citation expansion from seed papers ---
    seed_papers = topic.get("seed_papers", [])
    for seed in seed_papers:
        paper_id = seed.get("id", "")
        title = seed.get("title", paper_id)
        if not paper_id and not title:
            continue
        log(f"Seed paper citations: {title or paper_id}")

        citations = s2_citations(paper_id, limit=max_results) if paper_id else []
        if not citations and title:
            resolved_id = _resolve_seed_id(seed)
            if not resolved_id:
                log(f"  Could not resolve paper ID: {paper_id or title}")
                stats["errors"] += 1
                continue
            if resolved_id != paper_id:
                citations = s2_citations(resolved_id, limit=max_results)

        recent_citations = filter_recent(citations, recency_days)
        stats["seed_paper_citations"] += len(recent_citations)
        all_papers.extend(recent_citations)

    # --- Stream 2: Tracked author recent publications ---
    tracked_authors = topic.get("tracked_authors", [])
    for author_info in tracked_authors:
        name = author_info.get("name", "")
        if not name:
            continue
        log(f"Author papers: {name}")
        papers = oa_author_works(name, from_date=from_date,
                                 limit=5, mailto=mailto)
        stats["author_papers"] += len(papers)
        all_papers.extend(papers)

    # --- Stream 3: Concept-expanded searches ---
    concept_synonyms = topic.get("concept_synonyms", [])
    for concept in concept_synonyms[:8]:
        log(f"Concept search: {concept}")
        papers = oa_search(concept, from_date=from_date,
                           limit=5, mailto=mailto)
        stats["concept_searches"] += len(papers)
        all_papers.extend(papers)

    # --- Stream 4: arXiv category monitoring ---
    arxiv_cats = topic.get("arxiv_categories", [])
    if arxiv_cats:
        log(f"arXiv categories: {', '.join(arxiv_cats)}")
        per_category_cap = 3
        for category in arxiv_cats:
            log(f"arXiv category: {category}")
            category_papers = arxiv_recent_by_category([category],
                                                       max_results=per_category_cap)
            recent = filter_recent(category_papers, recency_days)
            stats["arxiv_papers"] += len(recent)
            all_papers.extend(recent)

        for query in build_arxiv_queries(topic):
            log(f"arXiv query: {query}")
            papers = arxiv_search(query, max_results=3)
            recent = filter_recent(papers, recency_days)
            stats["arxiv_papers"] += len(recent)
            all_papers.extend(recent)

    # --- Deduplicate and sort ---
    unique = deduplicate(all_papers)
    unique.sort(key=lambda p: (p.citation_count or 0), reverse=True)

    log(f"Discovery complete: {len(unique)} unique papers "
        f"(citations={stats['seed_paper_citations']}, "
        f"authors={stats['author_papers']}, "
        f"concepts={stats['concept_searches']}, "
        f"arxiv={stats['arxiv_papers']})")

    return {
        "topic": topic.get("slug", ""),
        "topic_label": topic.get("label", ""),
        "discovery_date": date.today().isoformat(),
        "recency_days": recency_days,
        "stats": stats,
        "papers": [asdict(p) for p in unique[:25]],
    }


def format_discovery_context(discovery_result: dict) -> str:
    papers = discovery_result.get("papers", [])
    if not papers:
        return ""

    lines = [
        "## Pre-Retrieved Research Candidates (Scholarly Discovery Engine)",
        "",
        "The following papers were discovered through citation graph expansion,",
        "author tracking, concept-expanded search, and arXiv category monitoring.",
        "These complement — not replace — your web search. Use them to find",
        "developments that web search alone would miss, especially:",
        "- governance methodology papers",
        "- safety engineering frameworks",
        "- workshop proceedings",
        "- institutional reports",
        "- emerging research from tracked authors and citation networks",
        "",
        "Evaluate each candidate on its merits. Not all will be relevant or recent",
        "enough for Key Developments, but they represent the scholarly frontier that",
        "web search systematically under-surfaces.",
        "",
    ]

    for i, paper in enumerate(papers, 1):
        authors = ", ".join(paper.get("authors", [])[:3])
        if len(paper.get("authors", [])) > 3:
            authors += " et al."
        year = paper.get("year", "")
        venue = paper.get("venue", "")
        citations = paper.get("citation_count")
        url = paper.get("url", "")
        abstract = paper.get("abstract", "")

        lines.append(f"### Candidate {i}: {paper.get('title', 'Untitled')}")
        parts = []
        if authors:
            parts.append(f"**Authors:** {authors}")
        if year:
            parts.append(f"**Year:** {year}")
        if venue:
            parts.append(f"**Venue:** {venue}")
        if citations is not None:
            parts.append(f"**Citations:** {citations}")
        if url:
            parts.append(f"**URL:** {url}")
        lines.append(" | ".join(parts))
        if abstract:
            lines.append(f"**Abstract:** {abstract}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Pre-retrieval scholarly discovery engine")
    parser.add_argument("--topic", required=True,
                        help="Topic slug from topics.json")
    parser.add_argument("--topics-file", default=str(TOPICS_FILE),
                        help="Path to topics.json")
    parser.add_argument("--days", type=int, default=None,
                        help="Override recency window (days)")
    parser.add_argument("--format", choices=["json", "context"],
                        default="json",
                        help="Output format: json (raw) or context (markdown)")
    args = parser.parse_args()

    topics_data = json.loads(Path(args.topics_file).read_text())
    config = topics_data.get("discovery", {})
    topics = topics_data.get("topics", [])

    topic = next((t for t in topics if t["slug"] == args.topic), None)
    if not topic:
        slugs = [t["slug"] for t in topics]
        print(f"ERROR: topic '{args.topic}' not found. Available: {slugs}",
              file=sys.stderr)
        sys.exit(1)

    rate_limiter._delay = config.get("request_delay_seconds", 1.1)

    result = run_discovery(topic, config, days=args.days)

    if args.format == "context":
        print(format_discovery_context(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
