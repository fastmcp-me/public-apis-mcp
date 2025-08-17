from __future__ import annotations


from fastmcp import FastMCP

from .embeddings import embed_query, ensure_index
from .resources import load_catalog_indexed
from .types import ApiItem, SearchResult


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool
    def search_public_apis(query: str, limit: int = 5) -> list[SearchResult]:
        """Search for free public APIs that match the input query string."""
        idx = ensure_index()
        qvec, _ = embed_query(query, model_id=idx.model_id)
        top = idx.search(qvec, top_k=max(1, min(50, int(limit))))  # limit to 50
        items, by_id = load_catalog_indexed()
        results: list[SearchResult] = []
        for api_id, score in top:
            item = by_id.get(api_id)
            if not item:
                continue
            results.append(
                SearchResult(
                    id=item.id,
                    name=item.api,
                    score=float(score),
                    snippet=item.description,
                )
            )
        return results

    @mcp.tool
    def get_public_api_details(id: str) -> ApiItem:
        """Get detailed information about a specific API by its
        unique public-apis-mcp server ID
        """
        items, by_id = load_catalog_indexed()
        item = by_id.get(id)
        if not item:
            raise ValueError(f"API id not found: {id}")
        return item
