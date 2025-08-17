from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import List

from fastmcp import FastMCP

from .types import ApiItem


def _datastore_dir() -> Path:
    return Path(str(resources.files("public_apis_mcp"))) / "datastore"


def catalog_path() -> Path:
    return _datastore_dir() / "index.json"


def load_catalog() -> List[ApiItem]:
    with resources.as_file(catalog_path()) as path:
        text = path.read_text(encoding="utf-8")
    raw = json.loads(text)
    return [ApiItem.model_validate(item) for item in raw]


def load_catalog_indexed() -> tuple[list[ApiItem], dict[str, ApiItem]]:
    items = load_catalog()
    index = {i.id: i for i in items}
    return items, index


def register_resources(mcp: FastMCP) -> None:
    @mcp.resource("public-apis://apis")
    def list_apis() -> list[ApiItem]:
        return load_catalog()

    @mcp.resource("public-apis://api/{id}")
    def get_api_resource(id: str) -> ApiItem:
        items, idx = load_catalog_indexed()
        if id not in idx:
            raise ValueError(f"API id not found: {id}")
        return idx[id]
