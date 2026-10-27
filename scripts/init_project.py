#!/usr/bin/env python3
"""Initialize backend-delivery docs without overwriting existing files.

Python >=3.9, standard-library-only; never edits source code or approval states.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "assets" / "templates"
ID_RE = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
PROJECT_FILES = (
    "00-project-control.md",
    "01-requirements.md",
    "02-technical-design.md",
    "05-final-test-report.md",
    "06-issue-log.md",
    "07-design-changelog.md",
    "08-traceability.md",
    "09-source-evidence.md",
)


def checked_id(value: str, label: str) -> str:
    if not ID_RE.fullmatch(value) or value.endswith("-"):
        raise ValueError(f"{label} 不合法：仅支持以字母开头的小写字母/数字/连字符，最长64字符且不以连字符结尾")
    return value


def render(template_name: str, project: str, module: str | None = None) -> str:
    template = (TEMPLATES / template_name).read_text(encoding="utf-8")
    today = dt.datetime.now(dt.timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %z")
    return (
        template.replace("{{PROJECT_ID}}", project)
        .replace("{{MODULE_ID}}", module or "")
        .replace("{{CREATED_AT}}", today)
    )


def write_new(destination: Path, content: str) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    # "x" mode is atomic no-overwrite, even across concurrent runs.
    try:
        with destination.open("x", encoding="utf-8", newline="\n") as out:
            out.write(content)
        print(f"CREATED  {destination}")
        return True
    except FileExistsError:
        print(f"SKIPPED  {destination} (已存在，绝不覆盖)")
        return False


def initialize(repo: Path, project: str, module: str | None = None) -> Path:
    checked_id(project, "project")
    if module is not None:
        checked_id(module, "module")
    if not repo.is_dir():
        raise ValueError(f"仓库目录不存在：{repo}")
    folder = repo.resolve() / "docs" / "ai-delivery" / project
    for filename in PROJECT_FILES:
        write_new(folder / filename, render(filename, project))
    (folder / "03-modules").mkdir(exist_ok=True)
    (folder / "04-module-tests").mkdir(exist_ok=True)
    if module:
        write_new(folder / "03-modules" / f"{module}-plan.md", render("03-module-plan.md", project, module))
        write_new(folder / "04-module-tests" / f"{module}-test.md", render("04-module-test.md", project, module))
    return folder


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="Existing repository root")
    parser.add_argument("--project", required=True, help="kebab-case project id")
    parser.add_argument("--module", help="Optional module id; adds plan and test skeleton")
    args = parser.parse_args(argv)
    try:
        path = initialize(args.repo, args.project, args.module)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"\n项目文档目录：{path}\n提示：初始化仅创建空白模板；不代表需求已核验、方案已批准或测试已通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
