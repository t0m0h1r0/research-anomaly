#!/usr/bin/env python3
"""Sync shared research-agent metaprompts from a remote snapshot.

The receiving project keeps no persistent ``prompts/upstream`` checkout. This
script materializes only shared ``kernel-*.md`` files into ``prompts/meta/`` and
preserves the local ``prompts/meta/kernel-project.md`` byte-for-byte.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REMOTE = "git@github.com:t0m0h1r0/research-agent.git"
DEFAULT_BRANCH = "main"
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


def kernel_source_path(source_dir: Path, filename: str) -> Path:
    direct = source_dir / filename
    if direct.exists():
        return direct
    nested = source_dir / "kernel" / filename
    if nested.exists():
        return nested
    raise SystemExit(f"missing source kernel file: {filename}")


def source_revision(source_dir: Path) -> str:
    try:
        return output(["git", "-C", str(source_dir), "rev-parse", "HEAD"])
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"source dir is not a git checkout: {source_dir}") from exc


def changed_files(source_dir: Path, target: Path) -> list[str]:
    changed: list[str] = []
    for filename in KERNEL_FILES:
        source = kernel_source_path(source_dir, filename)
        destination = target / "prompts" / "meta" / filename
        if not destination.exists() or source.read_bytes() != destination.read_bytes():
            changed.append(str(destination.relative_to(target)))
    return changed


def write_upstream_metadata(target: Path, remote: str, branch: str, revision: str) -> None:
    upstream_toml = "\n".join(
        [
            'name = "research-agent-metaprompt"',
            f'remote = "{remote}"',
            f'branch = "{branch}"',
            'distribution_mode = "git-remote-snapshot"',
            f'revision = "{revision}"',
            'metaprompt_groups = ["kernel"]',
            'shared_metaprompt_source = "remote-snapshot:kernel-*.md"',
            'materialized_shared_kernel = "prompts/meta/kernel-*.md"',
            'local_project_profile = "prompts/meta/kernel-project.md"',
            'persistent_upstream_checkout = false',
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
        "distribution_mode": "git-remote-snapshot",
        "generated_agent_prompts": "project-local",
        "generated_project_scripts": "project-local",
        "generated_skill_capsules": "project-local",
        "generated_templates": "project-local",
        "local_project_profile": PROJECT_PROFILE.as_posix(),
        "managed_files": [f"prompts/meta/{filename}" for filename in KERNEL_FILES]
        + ["prompts/upstream-managed.json"],
        "name": "research-agent-metaprompt",
        "note": (
            "Shared kernel files are materialized from an ephemeral remote "
            "snapshot. prompts/meta/kernel-project.md remains project-local. "
            "No persistent prompts/upstream checkout is kept."
        ),
        "preserve_project_profile": True,
        "remote": remote,
        "branch": branch,
        "revision": revision,
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
                f"Shared research-agent metaprompts were synced at `{revision[:12]}`.",
                "Run a zero-base project-local prompt deployment, regenerate",
                "Codex/Claude prompts, support docs, skill capsules, schema reports,",
                "token telemetry/ROI reports, and prompt audit artifacts before",
                "removing this marker.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def sync_from_source(
    *,
    target: Path,
    source_dir: Path,
    remote: str,
    branch: str,
    dry_run: bool,
) -> str:
    project_profile = target / PROJECT_PROFILE
    if not project_profile.exists():
        raise SystemExit(f"missing project profile: {project_profile}")

    before_hash = sha256(project_profile)
    revision = source_revision(source_dir)
    changed = changed_files(source_dir, target)
    mode = "DRY-RUN" if dry_run else "SYNCED"
    print(f"{mode} research-agent remote snapshot {revision[:12]}")
    print("changed kernel files:")
    for path in changed:
        print(f"  {path}")
    if dry_run:
        print(f"{PROJECT_PROFILE} would be preserved ({before_hash})")
        return revision

    meta_dir = target / "prompts" / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    for filename in KERNEL_FILES:
        shutil.copy2(kernel_source_path(source_dir, filename), meta_dir / filename)
    write_upstream_metadata(target, remote, branch, revision)
    write_redeploy_marker(target, revision)

    after_hash = sha256(project_profile)
    if before_hash != after_hash:
        raise SystemExit(
            "sync modified prompts/meta/kernel-project.md; restore it before continuing"
        )

    print(
        f"{mode} research-agent remote snapshot {revision[:12]}; "
        f"{PROJECT_PROFILE} preserved ({after_hash})"
    )
    return revision


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sync shared research-agent metaprompt assets from a remote snapshot "
            "while preserving prompts/meta/kernel-project.md. Generated skills, "
            "templates, scripts, and agent prompts are project-local derived outputs."
        )
    )
    parser.add_argument("--target", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--source-dir", type=Path, help="Existing temporary research-agent checkout")
    parser.add_argument("--revision", help="Require the source checkout to be at this commit prefix")
    parser.add_argument("--groups", default=DEFAULT_GROUPS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep the temporary clone path after sync for inspection",
    )
    args = parser.parse_args()

    target = args.target.resolve()
    if args.groups != DEFAULT_GROUPS:
        raise SystemExit("only metaprompt group 'kernel' is supported")

    if args.source_dir:
        source_dir = args.source_dir.resolve()
        revision = source_revision(source_dir)
        if args.revision and not revision.startswith(args.revision):
            raise SystemExit(
                f"source revision {revision} does not match requested {args.revision}"
            )
        sync_from_source(
            target=target,
            source_dir=source_dir,
            remote=args.remote,
            branch=args.branch,
            dry_run=args.dry_run,
        )
        return 0

    temp_parent = Path("/private/tmp") if Path("/private/tmp").exists() else None
    with tempfile.TemporaryDirectory(
        prefix="research-agent-metaprompt-",
        dir=str(temp_parent) if temp_parent else None,
    ) as tmp:
        source_dir = Path(tmp) / "research-agent"
        run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                args.branch,
                args.remote,
                str(source_dir),
            ]
        )
        revision = source_revision(source_dir)
        if args.revision and not revision.startswith(args.revision):
            raise SystemExit(
                f"source revision {revision} does not match requested {args.revision}"
            )
        sync_from_source(
            target=target,
            source_dir=source_dir,
            remote=args.remote,
            branch=args.branch,
            dry_run=args.dry_run,
        )
        if args.keep_temp:
            kept = Path(tmp + "-kept")
            shutil.copytree(tmp, kept)
            print(f"kept temporary checkout at {kept}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
