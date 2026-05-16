#!/usr/bin/env python3
"""Validate the project-local prompt deployment after a metaprompt sync."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SKILL_FIELDS = {
    "id",
    "purpose",
    "trigger",
    "minimal_instruction",
    "full_ref",
    "input_contract",
    "forbidden_context",
    "success_metric",
    "token_target",
}

EXPECTED_SKILLS = {
    "SKILL-CONDENSE-V2.md",
    "SKILL-GIT-WORKTREE.md",
    "SKILL-HANDOFF-AUDIT.md",
    "SKILL-PAPER-WRITING.md",
    "SKILL-PRESENTATION-DECK.md",
    "SKILL-PRESENTATION-ILLUSTRATION.md",
    "SKILL-PROMPT-AUDIT.md",
    "SKILL-SCHEME-CODE.md",
    "SKILL-TOOL-TRUST.md",
}


def expected_agent_count() -> int:
    roles_path = ROOT / "prompts" / "meta" / "kernel-roles.md"
    body = text(roles_path)
    match = re.search(
        r"# § AGENT PROFILE TABLE.*?\n\| Agent \|.*?\n\|[- |]+\|\n(?P<rows>.*?)(?:\n\n|─)",
        body,
        re.S,
    )
    if not match:
        return 24
    rows = [
        line
        for line in match.group("rows").splitlines()
        if line.startswith("| ") and not line.startswith("| Agent ")
    ]
    return len(rows)


def git_changed(path: str) -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", path],
        cwd=ROOT,
    )
    return result.returncode != 0


def count_files(path: Path, pattern: str) -> int:
    return len([item for item in path.glob(pattern) if item.is_file()])


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(condition: bool, name: str, detail: str, results: list[dict]) -> None:
    results.append(
        {
            "name": name,
            "status": "PASS" if condition else "FAIL",
            "detail": detail,
        }
    )


def skill_fields(path: Path) -> set[str]:
    fields = set()
    for line in text(path).splitlines():
        match = re.match(r"^([A-Za-z_]+):", line)
        if match:
            fields.add(match.group(1))
    return fields


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-redeploy-marker", action="store_true")
    parser.add_argument("--expected-revision")
    args = parser.parse_args()

    results: list[dict] = []
    project_rules = re.findall(r"^## PR-", text(ROOT / "docs" / "03_PROJECT_RULES.md"), re.M)
    codex_agents = count_files(ROOT / "prompts" / "agents-codex", "*.md")
    claude_agents = count_files(ROOT / "prompts" / "agents-claude", "*.md")
    agent_count = expected_agent_count()
    skill_paths = sorted((ROOT / "prompts" / "skills").glob("SKILL-*.md"))
    upstream = text(ROOT / "prompts" / "upstream.toml")
    revision_match = re.search(r'^revision = "([^"]+)"$', upstream, re.M)
    revision = revision_match.group(1) if revision_match else ""
    managed = ROOT / "prompts" / "upstream-managed.json"
    redeploy = ROOT / "prompts" / "REDEPLOY_REQUIRED.md"

    check(len(project_rules) == 6, "project_rules_count", f"found {len(project_rules)} PR rules", results)
    check(codex_agents == agent_count, "codex_agent_count", f"found {codex_agents}; expected {agent_count}", results)
    check(claude_agents == agent_count, "claude_agent_count", f"found {claude_agents}; expected {agent_count}", results)
    skill_names = {path.name for path in skill_paths}
    missing_skills = sorted(EXPECTED_SKILLS - skill_names)
    unexpected_skills = sorted(skill_names - EXPECTED_SKILLS)
    check(len(skill_paths) == len(EXPECTED_SKILLS), "skill_capsule_count", f"found {len(skill_paths)}", results)
    check(
        not missing_skills and not unexpected_skills,
        "skill_capsule_manifest",
        json.dumps({"missing": missing_skills, "unexpected": unexpected_skills}, sort_keys=True),
        results,
    )
    missing_fields = {
        str(path.relative_to(ROOT)): sorted(REQUIRED_SKILL_FIELDS - skill_fields(path))
        for path in skill_paths
        if REQUIRED_SKILL_FIELDS - skill_fields(path)
    }
    check(not missing_fields, "skill_required_fields", json.dumps(missing_fields, sort_keys=True), results)
    check(bool(revision), "upstream_revision_present", f"found {revision or 'missing'}", results)
    if args.expected_revision:
        check(revision == args.expected_revision, "upstream_revision_expected", f"found {revision}", results)
    check(
        "distribution_mode = \"git-submodule\"" in upstream,
        "distribution_mode",
        "expected git-submodule",
        results,
    )
    check(
        'submodule_path = "prompts/upstream/research-agent"' in upstream,
        "submodule_path",
        "prompts/upstream/research-agent",
        results,
    )
    check("generated_agent_prompts = \"project-local\"" in upstream, "agent_distribution_boundary", "project-local", results)
    check(managed.exists(), "managed_marker", str(managed.relative_to(ROOT)), results)
    check((ROOT / ".gitmodules").exists(), "gitmodules_present", ".gitmodules", results)
    check((ROOT / "prompts" / "upstream" / "research-agent").exists(), "research_agent_submodule_present", "prompts/upstream/research-agent", results)
    check(not git_changed("prompts/meta/kernel-project.md"), "project_profile_unchanged", "no diff vs HEAD", results)
    check(not Path(ROOT / "agents").exists(), "no_root_agents_export", "root agents/ absent", results)
    check(not Path(ROOT / "skills").exists(), "no_root_skills_export", "root skills/ absent", results)
    check(
        args.allow_redeploy_marker or not redeploy.exists(),
        "redeploy_marker_removed",
        "present" if redeploy.exists() else "absent",
        results,
    )
    check((ROOT / "schema_resolution_report.json").exists(), "schema_report_present", "schema_resolution_report.json", results)
    check((ROOT / "token_telemetry_report.json").exists(), "token_report_present", "token_telemetry_report.json", results)
    wiki_dir = ROOT / "docs" / "wiki"
    wiki_report = ROOT / "wiki_knowledge_injection_report.json"
    check(
        wiki_report.exists() or not wiki_dir.exists(),
        "wiki_knowledge_report_or_waiver",
        str(wiki_report.relative_to(ROOT)) if wiki_report.exists() else "docs/wiki absent",
        results,
    )
    if (ROOT / "token_telemetry_report.json").exists():
        telemetry = json.loads(text(ROOT / "token_telemetry_report.json"))
        q3b = telemetry.get("q3b", {})
        check(
            "skill_trigger_tokens" in q3b or "skill_trigger_tokens" in telemetry,
            "token_skill_trigger_tokens",
            "present" if ("skill_trigger_tokens" in q3b or "skill_trigger_tokens" in telemetry) else "missing",
            results,
        )
        check(
            "wiki_static_tokens" in q3b or "wiki_static_tokens" in telemetry,
            "token_wiki_static_tokens",
            "present" if ("wiki_static_tokens" in q3b or "wiki_static_tokens" in telemetry) else "missing",
            results,
        )

    status = "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL"
    print(json.dumps({"status": status, "checks": results}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
