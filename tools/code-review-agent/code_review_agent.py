from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class Finding:
    severity: str  # "ERROR" | "WARN"
    kind: str
    path: str
    line: int
    snippet: str


TEXT_EXTENSIONS = {
    ".java",
    ".kt",
    ".groovy",
    ".xml",
    ".yml",
    ".yaml",
    ".properties",
    ".sql",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".md",
    ".html",
    ".css",
    ".txt",
}


PATTERNS: List[Tuple[str, str, re.Pattern]] = [
    ("ERROR", "debugger", re.compile(r"^\s*debugger\s*;?\s*(//.*)?$")),
    ("ERROR", "console.log", re.compile(r"\bconsole\.log\s*\(")),
    ("WARN", "System.out.println", re.compile(r"\bSystem\.out\.println\s*\(")),
    ("WARN", "printStackTrace", re.compile(r"\.printStackTrace\s*\(")),
]


COMMENTED_CODE_HEURISTICS: List[Tuple[str, re.Pattern]] = [
    ("commented-code(js/java)", re.compile(r"^\s*//\s*(if|for|while|return|throw|new)\b")),
    ("commented-code(block)", re.compile(r"/\*.*\b(if|for|while|return|throw|new)\b.*\*/")),
]

TODO_TAGS = ("TODO", "FIXME")
COMMENT_PREFIXES = ("//", "#", "--", "/*", "*", "<!--")


def _is_probably_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def _iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for p in paths:
        if p.is_dir():
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "build", "dist", "target"}]
                for f in files:
                    fp = Path(root) / f
                    if _is_probably_text_file(fp):
                        yield fp
        elif p.is_file() and _is_probably_text_file(p):
            yield p


def _read_lines(path: Path) -> List[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()


def _scan_todo_fixme_in_comment_line(line: str) -> List[str]:
    stripped = line.lstrip()
    if not stripped:
        return []
    if not any(stripped.startswith(prefix) for prefix in COMMENT_PREFIXES):
        return []
    return [tag for tag in TODO_TAGS if re.search(rf"\b{tag}\b", stripped)]


def scan_file(path: Path) -> List[Finding]:
    findings: List[Finding] = []
    lines = _read_lines(path)

    for idx, line in enumerate(lines, start=1):
        for severity, kind, pattern in PATTERNS:
            if pattern.search(line):
                findings.append(
                    Finding(
                        severity=severity,
                        kind=kind,
                        path=str(path),
                        line=idx,
                        snippet=line.strip()[:240],
                    )
                )

        for tag in _scan_todo_fixme_in_comment_line(line):
            findings.append(
                Finding(
                    severity="WARN",
                    kind=tag,
                    path=str(path),
                    line=idx,
                    snippet=line.strip()[:240],
                )
            )

        for kind, pattern in COMMENTED_CODE_HEURISTICS:
            if pattern.search(line):
                findings.append(
                    Finding(
                        severity="WARN",
                        kind=kind,
                        path=str(path),
                        line=idx,
                        snippet=line.strip()[:240],
                    )
                )

    return findings


def _git_staged_files() -> List[Path]:
    try:
        out = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).strip()
    except Exception:
        return []
    if not out:
        return []
    return [Path(p) for p in out.splitlines() if p.strip()]


def _group_todos(findings: List[Finding]) -> List[Tuple[str, List[Finding]]]:
    buckets = {"backend": [], "frontend": [], "db": [], "other": []}
    for f in findings:
        if f.kind not in {"TODO", "FIXME"}:
            continue
        p = f.path.replace("\\", "/")
        if "sample/backend/" in p:
            buckets["backend"].append(f)
        elif "sample/frontend/" in p:
            buckets["frontend"].append(f)
        elif "sample/db/" in p or p.endswith("schema.sql") or p.endswith("data.sql"):
            buckets["db"].append(f)
        else:
            buckets["other"].append(f)
    return [(k, buckets[k]) for k in ["backend", "frontend", "db", "other"] if buckets[k]]


def render_markdown(findings: List[Finding]) -> str:
    errors = [f for f in findings if f.severity == "ERROR"]
    warns = [f for f in findings if f.severity == "WARN"]

    lines: List[str] = []
    lines.append("# Pre-commit Code Review Report (v0)")
    lines.append("")
    lines.append(f"- Errors: {len(errors)}")
    lines.append(f"- Warnings: {len(warns)}")
    lines.append("")

    def _section(title: str, items: List[Finding]) -> None:
        if not items:
            return
        lines.append(f"## {title}")
        lines.append("")
        for f in items:
            lines.append(f"- `{f.path}:{f.line}` [{f.severity}] `{f.kind}` — {f.snippet}")
        lines.append("")

    _section("Errors", errors)
    _section("Warnings", warns)

    todo_groups = _group_todos(findings)
    if todo_groups:
        lines.append("## TODO / FIXME (grouped)")
        lines.append("")
        for group, items in todo_groups:
            lines.append(f"### {group}")
            lines.append("")
            for f in items:
                lines.append(f"- `{f.path}:{f.line}` `{f.kind}` — {f.snippet}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Pre-commit code review helper (regex-based).")
    parser.add_argument("--staged", action="store_true", help="Scan only git staged files.")
    parser.add_argument("--paths", nargs="*", default=[], help="Paths to scan (files/dirs).")
    args = parser.parse_args(argv)

    if args.staged:
        targets = _git_staged_files()
        if not targets:
            print("No staged files found (or not a git repo).", file=sys.stderr)
            return 0
    else:
        if not args.paths:
            print("Provide --paths ... or use --staged", file=sys.stderr)
            return 2
        targets = [Path(p) for p in args.paths]

    findings: List[Finding] = []
    for fp in _iter_files(targets):
        findings.extend(scan_file(fp))

    report = render_markdown(findings)
    print(report, end="")

    has_error = any(f.severity == "ERROR" for f in findings)
    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
