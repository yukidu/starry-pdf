#!/usr/bin/env python3
"""Review Stirling PDF's pinned version and retrieve only its MIT-scope source.

DOES NOT imply a runnable standalone PDF application; dependencies and licensing
must be reviewed separately before building or deploying.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

PINNED_URL = "https://github.com/Stirling-Tools/Stirling-PDF.git"
PINNED_TAG = "v3.2.1"
PINNED_SHA = "cb7b58a2c0c00d6350de51994e5c47317b204d85"
EXPECTED_EXCLUDED = frozenset({
    "app/proprietary", "app/saas", "engine",
    "frontend/editor/src/proprietary", "frontend/editor/src/desktop",
    "frontend/editor/src/saas", "frontend/editor/src/cloud",
    "frontend/editor/src/portal", "frontend/editor/src/portal-saas",
})

def run(*args: str, cwd: Path | None = None) -> str:
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    if p.returncode:
        raise RuntimeError(f"Failed {args[0]}: {p.stderr.strip()[:1000]}")
    return p.stdout.strip()

def parse_restricted_paths(license_text: str) -> set[str]:
    if not license_text.startswith("MIT License\n"):
        raise ValueError("Unexpected root license, human review required")
    return {x[:-1] for x in re.findall(r'"([\w./-]+/)"', license_text)}

def check_upstream_license(license_text: str) -> set[str]:
    paths = parse_restricted_paths(license_text)
    if paths != EXPECTED_EXCLUDED:
        raise ValueError(f"License scope changed; expected {sorted(EXPECTED_EXCLUDED)}; got {sorted(paths)}")
    if "Copyright (c) 2025 Stirling PDF Inc." not in license_text:
        raise ValueError("Copyright notice is missing")
    return paths

def sparse_rules(exclusions: set[str]) -> str:
    for p in exclusions:
        if p.startswith("/") or ".." in Path(p).parts or not re.fullmatch(r"[a-zA-Z0-9_./-]+", p):
            raise ValueError(f"Unsafe path: {p}")
    return "/*\n" + "".join(f"!/{p}/\n" for p in sorted(exclusions))

def source_copy(repo_url: str, tag: str, expected_sha: str, target: Path) -> dict:
    target = target.resolve()
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stirling-stage-", dir=target.parent) as td:
        temp = Path(td) / "repository"
        run("git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout", "--branch", tag, repo_url, str(temp))
        actual_sha = run("git", "rev-parse", "HEAD", cwd=temp)
        if actual_sha != expected_sha:
            raise ValueError(f"Upstream tag mismatch: expected {expected_sha}, got {actual_sha}")
        paths = check_upstream_license(run("git", "show", "HEAD:LICENSE", cwd=temp) + "\n")
        info = temp / ".git" / "info" / "sparse-checkout"
        info.parent.mkdir(parents=True, exist_ok=True)
        info.write_text(sparse_rules(paths), encoding="utf-8")
        run("git", "config", "core.sparseCheckout", "true", cwd=temp)
        run("git", "read-tree", "-mu", "HEAD", cwd=temp)
        if not (temp / "LICENSE").exists() or not (temp / "README.md").exists():
            raise RuntimeError("Sparse checkout did not retrieve license / README")
        for excluded in paths:
            if (temp / excluded).exists():
                raise RuntimeError(f"Restricted subtree materialized: {excluded}")
        symlinks = [p for p in temp.rglob("*") if p.is_symlink() and ".git" not in p.relative_to(temp).parts]
        if symlinks:
            raise RuntimeError(f"Symlinks require individual review: {symlinks[:3]}")
        files = [p for p in temp.rglob("*") if p.is_file() and ".git" not in p.relative_to(temp).parts]
        if len(files) < 2:
            raise RuntimeError("No source files found")
        shutil.rmtree(temp / ".git")
        temp.rename(target)
    return {
        "origin": repo_url,
        "tag": tag,
        "commit": actual_sha,
        "license": "MIT except separately licensed directories",
        "excluded_separate_license_directories": sorted(paths),
        "file_count": len(files),
        "obtained_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "notes": "Further third-party license and dependency verification required",
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=PINNED_URL)
    parser.add_argument("--tag", default=PINNED_TAG)
    parser.add_argument("--sha", default=PINNED_SHA)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "vendor" / "stirling-pdf")
    args = parser.parse_args()
    audit = source_copy(args.repo, args.tag, args.sha, args.output)
    audit_path = args.output.parent.parent / "source-audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Audited upstream snapshot:", args.output, "| files:", audit["file_count"])

if __name__ == "__main__":
    main()
