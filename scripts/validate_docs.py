#!/usr/bin/env python3
"""Static doc integrity checker. Does not validate actual tests or SQL semantics."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from init_project import PROJECT_FILES, checked_id

SECTION_REQUIREMENTS = {
    "01-requirements.md": ("## 2. 需求统计", "## 3. 模块划分与开发顺序", "## 4. 后端需求明细"),
    "02-technical-design.md": ("## 4. API 合约设计", "## 5. 数据流图", "## 6. 功能流程图", "## 7. 时序图", "## 8. 数据模型、数据库 DDL 与迁移", "## 10. 技术难点与方案权衡"),
    "05-final-test-report.md": ("## 2. 接口全量清单与需求覆盖", "## 3. 逐接口测试明细及入参与响应示例", "## 5. 测试统计与覆盖"),
}
PLAN_SECTIONS = ("## 3. API 实现清单", "## 4. 预计文件变更清单", "## 5. 核心实现步骤与逻辑", "## 6. 本模块测试方案", "## 8. 审批记录")
TEST_SECTIONS = ("## 2. 本模块接口清单与覆盖", "## 3. 测试用例与结果", "## 4. 测试统计、结论与遗留")
TEMPLATE_MARKERS = ("[待填写]", "[待核实]", "[待设计", "[待确认]", "待统计", "[待校验]", "[待排查]", "草稿 v0.1")


def inspect(repo: Path, project: str, phase: str = "skeleton") -> tuple[list[str], list[str]]:
    checked_id(project, "project")
    folder = repo.resolve() / "docs" / "ai-delivery" / project
    errors: list[str] = []
    warnings: list[str] = []
    if not folder.is_dir():
        return [f"项目文档目录不存在：{folder}"], warnings

    texts: dict[str, str] = {}
    for filename in PROJECT_FILES:
        dest = folder / filename
        if not dest.is_file():
            errors.append(f"缺少文件：{filename}")
            continue
        try:
            source = dest.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"无法读取 {filename}：{exc}")
            continue
        texts[filename] = source
        if not source.lstrip().startswith("#"):
            warnings.append(f"{filename} 没有 Markdown 标题")
        for heading in SECTION_REQUIREMENTS.get(filename, ()):
            if heading not in source:
                errors.append(f"{filename} 缺少章节：{heading}")

    plans = sorted((folder / "03-modules").glob("*-plan.md")) if (folder / "03-modules").is_dir() else []
    tests = sorted((folder / "04-module-tests").glob("*-test.md")) if (folder / "04-module-tests").is_dir() else []
    tests_by_module = {p.name.removesuffix("-test.md"): p for p in tests}
    plans_by_module = {p.name.removesuffix("-plan.md"): p for p in plans}
    for module, file in plans_by_module.items():
        source = file.read_text(encoding="utf-8")
        for heading in PLAN_SECTIONS:
            if heading not in source:
                errors.append(f"{file.name} 缺少章节：{heading}")
        if module not in tests_by_module:
            errors.append(f"模块 {module} 缺少单独测试文件")
    for module, file in tests_by_module.items():
        source = file.read_text(encoding="utf-8")
        for heading in TEST_SECTIONS:
            if heading not in source:
                errors.append(f"{file.name} 缺少章节：{heading}")
        if module not in plans_by_module:
            errors.append(f"模块 {module} 缺少单独实施计划")

    design = texts.get("02-technical-design.md", "")
    diagrams = re.findall(r"```mermaid\s*\n(.*?)```", design, flags=re.DOTALL)
    flowcharts = sum(bool(re.search(r"^\s*flowchart\s+", d, re.MULTILINE)) for d in diagrams)
    sequence = any(re.search(r"^\s*sequenceDiagram\b", d, re.MULTILINE) for d in diagrams)
    if flowcharts < 2:
        errors.append("技术方案必须包含两张 Mermaid flowchart（数据流、功能流程）")
    if not sequence:
        errors.append("技术方案必须包含 Mermaid sequenceDiagram 时序图")
    if "```sql" not in design and "无 DDL 变更" not in design:
        errors.append("技术方案缺少 SQL DDL 或明确的“无 DDL 变更”")

    if phase != "skeleton":
        file_for_phase = {
            "requirements": ["01-requirements.md", "09-source-evidence.md", "08-traceability.md"],
            "design": ["02-technical-design.md"],
            "module": ["00-project-control.md"],
            "final-test": ["05-final-test-report.md"],
            "release": list(PROJECT_FILES),
        }[phase]
        checks = {name: texts.get(name, "") for name in file_for_phase}
        if phase in ("module", "release"):
            if not plans:
                errors.append("还没有独立的模块计划")
            for p in plans + tests:
                checks[p.name] = p.read_text(encoding="utf-8")
        for filename, source in checks.items():
            matched = [marker for marker in TEMPLATE_MARKERS if marker in source]
            if matched:
                warnings.append(f"{filename} 仍包含模板占位内容：{', '.join(matched[:4])}")
        if phase in ("design", "release"):
            if any("待设计" in block for block in diagrams) or re.search(r"```sql\s*\n\s*--\s*待设计", design):
                errors.append("技术方案 Mermaid/DDL 仍包含占位内容，不能视为可审批完成")
            if phase == "release" and not re.search(r"审批状态[：:]\s*`?APPROVED`?", design):
                errors.append("技术方案缺少明确 APPROVED 状态，或仍未更新审批记录")
        if phase == "module":
            for p in plans:
                source = p.read_text(encoding="utf-8")
                if "WAITING_APPROVAL" in source:
                    warnings.append(f"{p.name} 仍处于待审批，不能编码")
        if phase in ("final-test", "release"):
            report = texts.get("05-final-test-report.md", "")
            if "## 3. 逐接口测试明细及入参与响应示例" not in report:
                errors.append("未提供每接口入参和响应的测试章节")
            if phase == "release":
                if "NOT_RUN" in report or "BLOCKED" in report:
                    errors.append("全量测试中出现 NOT_RUN/BLOCKED；不能宣称全量交付通过")
                if "未执行" in report:
                    errors.append("测试报告包含未执行项；需真实验证或披露非完整交付")
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--phase", choices=("skeleton", "requirements", "design", "module", "final-test", "release"), default="skeleton")
    args = parser.parse_args(argv)
    try:
        errors, warnings = inspect(args.repo, args.project, args.phase)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for item in warnings:
        print(f"WARN  {item}")
    for item in errors:
        print(f"ERROR {item}")
    print(f"\n文档结构检查：{len(errors)} 个错误，{len(warnings)} 个提醒。此检查不证明业务/DDL/API/测试正确。")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
