#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path


def _ensure_project_root_on_path():
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def main() -> int:
    _ensure_project_root_on_path()
    from util.trigger_process import trigger_process

    parser = argparse.ArgumentParser(description="Run docker flow for a given UUID.")
    parser.add_argument("uuid", type=str, help="UUID for the transformation run")
    args = parser.parse_args()

    thread = trigger_process(args.uuid)
    thread.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
