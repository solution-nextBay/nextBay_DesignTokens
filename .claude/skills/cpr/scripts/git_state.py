#!/usr/bin/env python3
"""
git_state — plomberie git mécanique pour le skill /cpr.

Remplace les étapes 1 à 3 du workflow (lire l'état git, garde-fou branche
protégée, filtrage des fichiers à exclure) par un seul appel scriptable,
sans passer par un raisonnement LLM ni injecter un diff brut dans le contexte.

Sous-commandes :
  state   — snapshot JSON : branche, protection, upstream, fichiers modifiés,
            diffstat, derniers commits, exclusions détectées, nom de branche suggéré.
  stage   — applique le filtrage (exclut .env, dist/, node_modules/, *.map,
            fichiers suspects) et fait le `git add` des fichiers restants.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

PROTECTED_BRANCHES = {"main"}

HARD_EXCLUDE_DIR_SEGMENTS = {"dist", "node_modules"}

SECRET_HINTS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"credentials", re.I), "credentials file"),
    (re.compile(r"secrets?\.", re.I), "secrets file"),
    (re.compile(r"^id_rsa"), "SSH private key"),
    (re.compile(r"\.pem$", re.I), "PEM key/cert"),
    (re.compile(r"\.p12$|\.pfx$", re.I), "PKCS12 keystore"),
    (re.compile(r"service[-_]?account.*\.json$", re.I), "service account key"),
    (re.compile(r"\.key$", re.I), "key file"),
]

CONFIG_OR_META_PATTERNS = [
    re.compile(r"(^|/)package(-lock)?\.json$"),
    re.compile(r"\.config\.[jt]s$"),
    re.compile(r"(^|/)tsconfig.*\.json$"),
    re.compile(r"(^|/)vite\.config\.[jt]s$"),
    re.compile(r"(^|/)\.eslintrc"),
    re.compile(r"(^|/)\.prettierrc"),
]


class GitError(RuntimeError):
    pass


def run_git(repo_root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def get_current_branch(repo_root: Path) -> str:
    return run_git(repo_root, ["branch", "--show-current"]).strip()


def has_upstream(repo_root: Path, branch: str) -> bool:
    # 1. Tracking branch local configuré
    try:
        run_git(repo_root, ["rev-parse", "--verify", "--quiet", f"{branch}@{{upstream}}"])
        return True
    except GitError:
        pass
    # 2. Ref distante déjà fetchée localement
    try:
        out = run_git(repo_root, ["for-each-ref", f"refs/remotes/origin/{branch}"])
        if out.strip():
            return True
    except GitError:
        pass
    # 3. Appel réseau : branche existante sur origin mais jamais fetchée localement
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--exit-code", "origin", f"refs/heads/{branch}"],
            cwd=repo_root,
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def parse_status_porcelain(raw: str) -> list[dict]:
    entries = []
    for line in raw.splitlines():
        if not line:
            continue
        index_status, worktree_status = line[0], line[1]
        rest = line[3:]
        if index_status == "R" and " -> " in rest:
            _, new_path = rest.split(" -> ", 1)
            path = new_path
        else:
            path = rest
        entries.append(
            {
                "path": path,
                "index_status": index_status if index_status != " " else None,
                "worktree_status": worktree_status if worktree_status != " " else None,
                "is_untracked": index_status == "?" and worktree_status == "?",
            }
        )
    return entries


def get_status(repo_root: Path) -> list[dict]:
    raw = run_git(repo_root, ["status", "--porcelain=v1"])
    return parse_status_porcelain(raw)


def get_diff_stat(repo_root: Path) -> str:
    try:
        return run_git(repo_root, ["diff", "--stat", "HEAD"]).strip()
    except GitError:
        # repo sans commit initial
        return ""


def get_recent_log(repo_root: Path, count: int = 3) -> list[str]:
    try:
        out = run_git(repo_root, ["log", "--oneline", f"-{count}"])
        return [line for line in out.splitlines() if line]
    except GitError:
        return []


def classify_exclusion(path: str) -> tuple[bool, Optional[str], bool]:
    """Returns (excluded, reason, is_flagged_secret)."""
    norm = path.replace("\\", "/")
    name = norm.rsplit("/", 1)[-1]
    segments = norm.split("/")

    if name == ".env" or name.startswith(".env.") or norm.endswith(".env"):
        return True, "fichier .env", False

    if HARD_EXCLUDE_DIR_SEGMENTS & set(segments):
        return True, "artefact de build / dépendances (dist, node_modules)", False

    if norm.endswith(".map"):
        return True, "source map", False

    for pattern, label in SECRET_HINTS:
        if pattern.search(name):
            return True, f"secret potentiel ({label}) — vérifier manuellement", True

    return False, None, False


def _is_config_or_meta(path: str) -> bool:
    norm = path.replace("\\", "/")
    return any(p.search(norm) for p in CONFIG_OR_META_PATTERNS)


def _infer_scope(paths: list[str]) -> Optional[str]:
    counts: Counter[str] = Counter()
    for p in paths:
        parts = Path(p.replace("\\", "/")).parts
        if not parts:
            continue
        if parts[0] == "src" and len(parts) > 1:
            seg = parts[1]
            if seg == "apps" and len(parts) > 2:
                counts[parts[2]] += 1
            else:
                counts[seg] += 1
        elif parts[0] == ".claude":
            counts["claude"] += 1
        else:
            counts[parts[0]] += 1
    if not counts:
        return None
    return counts.most_common(1)[0][0]


def _slugify(text: str) -> str:
    text = re.sub(r"(?<!^)(?=[A-Z])", "-", text)
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text)
    return text.strip("-").lower()


def _infer_slug(paths: list[str]) -> Optional[str]:
    candidates = [p for p in paths if not re.search(r"\.(test|spec)\.", p)]
    target = candidates[0] if candidates else (paths[0] if paths else None)
    if not target:
        return None
    stem = Path(target.replace("\\", "/")).stem
    slug = _slugify(stem)
    return slug or None


def infer_branch_name(entries: list[dict]) -> Optional[str]:
    paths = [e["path"] for e in entries]
    if not paths:
        return None

    if all(re.search(r"\.(test|spec)\.[jt]sx?$", p) for p in paths):
        branch_type = "test"
    elif all(_is_config_or_meta(p) for p in paths):
        branch_type = "chore"
    elif any(e["is_untracked"] or e["index_status"] == "A" for e in entries):
        branch_type = "feat"
    else:
        branch_type = "fix"

    scope = _infer_scope(paths)
    slug = _infer_slug(paths)

    if scope and slug and scope != slug:
        name = f"{branch_type}/{scope}-{slug}"
    else:
        name = f"{branch_type}/{scope or slug or 'update'}"

    branch_type_part, _, rest = name.partition("/")
    return f"{branch_type_part}/{_slugify(rest)}"


def build_state(repo_root: Path) -> dict:
    branch = get_current_branch(repo_root)
    entries = get_status(repo_root)

    exclusions = []
    stageable = []
    for e in entries:
        excluded, reason, flagged = classify_exclusion(e["path"])
        if excluded:
            exclusions.append({"path": e["path"], "reason": reason, "flagged_secret": flagged})
        else:
            stageable.append(e["path"])

    is_protected = branch in PROTECTED_BRANCHES

    return {
        "branch": branch,
        "is_protected": is_protected,
        "has_upstream": has_upstream(repo_root, branch),
        "working_tree_clean": len(entries) == 0,
        "changed_files": entries,
        "diff_stat": get_diff_stat(repo_root),
        "recent_commits": get_recent_log(repo_root),
        "excluded_files": exclusions,
        "stageable_files": stageable,
        "suggested_branch_name": infer_branch_name(entries) if is_protected else None,
    }


def get_pr_url(repo_root: Path, branch: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--head", branch, "--json", "number,url", "-q", ".[0].url"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    return url or None


def cmd_pr_status(args: argparse.Namespace) -> int:
    branch = get_current_branch(args.repo_root)
    url = get_pr_url(args.repo_root, branch)
    print(json.dumps({"branch": branch, "pr_url": url, "has_pr": url is not None}, indent=2))
    return 0


def cmd_state(args: argparse.Namespace) -> int:
    try:
        state = build_state(args.repo_root)
    except GitError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(state, indent=2))
    return 0


def cmd_stage(args: argparse.Namespace) -> int:
    try:
        entries = get_status(args.repo_root)
    except GitError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    staged, excluded = [], []
    for e in entries:
        is_excluded, reason, flagged = classify_exclusion(e["path"])
        if is_excluded:
            excluded.append({"path": e["path"], "reason": reason, "flagged_secret": flagged})
        else:
            staged.append(e["path"])

    if staged and not args.dry_run:
        run_git(args.repo_root, ["add", "--", *staged])

    print(
        json.dumps(
            {"staged": staged, "excluded": excluded, "dry_run": args.dry_run},
            indent=2,
            
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Plomberie git mécanique pour /cpr")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Racine du dépôt (défaut : répertoire courant)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    state_parser = sub.add_parser("state", help="Snapshot JSON de l'état git")
    state_parser.set_defaults(func=cmd_state)

    stage_parser = sub.add_parser("stage", help="Stage les fichiers non exclus")
    stage_parser.add_argument("--dry-run", action="store_true", help="N'exécute pas git add")
    stage_parser.set_defaults(func=cmd_stage)

    pr_status_parser = sub.add_parser(
        "pr-status", help="URL du PR existant pour la branche courante (via gh pr list)"
    )
    pr_status_parser.set_defaults(func=cmd_pr_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
