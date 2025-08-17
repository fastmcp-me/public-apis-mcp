import argparse
import json
import re
import sys
import uuid
from typing import Dict, List, Tuple

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def slugify_header(s: str) -> str:
    s = s.replace("`", "").replace("&", " and ")
    s = re.sub(r"\s+", " ", s.strip()).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "col"


def strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def extract_first_link(cell: str) -> Tuple[str, str]:
    """
    Returns (display_text_without_md, href_or_None) for the first markdown link in the cell.
    Replaces *all* links in the display text with their visible text.
    """
    m = LINK_RE.search(cell)
    href = m.group(2).strip() if m else None

    def repl(mo: re.Match) -> str:
        return mo.group(1)

    text = LINK_RE.sub(repl, cell)
    text = strip_html(text).replace("`", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text, href


def is_alignment_row(line: str) -> bool:
    """
    Detects the markdown table alignment row, e.g.:
    |:---|:---:|---:|
    """
    line = line.strip()
    if "|" not in line:
        return False
    core = line.strip("|").strip()
    parts = [p.strip() for p in core.split("|")]
    if len(parts) < 2:
        return False
    return all(re.fullmatch(r":?-{3,}:?", p) for p in parts)


def split_md_row(line: str, expected: int = None) -> List[str]:
    line = re.sub(r"<!--.*?-->", "", line)  # remove HTML comments
    s = line.strip().strip("|")
    parts = [p.strip() for p in s.split("|")]
    if expected is not None:
        if len(parts) < expected:
            parts += [""] * (expected - len(parts))
        elif len(parts) > expected:
            # join extras into the last cell to keep column count stable
            parts = parts[: expected - 1] + [" | ".join(parts[expected - 1 :])]
    return parts


def parse_markdown_tables(md_text: str) -> List[Dict]:
    lines = md_text.splitlines()
    results: List[Dict] = []
    category = None
    i, n = 0, len(lines)

    while i < n:
        line = lines[i]

        # Track the most recent H2–H6 heading as the category
        mh = re.match(r"^(#{2,6})\s+(.+?)\s*$", line.strip())
        if mh:
            cat_text = mh.group(2)
            cat_text = LINK_RE.sub(lambda m: m.group(1), cat_text)
            cat_text = strip_html(cat_text).strip()
            # Skip APILayer APIs header
            if cat_text != "APILayer APIs":
                category = cat_text
            i += 1
            continue

        # Detect a table by "header line" followed by an alignment row
        if i + 1 < n and is_alignment_row(lines[i + 1]):
            header_cells = [c.strip() for c in split_md_row(line)]
            headers = [slugify_header(h) for h in header_cells]

            i += 2  # move to first data row
            while i < n:
                row = lines[i]
                if not row.strip():
                    break
                if re.match(r"^\s*#{1,6}\s+", row):  # next heading starts
                    break
                if is_alignment_row(row):  # stray alignment row
                    i += 1
                    continue
                if "|" not in row:
                    break

                cells = split_md_row(row, expected=len(headers))
                rec: Dict = {}

                for h, cell in zip(headers, cells):
                    text, href = extract_first_link(cell)
                    rec[h] = text
                    if href:
                        rec[f"{h}_link"] = href

                # Stable unique id derived from category + key fields + full row content
                base = f"{category or ''}|{rec.get('api', '')}|{rec.get('api_link', '')}|{'||'.join(cells)}"
                rec["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, base))
                rec["category"] = category or "Uncategorized"

                results.append(rec)
                i += 1
            continue

        i += 1

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Parse API tables from markdown into JSON."
    )
    parser.add_argument(
        "-i", "--input", help="Markdown file path (defaults to stdin)", required=True
    )
    parser.add_argument(
        "-o", "--output", help="Output JSON file path (defaults to stdout)"
    )
    parser.add_argument(
        "--indent", type=int, default=2, help="JSON indent (default: 2)"
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        md_text = f.read()

    records = parse_markdown_tables(md_text)

    out_json = json.dumps(records, ensure_ascii=False, indent=args.indent)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_json)
    else:
        print(out_json)


if __name__ == "__main__":
    main()
