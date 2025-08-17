from __future__ import annotations

from public_apis_mcp.resources import load_catalog, load_catalog_indexed


def test_catalog_loads():
    items = load_catalog()
    assert len(items) >= 1
    assert items[0].api


def test_catalog_indexed():
    items, idx = load_catalog_indexed()
    assert len(items) == len(idx)
    first_id = items[0].id
    assert first_id in idx
