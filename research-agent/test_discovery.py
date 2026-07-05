"""Tests for discovery.py candidate filtering."""

import xml.etree.ElementTree as ET
from datetime import date

from discovery import (
    CircuitBreaker,
    Paper,
    _arxiv_entry_to_paper,
    _s2_to_paper,
    build_arxiv_category_query,
    filter_recent,
    filter_relevant,
    parse_watch_feed,
    rank_papers,
    redact_url,
    resolve_contact_email,
    s2_headers,
    select_candidates,
    filter_feed_items,
)


def make_paper(title="A Paper", abstract=""):
    return Paper(title=title, abstract=abstract)


class TestFilterRelevant:
    """Keeping papers whose title or abstract mentions a topic term."""

    def test_keeps_paper_matching_single_word_match_term(self):
        """Given a topic with a single-word match_term,
        when a paper's abstract contains that word,
        then the paper is kept."""
        topic = {"concept_synonyms": ["LLM agents"], "match_terms": ["agentic"]}
        paper = make_paper(abstract="an integrative framework for agentic finance")

        result = filter_relevant([paper], topic)

        assert result == [paper]

    def test_matches_plural_form_of_term(self):
        """Given a match_term in singular form,
        when a paper's abstract uses the plural,
        then the paper is kept."""
        topic = {"concept_synonyms": [], "match_terms": ["AI agent"]}
        paper = make_paper(abstract="tool-using AI agents in markets")

        result = filter_relevant([paper], topic)

        assert result == [paper]

    def test_rejects_term_inside_larger_word(self):
        """Given a match_term that is a substring of an unrelated word,
        when a paper only contains the larger word,
        then the paper is dropped."""
        topic = {"concept_synonyms": [], "match_terms": ["agent"]}
        paper = make_paper(abstract="a study of chemical reagents")

        result = filter_relevant([paper], topic)

        assert result == []

    def test_still_matches_existing_concept_synonyms(self):
        """Given a topic with only concept_synonyms and no match_terms,
        when a paper's abstract contains a synonym phrase,
        then the paper is kept as before."""
        topic = {"concept_synonyms": ["LLM agents"]}
        paper = make_paper(abstract="benchmarking LLM agents on web tasks")

        result = filter_relevant([paper], topic)

        assert result == [paper]

    def test_keeps_everything_when_topic_has_no_terms(self):
        """Given a topic with no concept_synonyms and no match_terms,
        when papers are filtered,
        then all papers are kept."""
        topic = {}
        papers = [make_paper(abstract="anything at all")]

        result = filter_relevant(papers, topic)

        assert result == papers


ARXIV_ENTRY_TEMPLATE = """
<entry xmlns="http://www.w3.org/2005/Atom">
  <id>http://arxiv.org/abs/2605.07982v1</id>
  <title>GLiGuard: Schema-Conditioned Classification</title>
  <summary>{abstract}</summary>
  <published>2026-05-11T00:00:00Z</published>
  <author><name>A. Author</name></author>
  <link rel="alternate" type="text/html" href="http://arxiv.org/abs/2605.07982v1"/>
</entry>
"""


class TestAbstractLength:
    """Abstracts keep enough text for relevance matching."""

    def test_s2_abstract_keeps_text_beyond_500_chars(self):
        """Given a Semantic Scholar record with a 900-char abstract,
        when it is converted to a Paper,
        then text past the 500th character is preserved."""
        abstract = "x" * 795 + " jailbreak strategies"
        data = {"title": "A Paper", "abstract": abstract}

        paper = _s2_to_paper(data)

        assert "jailbreak" in paper.abstract

    def test_arxiv_entry_abstract_keeps_text_beyond_500_chars(self):
        """Given an arXiv Atom entry with a 900-char summary,
        when it is parsed to a Paper,
        then text past the 500th character is preserved."""
        abstract = "y" * 795 + " jailbreak strategies"
        entry = ET.fromstring(ARXIV_ENTRY_TEMPLATE.format(abstract=abstract))

        paper = _arxiv_entry_to_paper(entry)

        assert "jailbreak" in paper.abstract


class TestRankPapers:
    """Ranking candidates so new uncited papers are not buried."""

    @staticmethod
    def _pool():
        old = [
            Paper(title=f"Old cited paper {i}", citation_count=50 + i,
                  published_date="2026-06-01")
            for i in range(20)
        ]
        new = [
            Paper(title=f"Brand new paper {i}", citation_count=0,
                  published_date="2026-07-01")
            for i in range(5)
        ]
        return old, new

    def test_new_uncited_papers_fill_recent_slots(self):
        """Given 20 month-old cited papers and 5 brand-new uncited papers,
        when ranked with cap 25 and 15 recent slots,
        then all 5 new papers appear in the result."""
        old, new = self._pool()

        result = rank_papers(old + new, cap=25, recent_slots=15)

        titles = [p.title for p in result]
        assert all(p.title in titles for p in new)

    def test_cited_papers_fill_remaining_slots(self):
        """Given the same pool,
        when ranked,
        then the highest-cited older papers fill the back of the list."""
        old, new = self._pool()

        result = rank_papers(old + new, cap=25, recent_slots=15)

        back = result[15:]
        assert all(p.citation_count >= 50 for p in back)
        assert back[0].citation_count == max(p.citation_count for p in back)

    def test_respects_cap_without_duplicates(self):
        """Given 40 papers,
        when ranked with cap 25,
        then exactly 25 unique papers are returned."""
        papers = [
            Paper(title=f"Paper {i}", citation_count=i,
                  published_date="2026-06-15")
            for i in range(40)
        ]

        result = rank_papers(papers, cap=25, recent_slots=15)

        assert len(result) == 25
        assert len({p.title for p in result}) == 25

    def test_watch_feed_items_always_included(self):
        """Given a pool where uncited watch-feed items are older than
        fifteen newer papers,
        when the pool is ranked,
        then the watch-feed items still appear in the result."""
        newer = [
            Paper(title=f"New paper {i}", citation_count=0,
                  published_date="2026-07-01")
            for i in range(20)
        ]
        cited = [
            Paper(title=f"Cited paper {i}", citation_count=50,
                  published_date="2026-06-01")
            for i in range(10)
        ]
        feed = [
            Paper(title="NIST draft announcement", citation_count=None,
                  published_date="2026-06-20", source="watch_feed"),
        ]

        result = rank_papers(newer + cited + feed, cap=25, recent_slots=15)

        assert feed[0] in result
        assert len(result) == 25


class TestBuildArxivCategoryQuery:
    """Building keyword-filtered arXiv category queries."""

    def test_combines_category_with_or_of_terms(self):
        """Given a topic with match_terms,
        when a category query is built,
        then it ANDs the category with the OR of quoted terms."""
        topic = {"match_terms": ["AI agent", "agentic"]}

        query = build_arxiv_category_query("q-fin.GN", topic)

        assert query == '(cat:q-fin.GN)+AND+(all:%22AI%20agent%22+OR+all:agentic)'

    def test_caps_terms_at_six(self):
        """Given a topic with more than six terms,
        when a category query is built,
        then only the first six are used."""
        topic = {"match_terms": [f"term{i}" for i in range(10)]}

        query = build_arxiv_category_query("cs.AI", topic)

        assert query.count("all:") == 6

    def test_falls_back_to_bare_category_when_no_terms(self):
        """Given a topic with no match_terms or concept_synonyms,
        when a category query is built,
        then it returns just the category filter."""
        query = build_arxiv_category_query("q-fin.GN", {})

        assert query == "cat:q-fin.GN"


RSS_FEED_FIXTURE = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>NIST AI News</title>
    <item>
      <title>NIST Releases Draft Practices for Automated Benchmark Evaluations</title>
      <link>https://www.nist.gov/news-events/news/2026/01/draft-800-2</link>
      <description>Initial public draft open for comment until March.</description>
      <pubDate>Mon, 29 Jun 2026 12:00:00 +0000</pubDate>
    </item>
    <item>
      <title>NIST Expands AI Consortium Scope</title>
      <link>https://www.nist.gov/news-events/news/2026/06/consortium</link>
      <description>Calls for new members.</description>
      <pubDate>Tue, 23 Jun 2026 09:00:00 +0000</pubDate>
    </item>
    <item>
      <title>Malformed item without a date</title>
    </item>
  </channel>
</rss>"""


class TestParseWatchFeed:
    """Parsing watch-feed RSS sources into candidate Papers."""

    def test_parses_rss_items_to_papers(self):
        """Given an RSS 2.0 feed with two dated items,
        when the feed is parsed,
        then two Papers are returned with feed metadata."""
        root = ET.fromstring(RSS_FEED_FIXTURE)

        papers = parse_watch_feed(root, "NIST AI News")

        assert len(papers) == 2
        first = papers[0]
        assert first.title == ("NIST Releases Draft Practices for "
                               "Automated Benchmark Evaluations")
        assert first.source == "watch_feed"
        assert first.venue == "NIST AI News"
        assert first.published_date == "2026-06-29"
        assert first.url == "https://www.nist.gov/news-events/news/2026/01/draft-800-2"
        assert "open for comment" in first.abstract

    def test_skips_items_without_title_or_date(self):
        """Given a feed containing a malformed item,
        when the feed is parsed,
        then the malformed item is dropped without raising."""
        root = ET.fromstring(RSS_FEED_FIXTURE)

        papers = parse_watch_feed(root, "NIST AI News")

        assert all(p.published_date for p in papers)


class TestFilterRelevantWatchFeed:
    """Watch-feed items bypass term matching."""

    def test_keeps_watch_feed_items_without_term_match(self):
        """Given a topic with terms a feed item's title does not mention,
        when papers are filtered,
        then the watch_feed item is kept anyway."""
        topic = {"concept_synonyms": ["guardrail"]}
        feed_item = Paper(
            title="Practices for Automated Benchmark Evaluations",
            source="watch_feed",
        )
        arxiv_item = Paper(title="Unrelated quantum chemistry paper",
                           source="arxiv")

        result = filter_relevant([feed_item, arxiv_item], topic)

        assert result == [feed_item]


class TestFilterRecentFutureDates:
    """Junk metadata with future dates must not enter the pool."""

    def test_drops_papers_dated_in_the_future(self):
        """Given a paper whose published_date is years in the future,
        when papers are filtered for recency,
        then the future-dated paper is dropped."""
        junk = Paper(title="Junk record", published_date="2028-01-01")
        fresh = Paper(title="Fresh paper",
                      published_date=date.today().isoformat())

        result = filter_recent([junk, fresh], days=30)

        assert result == [fresh]


class TestSelectCandidates:
    """Final candidate selection applied to the merged stream pool."""

    def test_drops_future_dated_papers_from_any_stream(self):
        """Given a merged pool containing a future-dated record,
        when candidates are selected,
        then the future-dated record is dropped regardless of stream."""
        junk = Paper(title="Junk agentic record from openalex",
                     abstract="an agentic study", source="openalex",
                     published_date="2028-01-01")
        fresh = Paper(title="Fresh agentic paper", abstract="agentic tools",
                      source="arxiv",
                      published_date=date.today().isoformat())
        topic = {"match_terms": ["agentic"]}

        result = select_candidates([junk, fresh], topic, recency_days=30)

        assert junk not in result
        assert fresh in result


class TestFilterFeedItems:
    """Per-feed term filtering for watch feeds."""

    def test_keeps_items_matching_a_filter_term(self):
        """Given feed filter terms,
        when an item's title mentions one,
        then the item is kept and non-matching items are dropped."""
        draft = Paper(title="NIST Releases Draft Practices for Benchmark "
                            "Evaluations of Language Models",
                      source="watch_feed")
        robots = Paper(title="Test Your Robot Skills in Global Competition",
                       source="watch_feed")

        result = filter_feed_items([draft, robots], ["draft", "benchmark"])

        assert result == [draft]

    def test_keeps_everything_when_no_filter_terms(self):
        """Given a feed with no filter terms configured,
        when items are filtered,
        then all items are kept."""
        items = [Paper(title="Anything", source="watch_feed")]

        result = filter_feed_items(items, [])

        assert result == items


class TestResolveContactEmail:
    """Contact email comes from the environment, not committed config."""

    def test_env_var_overrides_config(self, monkeypatch):
        """Given OPENALEX_MAILTO is set in the environment,
        when the contact email is resolved,
        then the environment value wins over topics.json config."""
        monkeypatch.setenv("OPENALEX_MAILTO", "real@example.org")

        result = resolve_contact_email({"contact_email": "placeholder@x.com"})

        assert result == "real@example.org"

    def test_falls_back_to_config_when_env_unset(self, monkeypatch):
        """Given OPENALEX_MAILTO is not set,
        when the contact email is resolved,
        then the config value is used."""
        monkeypatch.delenv("OPENALEX_MAILTO", raising=False)

        result = resolve_contact_email({"contact_email": "cfg@x.com"})

        assert result == "cfg@x.com"

    def test_empty_when_neither_set(self, monkeypatch):
        """Given no env var and no config value,
        when the contact email is resolved,
        then it is empty (anonymous pool, no fake address sent)."""
        monkeypatch.delenv("OPENALEX_MAILTO", raising=False)

        result = resolve_contact_email({})

        assert result == ""


class TestRedactUrl:
    """Logged URLs must not leak the mailto address."""

    def test_redacts_mailto_param(self):
        """Given a URL containing a mailto query parameter,
        when it is redacted for logging,
        then the address is masked and other params survive."""
        url = "https://api.openalex.org/works?search=x&mailto=me%40example.org&per_page=5"

        result = redact_url(url)

        assert "me%40example.org" not in result
        assert "mailto=***" in result
        assert "per_page=5" in result

    def test_leaves_urls_without_mailto_unchanged(self):
        """Given a URL with no mailto parameter,
        when it is redacted,
        then it is returned unchanged."""
        url = "https://api.semanticscholar.org/graph/v1/paper/search?query=x"

        assert redact_url(url) == url


class TestCircuitBreaker:
    """Skipping an API for the rest of the run once it is clearly blocked."""

    def test_opens_after_threshold_consecutive_failures(self):
        """Given three consecutive rate-limit failures for one API,
        when the breaker is checked,
        then it is open for that API."""
        breaker = CircuitBreaker(threshold=3)

        for _ in range(3):
            breaker.record_failure("openalex")

        assert breaker.is_open("openalex")

    def test_stays_closed_below_threshold(self):
        """Given fewer failures than the threshold,
        when the breaker is checked,
        then it stays closed."""
        breaker = CircuitBreaker(threshold=3)

        breaker.record_failure("openalex")
        breaker.record_failure("openalex")

        assert not breaker.is_open("openalex")

    def test_success_resets_the_count(self):
        """Given failures followed by a success,
        when more failures occur,
        then the count restarts from zero."""
        breaker = CircuitBreaker(threshold=3)

        breaker.record_failure("openalex")
        breaker.record_failure("openalex")
        breaker.record_success("openalex")
        breaker.record_failure("openalex")

        assert not breaker.is_open("openalex")

    def test_apis_are_independent(self):
        """Given one API tripping the breaker,
        when another API is checked,
        then the other API is unaffected."""
        breaker = CircuitBreaker(threshold=3)

        for _ in range(3):
            breaker.record_failure("openalex")

        assert breaker.is_open("openalex")
        assert not breaker.is_open("semantic_scholar")


class TestS2ApiKey:
    """Semantic Scholar API key comes from the environment as a header."""

    def test_header_built_when_env_set(self, monkeypatch):
        """Given SEMANTIC_SCHOLAR_API_KEY is set,
        when the S2 headers are built,
        then the key is sent as x-api-key."""
        monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "test-key-123")

        result = s2_headers()

        assert result == {"x-api-key": "test-key-123"}

    def test_no_header_when_env_unset(self, monkeypatch):
        """Given SEMANTIC_SCHOLAR_API_KEY is not set,
        when the S2 headers are built,
        then no headers are returned (anonymous access unchanged)."""
        monkeypatch.delenv("SEMANTIC_SCHOLAR_API_KEY", raising=False)

        result = s2_headers()

        assert result is None
