def reciprocal_rank_fusion(
    result_lists: list[list[dict]],
    k: int = 60,
    top_n: int = 5,
) -> list[dict]:
    scores: dict[str, float] = {}
    doc_map: dict[str, dict] = {}

    for result_list in result_lists:
        for rank, doc in enumerate(result_list, start=1):
            doc_id = str(doc["id"])
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            doc_map[doc_id] = doc

    sorted_ids = sorted(scores, key=lambda did: scores[did], reverse=True)
    return [
        {**doc_map[did], "rrf_score": scores[did]}
        for did in sorted_ids[:top_n]
    ]
