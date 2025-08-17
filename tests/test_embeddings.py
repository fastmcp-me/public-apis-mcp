from __future__ import annotations

import os
from public_apis_mcp.embeddings import build_index, embed_query


def test_build_and_query_index():
    os.environ["FREE_APIS_MCP_TEST_MODE"] = "1"
    idx = build_index()
    qvec, _ = embed_query("pets adoption")
    results = idx.search(qvec, top_k=2)
    assert len(results) >= 1
    assert isinstance(results[0][0], str)
    assert isinstance(results[0][1], float)
