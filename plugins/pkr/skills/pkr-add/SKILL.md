---
name: pkr-add
description: >
  This skill should be used when the user asks to "add capability",
  "register convention", "add PKR doc", "manual register",
  "pkr add", or mentions manually adding knowledge registry entries.
argument-hint: ""
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion, Glob, Grep, mcp__codegraph__*]
disable-model-invocation: true
---

# PKR Add — 手动注册项目知识

通用的手动入口，通过交互式问答收集信息，按模板生成 PKR 文档。用于补漏和扩展。

## 文档存储位置

- Capability 文档 → `docs/capabilities/{name}.md`
- Capability 索引 → `docs/capabilities/index.md`（由脚本自动维护）
- Convention 文档 → `docs/conventions/{name}.md`
- Convention 索引 → `docs/conventions/index.md`（由脚本自动维护）

## 文档格式

生成文档前，先读取对应模板：
- Capability → `${CLAUDE_PLUGIN_ROOT}/shared/templates/capability.md`
- Convention → `${CLAUDE_PLUGIN_ROOT}/shared/templates/convention.md`

YAML Front Matter 字段：

**必填字段：**

| 字段 | 说明 |
|------|------|
| `name` | 英文短横线格式名称（如 `workflow-engine`） |
| `description` | 一句话描述 |
| `status` | `计划中` / `已实现` / `已废弃` |
| `scope` | `前端` / `后端` / `全栈` |
| `source` | `项目自有` / `框架:{框架名}` / `计划` |

**条件字段（根据 source 类型选填）：**

| source 类型 | 额外字段 | 用途 |
|------------|---------|------|
| `项目自有` | `last_commit` | 关联源码的最后一次 git commit hash（用于 sync 变更检测） |
| `项目自有` | `code_files` | 关联的源码文件列表（用于 sync 时定位 git 变更） |
| `框架:xxx` | `framework_version` | 依赖版本号（用于 sync 时对比依赖版本是否变化） |
| `计划` | 无额外字段 | sync 时忽略计划中的文档 |

正文三个必含章节：**解决什么问题** / **如何使用** / **使用实例**

## 脚本使用约定

- **执行方式**：通过 Bash 直接执行，使用 `${CLAUDE_PLUGIN_ROOT}` 定位脚本绝对路径
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rebuild_pkr_index.py"
  ```
- **禁止 Read+stdin**：不需要先 Read 脚本源码再管道执行，直接 python3 调用即可

## 代码分析工具

如果本地已安装 CodeGraph MCP，**优先使用** CodeGraph 进行代码分析（`codegraph_search` / `codegraph_explore` / `codegraph_callers`）；未安装时降级到 Bash + Grep/Glob。

---

## 典型场景

| 场景 | status | source |
|------|--------|--------|
| 扫描没发现但项目中确实存在的能力 | 已实现 | 项目自有 |
| 计划开发但代码尚未实现的能力 | 计划中 | 计划 |
| 速查表中未收录的三方框架能力 | 已实现 | 框架:xxx |
| 扫描遗漏的规范/约定 | 已实现 | 项目自有 |

## 工作流程

1. 用户提供名称或简要描述
2. 用 AskUserQuestion 交互收集：
   - **名称**（英文短横线格式）
   - **描述**（一句话）
   - **类型**：Capability / Convention
   - **scope**：前端 / 后端 / 全栈
   - **source**：项目自有 / 框架 / 计划
   - **status**：已实现 / 计划中 — **用户自选，不预设**
3. 若 status=已实现：
   - 询问用户代码位置（类名/文件路径）
   - 分析源码，自动填充"如何使用"和"使用实例"
4. 若 status=计划中：
   - 收集预期设计和规划信息
5. 按模板生成文档，写入对应目录

---

## 反模式（禁止行为）

1. **禁止跳过用户确认**：必须经用户确认后才生成文档
2. **禁止凭空推断**：文档内容必须基于代码事实或用户提供的信息，不得编造 API
3. **禁止删除文档**：只标记 `已废弃`，不删除文件
4. **禁止覆盖人工编辑**：必须保留无法从代码推导的内容
5. **禁止全量加载**：不要一次读取所有源码文件，按需读取
