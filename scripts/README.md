
Fetch and update dataset with new public apis from `publib-apis` git repo:

https://raw.githubusercontent.com/public-apis/public-apis/refs/heads/master/README.md

```bash
python fetch_public_apis.py -i input/public_apis_2025-08.md -o output/public_apis_2025-08.json
# Remove the "call_this_api_link" records from the top (about 10) manually
cp output/public_apis_2025-08.json ../src/free_api_mcp/datastore/index.json
```
