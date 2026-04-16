#!/usr/bin/env python3
import argparse
import hashlib
from pathlib import Path


def sha256_file(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_shared_path(cli_path: str | None) -> Path:
    if cli_path:
        return Path(cli_path)

    candidates = [
        Path("/app/shared"),
        Path("/root/dev/shared"),
        Path("shared"),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return Path("shared")


def directory_report(directory: Path):
    files = sorted([p for p in directory.rglob("*") if p.is_file()])
    file_entries = []
    for file_path in files:
        rel_path = file_path.relative_to(directory).as_posix()
        file_hash = sha256_file(file_path)
        file_entries.append((rel_path, file_hash))

    aggregate = hashlib.sha256()
    for rel_path, file_hash in file_entries:
        aggregate.update(f"{rel_path}\t{file_hash}\n".encode("utf-8"))

    return file_entries, aggregate.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute SHA256 checksums for files in each folder under shared."
    )
    parser.add_argument(
        "--shared-path",
        help="Path to the shared directory (defaults to /app/shared, /root/dev/shared, or ./shared).",
    )
    args = parser.parse_args()

    shared_path = resolve_shared_path(args.shared_path)
    if not shared_path.exists() or not shared_path.is_dir():
        print(f"shared path not found: {shared_path}")
        return 1

    subdirs = sorted([p for p in shared_path.iterdir() if p.is_dir()])
    if not subdirs:
        print(f"no folders found under {shared_path}")
        return 0

    for folder in subdirs:
        print(f"Folder: {folder.name}")
        file_entries, total_hash = directory_report(folder)
        if not file_entries:
            print("  (no files)")
        else:
            for rel_path, file_hash in file_entries:
                print(f"  {rel_path}: {file_hash}")
        print(f"  Aggregate checksum: {total_hash}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
