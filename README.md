## Public APIs MCP

Catalog of free public APIs with semantic search.

## 🎯 Features

- `search_public_apis`: embedding-based search over API names and descriptions
- `get_public_api_details`: retrieve full details by `id`
- Resources: `public-apis://apis`, `public-apis://api/{id}`

## 🔧 Setup (uv)

Add to MCP clients (e.g., Claude Desktop) using uv.

### Claude Desktop

macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "public-apis": {
      "command": "uvx",
      "args": ["public-apis-mcp"]
    }
  }
}
```

## 🚀 Usage

- Build embeddings index (optional; auto-build on first search):
```bash
uvx public-apis-mcp build-index
```
- Run the MCP server over STDIO:
```bash
uvx public-apis-mcp run
```

## 📋 Tool Reference

### `search_public_apis`
- Purpose: Semantic search over the catalog
- Parameters: `query` (str), `limit` (int, default 5)
- Returns: list of `{ id, name, score, snippet }`

Example call payload:
```json
{ "name": "search_public_apis", "arguments": { "query": "weather", "limit": 5 } }
```

### `get_public_api_details`
- Purpose: Fetch full details by `id`
- Parameters: `id` (str)
- Returns: `ApiItem`

Example call payload:
```json
{ "name": "get_public_api_details", "arguments": { "id": "a6b3a6b3-a6b3-a6b3-a6b3-a6b3a6b3a6b3" } }
```

## 🛠️ Development

Prerequisites:
- Python 3.10+
- uv (`https://docs.astral.sh/uv/`)

Setup:
```bash
uv sync --dev
```

Run tests:
```bash
FREE_APIS_MCP_TEST_MODE=1 uv run pytest -q
```

Lint and format:
```bash
uv run ruff check --fix
uv run ruff format
```

Type checking:
```bash
uv run mypy src/
```

### MCP Client Dev Config

```json
{
  "mcpServers": {
    "public-apis-dev": {
      "command": "uv",
      "args": [
        "--directory",
        "<abs_path>/public-apis-mcp",
        "run",
        "public-apis-mcp"
      ]
    }
  }
}
```

### Build and Try

```bash
uv build
uv run --with dist/*.whl public-apis-mcp --help
```


## 📦 Data & Index

- Data: `src/public_apis_mcp/datastore/free_apis.json`
- Embedding index: `src/public_apis_mcp/datastore/index.npz` (auto-built)

## Testing with MCP Inspector

For exploring and/or developing this server, use the MCP Inspector npm utility:

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run local development server with the inspector
npx @modelcontextprotocol/inspector uv run public-apis-mcp

# Run PyPI production server with the inspector
npx @modelcontextprotocol/inspector uvx public-apis-mcp
```


## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

