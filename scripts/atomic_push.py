#!/usr/bin/env python3
"""Fetch, rebase, and push only when the project-local branch lock matches."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def branch_slug(branch: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", branch).strip("-")
    return slug or "branch"


def run(command: list[str], dry_run: bool) -> None:
    print("+ " + " ".join(command))
    if not dry_run:
        subprocess.run(command, check=True)


def output(command: list[str]) -> str:
    return subprocess.check_output(command, text=True).strip()


def lock_path(root: Path, branch: str) -> Path:
    return root / "docs" / "locks" / f"{branch_slug(branch)}.lock.json"


def verify_lock(root: Path, branch: str, session: str) -> None:
    path = lock_path(root, branch)
    if not path.exists():
        raise SystemExit(f"missing branch lock: {path}")
    holder = json.loads(path.read_text(encoding="utf-8"))
    if holder.get("session_id") != session:
        raise SystemExit(f"branch lock held by different session: {path}")


def remote_branch_exists(remote: str, branch: str) -> bool:
    try:
        subprocess.check_output(
            ["git", "rev-parse", "--verify", f"refs/remotes/{remote}/{branch}"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(output(["git", "rev-parse", "--show-toplevel"])).resolve()
    current = output(["git", "branch", "--show-current"])
    if current != args.branch:
        raise SystemExit(f"current branch is {current!r}, expected {args.branch!r}")

    verify_lock(root, args.branch, args.session)
    run(["git", "fetch", args.remote], args.dry_run)
    if remote_branch_exists(args.remote, args.branch):
        run(["git", "rebase", f"{args.remote}/{args.branch}"], args.dry_run)
    else:
        print(f"remote branch {args.remote}/{args.branch} not found; pushing new branch")
    run(["git", "push", args.remote, args.branch], args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
