from src.retrieval.fusion import reciprocal_rank_fusion


def test_rrf_basic_merge():
    list_a = [
        {"id": "1", "source": "a.md", "content": "a", "score": 0.9},
        {"id": "2", "source": "b.md", "content": "b", "score": 0.8},
        {"id": "3", "source": "c.md", "content": "c", "score": 0.7},
    ]
    list_b = [
        {"id": "2", "source": "b.md", "content": "b", "score": 0.95},
        {"id": "1", "source": "a.md", "content": "a", "score": 0.85},
        {"id": "4", "source": "d.md", "content": "d", "score": 0.75},
    ]

    results = reciprocal_rank_fusion([list_a, list_b], k=60, top_n=3)

    assert len(results) == 3
    ids = [str(r["id"]) for r in results]
    # docs 1 and 2 appear in both lists, should rank highest
    assert "1" in ids[:2]
    assert "2" in ids[:2]
    assert all("rrf_score" in r for r in results)


def test_rrf_scores_decrease():
    list_a = [
        {"id": str(i), "source": f"{i}.md", "content": "", "score": 1.0 - i * 0.1}
        for i in range(5)
    ]
    results = reciprocal_rank_fusion([list_a], k=60, top_n=5)
    scores = [r["rrf_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_rrf_doc_in_both_lists_ranks_higher():
    list_a = [
        {"id": "1", "source": "a.md", "content": "a", "score": 0.5},
        {"id": "2", "source": "b.md", "content": "b", "score": 0.9},
    ]
    list_b = [
        {"id": "1", "source": "a.md", "content": "a", "score": 0.5},
        {"id": "3", "source": "c.md", "content": "c", "score": 0.95},
    ]
    results = reciprocal_rank_fusion([list_a, list_b], k=60, top_n=3)
    # doc 1 appears in both lists, so should rank first despite lower individual scores
    assert str(results[0]["id"]) == "1"


def test_rrf_empty_lists():
    results = reciprocal_rank_fusion([[], []], k=60, top_n=5)
    assert results == []


def test_rrf_top_n_limits():
    docs = [{"id": str(i), "source": f"{i}.md", "content": "", "score": 0.5} for i in range(10)]
    results = reciprocal_rank_fusion([docs], k=60, top_n=3)
    assert len(results) == 3
