"""
Split large .jsonl concept files into parts under 100 MB for GitHub.

Usage:
  python split_large_jsonl.py [concepts_dir]

Default concepts_dir: evs/api/concepts (relative to repo root).
Files larger than MAX_MB are split into parts of at most PART_MB each.
Original file is removed after successful split.
"""

from __future__ import annotations

import sys
from pathlib import Path

# GitHub limit 100 MB; keep parts clearly under (50 MB)
MAX_MB = 80
PART_MB = 50
MAX_BYTES = MAX_MB * 1024 * 1024
PART_BYTES = PART_MB * 1024 * 1024


def split_large_jsonl(concepts_dir: Path) -> None:
    concepts_dir = concepts_dir.resolve()
    if not concepts_dir.is_dir():
        print(f"Not a directory: {concepts_dir}")
        sys.exit(1)

    for path in sorted(concepts_dir.glob("*.jsonl")):
        # Skip already split parts
        if ".part" in path.name and path.name.rsplit(".", 1)[-1] == "jsonl":
            continue
        size = path.stat().st_size
        if size <= MAX_BYTES:
            continue

        print(f"Splitting {path.name} ({size / (1024*1024):.1f} MB)...")
        part_num = 1
        out_path = concepts_dir / f"{path.stem}.part{part_num:03d}.jsonl"
        current_size = 0
        out_file = None

        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if out_file is not None and current_size >= PART_BYTES:
                        out_file.close()
                        out_file = None
                        part_num += 1
                    if out_file is None:
                        out_path = concepts_dir / f"{path.stem}.part{part_num:03d}.jsonl"
                        out_file = out_path.open("w", encoding="utf-8")
                        current_size = 0
                    out_file.write(line)
                    current_size += len(line.encode("utf-8"))
        finally:
            if out_file is not None:
                out_file.close()

        path.unlink()
        print(f"  -> removed original, created {part_num} part(s)")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    if len(sys.argv) >= 2:
        concepts_dir = Path(sys.argv[1])
        if not concepts_dir.is_absolute():
            concepts_dir = repo_root / concepts_dir
    else:
        concepts_dir = repo_root / "evs" / "api" / "concepts"
    split_large_jsonl(concepts_dir)


if __name__ == "__main__":
    main()
