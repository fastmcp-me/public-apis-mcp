#!/usr/bin/env python3
from __future__ import annotations

from public_apis_mcp.embeddings import build_index, save_index


def main() -> None:
    idx = build_index()
    save_index(idx)
    print(
        f"Built index: {len(idx.ids)} items, dim={idx.vectors.shape[1]}, model={idx.model_id}"
    )


if __name__ == "__main__":
    main()
