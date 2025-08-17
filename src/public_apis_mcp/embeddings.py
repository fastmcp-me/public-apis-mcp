from __future__ import annotations

import json
import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

try:
    from fastembed import TextEmbedding
except Exception:  # pragma: no cover - optional at import time for build systems
    TextEmbedding = None  # type: ignore


from .types import ApiItem

INDEX_FILE = "index.npz"
INDEX_META_VERSION = 1
DEFAULT_FASTEMBED_MODEL = "BAAI/bge-small-en-v1.5"


def _datastore_dir() -> Path:
    return Path(str(resources.files("public_apis_mcp"))) / "datastore"


def index_path() -> Path:
    return _datastore_dir() / INDEX_FILE


def catalog_path() -> Path:
    return _datastore_dir() / "index.json"


def load_catalog_texts() -> Tuple[list[str], list[str]]:
    with resources.as_file(catalog_path()) as path:
        data = json.loads(path.read_text("utf-8"))
    ids: list[str] = []
    texts: list[str] = []
    for row in data:
        item = ApiItem.model_validate(row)
        ids.append(item.id)
        # This defines what we will embed (this string is embedded as a vector)
        texts.append(f"{item.api} — {item.description}")
    return ids, texts


def _normalize_l2(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


@dataclass
class EmbeddingIndex:
    ids: list[str]
    vectors: np.ndarray  # shape (N, D), float32, L2-normalized
    model_id: str
    meta_version: int = INDEX_META_VERSION

    def search(self, query_vector: np.ndarray, top_k: int) -> list[tuple[str, float]]:
        # query_vector expected shape (D,), normalized
        scores = self.vectors @ query_vector.astype(np.float32)
        idx = np.argsort(-scores)[:top_k]
        return [(self.ids[i], float(scores[i])) for i in idx]


def _hash_string_to_vector(text: str, dim: int = 128) -> np.ndarray:
    # Very lightweight, deterministic embedding for tests; not semantic.
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    vec = rng.normal(0, 1, size=(dim,)).astype(np.float32)
    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec /= norm
    return vec


def _embed_texts_hash(texts: list[str]) -> np.ndarray:
    return np.stack([_hash_string_to_vector(t) for t in texts], axis=0)


def _embed_texts_fastembed(texts: list[str], model_id: Optional[str]) -> np.ndarray:
    if TextEmbedding is None:
        raise RuntimeError(
            "fastembed is not installed; please install the base package requirements"
        )
    model_name = model_id or DEFAULT_FASTEMBED_MODEL
    encoder = TextEmbedding(model_name)
    # fastembed returns generator of lists
    vectors = list(encoder.embed(texts))
    return np.array(vectors, dtype=np.float32)


def embed_texts(
    texts: list[str], model_id: Optional[str] = None
) -> tuple[np.ndarray, str]:
    # Test/deterministic lightweight path
    backend = os.getenv("FREE_APIS_MCP_EMBED_BACKEND")
    if os.getenv("FREE_APIS_MCP_TEST_MODE") == "1" or (
        backend and backend.lower() == "hash"
    ):
        vecs = _embed_texts_hash(texts)
        return vecs, "hash/test"

    # Use fastembed for all embeddings
    vecs = _embed_texts_fastembed(texts, model_id)
    return vecs, (model_id or DEFAULT_FASTEMBED_MODEL)


def build_index(model_id: Optional[str] = None) -> EmbeddingIndex:
    ids, texts = load_catalog_texts()
    vectors, resolved_model = embed_texts(texts, model_id=model_id)
    vectors = _normalize_l2(vectors.astype(np.float32))
    return EmbeddingIndex(ids=ids, vectors=vectors, model_id=resolved_model)


def save_index(index: EmbeddingIndex) -> Path:
    p = index_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        p,
        vectors=index.vectors,
        ids=np.array(index.ids),
        model_id=index.model_id,
        meta_version=index.meta_version,
    )
    return p


def load_index() -> Optional[EmbeddingIndex]:
    p = index_path()
    if not p.exists():
        return None
    data = np.load(p, allow_pickle=True)
    vectors = data["vectors"].astype(np.float32)
    ids = data["ids"].tolist()
    model_id = str(data["model_id"]) if "model_id" in data else DEFAULT_FASTEMBED_MODEL
    meta_version = int(data["meta_version"]) if "meta_version" in data else 0
    if meta_version != INDEX_META_VERSION:
        return None
    vectors = _normalize_l2(vectors)
    return EmbeddingIndex(
        ids=ids, vectors=vectors, model_id=model_id, meta_version=meta_version
    )


def ensure_index(model_id: Optional[str] = None) -> EmbeddingIndex:
    idx = load_index()
    if idx is not None:
        return idx
    idx = build_index(model_id=model_id)
    save_index(idx)
    return idx


def embed_query(text: str, model_id: Optional[str] = None) -> tuple[np.ndarray, str]:
    vecs, resolved = embed_texts([text], model_id=model_id)
    q = vecs[0].astype(np.float32)
    q = q / (np.linalg.norm(q) + 1e-12)
    return q, resolved


def build_index_cli(model_id: Optional[str] = None) -> None:
    idx = build_index(model_id=model_id)
    save_index(idx)
    print(
        f"Built index: {len(idx.ids)} items, dim={idx.vectors.shape[1]}, model={idx.model_id}"
    )
