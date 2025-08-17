from __future__ import annotations

from fastmcp import FastMCP

from .resources import register_resources
from .tools import register_tools


def create_server() -> FastMCP:
    mcp = FastMCP(name="free-api-mcp")
    register_tools(mcp)
    register_resources(mcp)
    return mcp


def run() -> None:
    mcp = create_server()
    mcp.run()  # Run over STDIO
