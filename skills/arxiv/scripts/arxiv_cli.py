#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import arxiv


@dataclass
class PaperRow:
    arxiv_id: str
    title: str
    published: str
    updated: str
    authors: List[str]
    summary: str
    pdf_url: Optional[str]
    entry_id: str


def _iso(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        return dt.isoformat()
    return dt.astimezone().isoformat()


def _clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _result_to_row(result: arxiv.Result) -> PaperRow:
    pdf_url = None
    try:
        pdf_url = result.pdf_url
    except Exception:
        pdf_url = None

    return PaperRow(
        arxiv_id=result.get_short_id(),
        title=_clean_whitespace(result.title),
        published=_iso(result.published),
        updated=_iso(result.updated),
        authors=[a.name for a in (result.authors or [])],
        summary=_clean_whitespace(result.summary),
        pdf_url=pdf_url,
        entry_id=result.entry_id,
    )


def cmd_search(args: argparse.Namespace) -> int:
    sort_by_map = {
        "relevance": arxiv.SortCriterion.Relevance,
        "last_updated": arxiv.SortCriterion.LastUpdatedDate,
        "submitted": arxiv.SortCriterion.SubmittedDate,
    }
    sort_order_map = {
        "ascending": arxiv.SortOrder.Ascending,
        "descending": arxiv.SortOrder.Descending,
    }

    search = arxiv.Search(
        query=args.query,
        max_results=args.max_results,
        sort_by=sort_by_map[args.sort_by],
        sort_order=sort_order_map[args.sort_order],
    )

    client = arxiv.Client(
        page_size=min(100, max(1, args.page_size)),
        delay_seconds=max(0.0, args.delay_seconds),
        num_retries=max(0, args.retries),
    )

    rows: List[PaperRow] = []
    for result in client.results(search):
        rows.append(_result_to_row(result))

    if args.json:
        payload = {
            "query": args.query,
            "count": len(rows),
            "results": [asdict(r) for r in rows],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if not rows:
        print("No results.")
        return 0

    for i, r in enumerate(rows, start=1):
        authors = ", ".join(r.authors[:5]) + (" et al." if len(r.authors) > 5 else "")
        print(f"[{i}] {r.arxiv_id} | {r.published[:10]} | {r.title}")
        if authors:
            print(f"    Authors: {authors}")
        if r.pdf_url:
            print(f"    PDF: {r.pdf_url}")
        print(f"    Entry: {r.entry_id}")
    return 0


def cmd_abstract(args: argparse.Namespace) -> int:
    search = arxiv.Search(id_list=[args.id])
    client = arxiv.Client(num_retries=max(0, args.retries))

    results = list(client.results(search))
    if not results:
        print(f"Not found: {args.id}", file=sys.stderr)
        return 2

    row = _result_to_row(results[0])

    if args.json:
        print(json.dumps(asdict(row), ensure_ascii=False, indent=2))
        return 0

    print(f"{row.arxiv_id}")
    print(f"Title: {row.title}")
    if row.authors:
        print(f"Authors: {', '.join(row.authors)}")
    if row.published:
        print(f"Published: {row.published}")
    if row.pdf_url:
        print(f"PDF: {row.pdf_url}")
    print("\nAbstract:\n")
    print(row.summary)
    return 0


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def cmd_download(args: argparse.Namespace) -> int:
    search = arxiv.Search(id_list=[args.id])
    client = arxiv.Client(num_retries=max(0, args.retries))

    results = list(client.results(search))
    if not results:
        print(f"Not found: {args.id}", file=sys.stderr)
        return 2

    result = results[0]
    row = _result_to_row(result)

    if args.outfile and args.outdir is not None:
        print("Use either --outfile or --outdir, not both.", file=sys.stderr)
        return 2

    if args.outfile:
        out_path = args.outfile
        out_dir = os.path.dirname(out_path) or "."
        _ensure_dir(out_dir)
    else:
        out_dir = args.outdir or "."
        _ensure_dir(out_dir)
        out_path = os.path.join(out_dir, f"{row.arxiv_id}.pdf")

    if os.path.exists(out_path) and not args.force:
        print(f"File exists (use --force to overwrite): {out_path}", file=sys.stderr)
        return 3

    written_path = None
    try:
        # Newer arxiv.py versions accept a full path.
        written_path = result.download_pdf(filename=out_path)
    except TypeError:
        try:
            # Other versions accept dirpath + filename (basename).
            written_path = result.download_pdf(dirpath=out_dir, filename=os.path.basename(out_path))
        except TypeError:
            # Last-resort: download into dirpath and rename if needed.
            written_path = result.download_pdf(dirpath=out_dir)

    written_path_str = str(written_path)
    if os.path.abspath(written_path_str) != os.path.abspath(out_path):
        _ensure_dir(os.path.dirname(out_path) or ".")
        os.replace(written_path_str, out_path)
        written_path_str = out_path

    print(written_path_str)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arxiv_cli.py",
        description="arXiv API helper (search / abstract / download) built on arxiv.py",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search papers by keyword/query")
    p_search.add_argument("--query", required=True, help="arXiv query string (e.g. 'all:whisper AND cat:cs.CL')")
    p_search.add_argument("--max-results", type=int, default=10, help="Max number of results (default: 10)")
    p_search.add_argument(
        "--sort-by",
        choices=["relevance", "last_updated", "submitted"],
        default="relevance",
        help="Sort criterion (default: relevance)",
    )
    p_search.add_argument(
        "--sort-order",
        choices=["ascending", "descending"],
        default="descending",
        help="Sort order (default: descending)",
    )
    p_search.add_argument("--page-size", type=int, default=100, help="Client page size (default: 100)")
    p_search.add_argument("--delay-seconds", type=float, default=0.0, help="Delay between requests (default: 0)")
    p_search.add_argument("--retries", type=int, default=3, help="Retry count (default: 3)")
    p_search.add_argument("--json", action="store_true", help="Output JSON")
    p_search.set_defaults(func=cmd_search)

    p_abs = sub.add_parser("abstract", help="Get paper abstract by arXiv ID")
    p_abs.add_argument("--id", required=True, help="arXiv ID (e.g. 2401.01234 or 2401.01234v2)")
    p_abs.add_argument("--retries", type=int, default=3, help="Retry count (default: 3)")
    p_abs.add_argument("--json", action="store_true", help="Output JSON")
    p_abs.set_defaults(func=cmd_abstract)

    p_dl = sub.add_parser("download", help="Download paper PDF by arXiv ID")
    p_dl.add_argument("--id", required=True, help="arXiv ID (e.g. 2401.01234)")
    p_dl.add_argument("--outdir", default=None, help="Output directory (default: current dir)")
    p_dl.add_argument("--outfile", default=None, help="Output file path (overrides --outdir)")
    p_dl.add_argument("--force", action="store_true", help="Overwrite existing file")
    p_dl.add_argument("--retries", type=int, default=3, help="Retry count (default: 3)")
    p_dl.set_defaults(func=cmd_download)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
