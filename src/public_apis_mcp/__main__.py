import argparse
import sys

from .embeddings import build_index_cli
from .server import run


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="free-api-mcp",
        description="MCP server exposing a catalog of public APIs with embedding-based lookups",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Run the MCP server over STDIO")

    build = subparsers.add_parser(
        "build-index", help="Build embeddings index from bundled catalog"
    )
    build.add_argument("--model", default=None, help="Override embedding model id")

    args = parser.parse_args()

    if args.command == "run" or args.command is None:
        run()
        return

    if args.command == "build-index":
        build_index_cli(model_id=args.model)
        return

    parser.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
