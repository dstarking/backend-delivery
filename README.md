# backend-delivery

后端需求全流程交付 Agent Skill（v1.0.0）。通过 BrowserSkill 取证网页需求，再按阶段完成需求拆分、技术设计、模块实施、接口与回归测试，以及问题修复闭环。

## 能力

- 网页需求证据记录、后端需求提取、模块分组与开发顺序
- 基于实际代码的技术方案，包括 Mermaid 数据流图、功能流程图、时序图、DDL 及技术选型
- 每个模块独立实施计划、接口清单、修改文件清单、代码风格对齐、确认门禁
- 模块测试、全量回归、接口请求与响应示例、缺陷汇总和复测
- 进度文件、版本变更与需求-设计-代码-测试追溯

**强制规则：技术方案未经确认不得编码；每个模块实施计划未经确认不得修改该模块代码。** 真实浏览器操作和测试依赖环境授权与可用工具，不能虚构结果。

## 安装（Windows）

推荐将整个仓库下载/克隆到本地，然后运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows.ps1 -Target Both -Scope User
```

该脚本会复制到用户级 Codex `%USERPROFILE%\.agents\skills\backend-delivery` 与 Claude Code `%USERPROFILE%\.claude\skills\backend-delivery`，已有目标目录时不会覆盖。也可将仓库直接克隆到任一 Skills 目录中。

## 使用

在 Codex 中：`$backend-delivery`；在 Claude Code 中：`/backend-delivery`。

例如：

> 使用 backend-delivery 和已安装的 BrowserSkill 分析需求文档 URL；读取后端仓库现状，输出需求拆分、模块顺序和技术方案，保存 Markdown 文档；在我批准方案前，不要修改代码。

请先阅读 [SKILL.md](SKILL.md) 和 [使用说明](references/06-user-guide.md)。额外中文操作说明见 [docs/使用说明.md](docs/使用说明.md)。

## 目录

- `SKILL.md` — Skill 入口及执行硬约束
- `references/` — 各阶段流程规范与使用指南
- `assets/templates/` — 10 份可复用 Markdown 文档模板
- `scripts/` — Windows 安装、项目初始化、文档验证脚本
- `tests/` — 脚本自动化测试

## 本地验证

```powershell
python -m unittest discover -s tests -v
```

采用真实开发项目时，仍需根据项目运行实际构建、集成测试及接口测试。
