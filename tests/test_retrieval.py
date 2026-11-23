from app import retrieval


def _page(document_id, section, page):
    return {
        "page_id": f"{document_id}-p{page:03d}",
        "document_id": document_id,
        "section": section,
        "page": page,
        "content": f"{document_id} {section} {page}",
    }


def test_adjacent_pages_are_deduplicated_and_stay_within_document_and_section():
    pages = [
        *[_page("lec01-main", "章A", page) for page in range(1, 6)],
        _page("lec01-main", "章B", 6),
        *[_page("lec02-main", "章A", page) for page in range(1, 3)],
    ]
    hits = [
        {**pages[1], "distance": 0.1},
        {**pages[3], "distance": 0.2},
        {**pages[1], "distance": 0.3},
        {**pages[6], "distance": 0.4},
    ]

    results = retrieval._include_adjacent_pages(hits, pages)

    assert [page["page_id"] for page in results] == [
        "lec01-main-p002",
        "lec01-main-p004",
        "lec02-main-p001",
        "lec01-main-p001",
        "lec01-main-p003",
        "lec01-main-p005",
        "lec02-main-p002",
    ]
    assert [page["source"] for page in results] == [
        "search_hit",
        "search_hit",
        "search_hit",
        "adjacent_page",
        "adjacent_page",
        "adjacent_page",
        "adjacent_page",
    ]
    assert len({page["page_id"] for page in results}) == len(results)


def test_search_returns_adjacent_pages(monkeypatch):
    hit = {
        "page_id": "lec01-main-p002",
        "document_id": "lec01-main",
        "section": "章A",
        "page": 2,
        "content": "ヒット本文",
        "distance": 0.1,
    }
    pages = [_page("lec01-main", "章A", page) for page in range(1, 4)]

    def search_hits(query):
        assert query == "質問"
        return [hit]

    def load_pages(source):
        assert source == retrieval.RAG_SOURCE
        return pages

    monkeypatch.setattr(retrieval, "search_hits", search_hits)
    monkeypatch.setattr(retrieval, "load_pages", load_pages)

    results = retrieval.search("質問")

    assert [page["page_id"] for page in results] == [
        "lec01-main-p002",
        "lec01-main-p001",
        "lec01-main-p003",
    ]
