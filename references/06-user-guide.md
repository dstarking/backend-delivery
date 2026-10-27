# 使用说明（Windows / Codex / Claude Code）

## 安装

下载 zip 后解压出 `backend-delivery/` 文件夹：

- Codex 用户级：复制到 `%USERPROFILE%\.agents\skills\backend-delivery\`；仓库级：`<repo>\.agents\skills\backend-delivery\`。
- Claude Code 用户级：复制到 `%USERPROFILE%\.claude\skills\backend-delivery\`；仓库级：`<repo>\.claude\skills\backend-delivery\`。
- 要同时给二者使用，可以复制两份同名 skill；需要更新时同步两份。首次不出现可重启对应应用。

Codex CLI 输入 `$backend-delivery` 触发，Claude Code 输入 `/backend-delivery`。在 Codex Desktop 是否呈现快捷入口依版本而异，可在指令里直接点名本 Skill。需要 shell/仓库访问权限才能运行本地脚本和编辑项目。

## BrowserSkill 前提

此 Skill **调用已安装的 BrowserSkill**，并不包含 bsk 浏览器服务本体、插件或 Chrome 登录态。浏览器登录操作仍由用户授权；CLI + 浏览器扩展需要可连接。参考 https://github.com/Tencent/BrowserSkill 。先用 `bsk --version`、`bsk status` 自检；不连通时请补可读文档，不要让 AI 假装浏览成功。

## 典型语句

1. `使用 backend-delivery，分析这个需求网页：https://...，只做需求提取与模块排序，不改代码。项目 ID：sorting-optimization。`
2. `基于已经确认的需求和代码，生成技术方案，包括三张 Mermaid 图、接口设计、DDL（若需要）、技术选型；提交我确认前不要编码。`
3. `技术方案 v1.0 我批准。现在只生成 device-statistics 模块的实施计划，列出将修改的文件，先不要动代码。`
4. `批准 device-statistics 模块计划 v1.0，按计划编码并完成本模块测试。`
5. `所有模块已完成，执行全量回归并输出真实测试记录、每个接口请求/响应示例和问题清单；测不到的标 BLOCKED。`
6. `根据 BUG-001 到 BUG-003，先分析根因和修复影响，再最小范围修复和回归；涉及方案变更先征求批准。`
7. `恢复项目 sorting-optimization，读取 docs/ai-delivery/sorting-optimization 的状态，告诉我可合法执行的下一步。`

## 可选初始化 / 校验（Python 3.9+，仅标准库）

```powershell
python "<skill路径>\scripts\init_project.py" --repo "C:\code\my-service" --project "sorting-optimization"
python "<skill路径>\scripts\init_project.py" --repo "C:\code\my-service" --project "sorting-optimization" --module "device-statistics"
python "<skill路径>\scripts\validate_docs.py" --repo "C:\code\my-service" --project "sorting-optimization"
```

脚本不会调用 BrowserSkill/生成业务代码/自动写 APPROVED，文档初始化**不会覆盖**已有文件；校验仅检查必需模板与章节结构，不能代替架构审查、SQL 审查或真机测试。项目 ID 和模块 ID 为小写字母/数字/连字符。
