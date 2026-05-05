#!/usr/bin/env python3
"""Project-local branch lock helper for research-agent worktrees."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def branch_slug(branch: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", branch).strip("-")
    return slug or "branch"


def lock_path(root: Path, branch: str) -> Path:
    return root / "docs" / "locks" / f"{branch_slug(branch)}.lock.json"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def acquire(args: argparse.Namespace) -> int:
    path = lock_path(args.root, args.branch)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "branch": args.branch,
        "session_id": args.session,
        "worktree": str(args.root),
        "acquired_at_utc": utc_now(),
        "pid": os.getpid(),
    }
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        holder = read_json(path)
        print(json.dumps({"status": "LOCKED", "path": str(path), "holder": holder}, indent=2))
        return 2
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"status": "ACQUIRED", "path": str(path), "lock": payload}, indent=2))
    return 0


def release(args: argparse.Namespace) -> int:
    path = lock_path(args.root, args.branch)
    if not path.exists():
        print(json.dumps({"status": "ABSENT", "path": str(path)}, indent=2))
        return 1
    holder = read_json(path)
    if holder.get("session_id") != args.session:
        print(json.dumps({"status": "OWNER_MISMATCH", "path": str(path), "holder": holder}, indent=2))
        return 2
    path.unlink()
    print(json.dumps({"status": "RELEASED", "path": str(path)}, indent=2))
    return 0


def force_release(args: argparse.Namespace) -> int:
    path = lock_path(args.root, args.branch)
    if not path.exists():
        print(json.dumps({"status": "ABSENT", "path": str(path)}, indent=2))
        return 0
    holder = read_json(path)
    path.unlink()
    print(
        json.dumps(
            {
                "status": "FORCE_RELEASED",
                "path": str(path),
                "reason": args.reason,
                "previous_holder": holder,
            },
            indent=2,
        )
    )
    return 0


def status(args: argparse.Namespace) -> int:
    path = lock_path(args.root, args.branch)
    if not path.exists():
        print(json.dumps({"status": "UNLOCKED", "path": str(path)}, indent=2))
        return 0
    print(json.dumps({"status": "LOCKED", "path": str(path), "holder": read_json(path)}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root; defaults to the current directory",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, func in (
        ("acquire", acquire),
        ("release", release),
        ("force-release", force_release),
        ("status", status),
    ):
        p = sub.add_parser(name)
        p.add_argument("--branch", required=True)
        if name in {"acquire", "release"}:
            p.add_argument("--session", required=True)
        if name == "force-release":
            p.add_argument("--reason", required=True)
        p.set_defaults(func=func)

    args = parser.parse_args()
    args.root = args.root.resolve()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
