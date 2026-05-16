#!/usr/bin/env python3
"""Sync the shared research-agent metaprompt kernel from the project submodule."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REMOTE = "git@github.com:t0m0h1r0/research-agent.git"
DEFAULT_SUBMODULE_DIR = Path("prompts/upstream/research-agent")
DEFAULT_GROUPS = "kernel"
PROJECT_PROFILE = Path("prompts/meta/kernel-project.md")
KERNEL_FILES = [
    "kernel-antipatterns.md",
    "kernel-constitution.md",
    "kernel-deploy.md",
    "kernel-domains.md",
    "kernel-ops.md",
    "kernel-roles.md",
    "kernel-workflow.md",
]


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


def ensure_submodule(submodule_dir: Path) -> str:
    if not submodule_dir.exists():
        raise SystemExit(
            f"missing research-agent submodule: {submodule_dir}\n"
            "Run: git submodule update --init --recursive"
        )
    git_dir = submodule_dir / ".git"
    if not git_dir.exists():
        raise SystemExit(f"submodule path exists but is not initialized: {submodule_dir}")
    return output(["git", "-C", str(submodule_dir), "rev-parse", "--short", "HEAD"])


def kernel_source_path(submodule_dir: Path, filename: str) -> Path:
    direct = submodule_dir / filename
    if direct.exists():
        return direct
    nested = submodule_dir / "kernel" / filename
    if nested.exists():
        return nested
    raise SystemExit(f"missing upstream kernel file: {filename}")


def changed_files(submodule_dir: Path, target: Path) -> list[str]:
    changed: list[str] = []
    for filename in KERNEL_FILES:
        source = kernel_source_path(submodule_dir, filename)
        destination = target / "prompts" / "meta" / filename
        if not destination.exists() or source.read_bytes() != destination.read_bytes():
            changed.append(str(destination.relative_to(target)))
    return changed


def write_upstream_metadata(target: Path, remote: str, revision: str, submodule_path: Path) -> None:
    upstream_toml = "\n".join(
        [
            'name = "research-agent-metaprompt"',
            f'remote = "{remote}"',
            'distribution_mode = "git-submodule"',
            f'revision = "{revision}"',
            f'submodule_path = "{submodule_path.as_posix()}"',
            'metaprompt_groups = ["kernel"]',
            'shared_metaprompt_source = "submodule:kernel-*.md"',
            'materialized_shared_kernel = "prompts/meta/kernel-*.md"',
            'generated_agent_prompts = "project-local"',
            'generated_skill_capsules = "project-local"',
            'generated_templates = "project-local"',
            'generated_project_scripts = "project-local"',
            "preserve_project_profile = true",
            "",
        ]
    )
    (target / "prompts" / "upstream.toml").write_text(upstream_toml, encoding="utf-8")

    managed = {
        "distribution_mode": "git-submodule",
        "managed_files": [f"prompts/meta/{filename}" for filename in KERNEL_FILES]
        + ["prompts/upstream-managed.json"],
        "name": "research-agent-metaprompt",
        "remote": remote,
        "revision": revision,
        "submodule_path": submodule_path.as_posix(),
        "preserve_project_profile": True,
        "note": (
            "Shared kernel files are materialized from the pinned submodule. "
            "prompts/meta/kernel-project.md remains project-local."
        ),
    }
    (target / "prompts" / "upstream-managed.json").write_text(
        json.dumps(managed, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_redeploy_marker(target: Path, revision: str) -> None:
    marker = target / "prompts" / "REDEPLOY_REQUIRED.md"
    marker.write_text(
        "\n".join(
            [
                "# REDEPLOY REQUIRED",
                "",
                f"Shared research-agent metaprompts were synced at `{revision}`.",
                "Regenerate project-local Codex prompts, support docs, skill capsules,",
                "schema reports, token telemetry, and prompt audit artifacts before",
                "removing this marker.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sync shared research-agent metaprompt assets from the pinned "
            "submodule while preserving prompts/meta/kernel-project.md. "
            "Generated skills, templates, scripts, and agent prompts are "
            "project-local derived outputs."
        )
    )
    parser.add_argument("--target", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument("--submodule-dir", type=Path, default=DEFAULT_SUBMODULE_DIR)
    parser.add_argument(
        "--upstream-dir",
        type=Path,
        help="Deprecated alias for --submodule-dir, kept for old automation.",
    )
    parser.add_argument("--revision", help="Require the submodule to be at this commit prefix")
    parser.add_argument("--groups", default=DEFAULT_GROUPS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-fetch", action="store_true", help="Deprecated no-op; submodule pins are explicit")
    args = parser.parse_args()

    target = args.target.resolve()
    submodule_dir = (target / (args.upstream_dir or args.submodule_dir)).resolve()
    project_profile = target / PROJECT_PROFILE
    if not project_profile.exists():
        raise SystemExit(f"missing project profile: {project_profile}")

    before_hash = sha256(project_profile)
    revision = ensure_submodule(submodule_dir)
    if args.revision and not revision.startswith(args.revision):
        raise SystemExit(f"submodule revision {revision} does not match requested {args.revision}")

    changed = changed_files(submodule_dir, target)
    mode = "DRY-RUN" if args.dry_run else "SYNCED"
    print(f"{mode} research-agent submodule revision {revision}")
    print("changed kernel files:")
    for path in changed:
        print(f"  {path}")
    if args.dry_run:
        print(f"{PROJECT_PROFILE} would be preserved ({before_hash})")
        return 0

    meta_dir = target / "prompts" / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    for filename in KERNEL_FILES:
        shutil.copy2(kernel_source_path(submodule_dir, filename), meta_dir / filename)
    write_upstream_metadata(
        target,
        args.remote,
        revision,
        (args.upstream_dir or args.submodule_dir),
    )
    write_redeploy_marker(target, revision)

    after_hash = sha256(project_profile)
    if before_hash != after_hash:
        raise SystemExit(
            "sync modified prompts/meta/kernel-project.md; restore it before continuing"
        )

    print(
        f"{mode} research-agent submodule revision {revision}; "
        f"{PROJECT_PROFILE} preserved ({after_hash})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
