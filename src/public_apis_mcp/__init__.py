"""public_apis_mcp package.

MCP server exposing a catalog of public APIs with embedding-based lookups
"""

from .server import create_server, run

__all__ = [
    "create_server",
    "run",
]
