#!/usr/bin/env python3
"""Fetch and sync the shared research-agent metaprompt kernel into this project."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REMOTE = "git@github.com:t0m0h1r0/research-agent.git"
DEFAULT_UPSTREAM_DIR = Path("/private/tmp/research-agent-upstream")
DEFAULT_GROUPS = "kernel"
PROJECT_PROFILE = Path("prompts/meta/kernel-project.md")


def run(command: list[str]) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, check=True)


def output(command: list[str]) -> str:
    return subprocess.check_output(command, text=True).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_upstream(
    upstream_dir: Path,
    remote: str,
    revision: str | None,
    fetch: bool,
) -> str:
    if upstream_dir.exists():
        if not (upstream_dir / ".git").exists():
            raise SystemExit(f"upstream path exists but is not a git clone: {upstream_dir}")
        if fetch:
            run(["git", "-C", str(upstream_dir), "fetch", "--prune", "origin"])
    else:
        run(["git", "clone", remote, str(upstream_dir)])

    if revision:
        run(["git", "-C", str(upstream_dir), "checkout", revision])
    else:
        run(["git", "-C", str(upstream_dir), "checkout", "main"])
        if fetch:
            run(["git", "-C", str(upstream_dir), "pull", "--ff-only", "origin", "main"])

    return output(["git", "-C", str(upstream_dir), "rev-parse", "--short", "HEAD"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sync shared research-agent metaprompt assets while preserving "
            "prompts/meta/kernel-project.md. Generated skills, templates, scripts, "
            "and agent prompts are project-local derived outputs."
        )
    )
    parser.add_argument("--target", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument("--upstream-dir", type=Path, default=DEFAULT_UPSTREAM_DIR)
    parser.add_argument("--revision", help="Optional upstream commit, tag, or branch to checkout")
    parser.add_argument("--groups", default=DEFAULT_GROUPS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-fetch", action="store_true", help="Use the existing upstream clone as-is")
    args = parser.parse_args()

    target = args.target.resolve()
    project_profile = target / PROJECT_PROFILE
    if not project_profile.exists():
        raise SystemExit(f"missing project profile: {project_profile}")

    before_hash = sha256(project_profile)
    revision = ensure_upstream(
        args.upstream_dir.resolve(),
        args.remote,
        args.revision,
        fetch=not args.no_fetch,
    )

    sync_script = args.upstream_dir.resolve() / "scripts" / "sync_to_project.py"
    if not sync_script.exists():
        raise SystemExit(f"missing upstream sync script: {sync_script}")

    command = [
        sys.executable,
        str(sync_script),
        "--target",
        str(target),
        "--groups",
        args.groups,
    ]
    if args.dry_run:
        command.append("--dry-run")
    run(command)

    after_hash = sha256(project_profile)
    if before_hash != after_hash:
        raise SystemExit(
            "sync modified prompts/meta/kernel-project.md; restore it before continuing"
        )

    mode = "DRY-RUN" if args.dry_run else "SYNCED"
    print(
        f"{mode} research-agent revision {revision}; "
        f"{PROJECT_PROFILE} preserved ({after_hash})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
