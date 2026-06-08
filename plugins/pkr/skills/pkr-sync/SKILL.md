---
name: pkr-sync
description: >
  This skill should be used when the user asks to "sync PKR docs",
  "synchronize project knowledge", "check all PKR docs",
  "pkr sync", or mentions full synchronization of knowledge registry.
argument-hint: ""
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion, Glob, Grep, mcp__codegraph__*]
disable-model-invocation: true
---

# PKR Sync — 全量同步项目知识库

扫描所有现有 PKR 文档，与代码/依赖现状对比，智能检测变更后批量更新。

## 文档存储位置

- Capability 文档 → `docs/capabilities/[{module}/]{name}.md`
- Capability 索引 → `docs/capabilities/index.md`（由脚本自动维护）
- Convention 文档 → `docs/conventions/[{module}/]{name}.md`
- Convention 索引 → `docs/conventions/index.md`（由脚本自动维护）

## 文档格式

生成文档前，先读取对应模板：
- Capability → `${CLAUDE_PLUGIN_ROOT}/shared/templates/capability.md`
- Convention → `${CLAUDE_PLUGIN_ROOT}/shared/templates/convention.md`

YAML Front Matter 字段：

**必填字段：**

| 字段 | 说明 |
|------|------|
| `name` | 名称，格式 `[module/]short-name`（如 `workflow-engine` 或 `springboot/cache`） |
| `description` | 一句话描述 |
| `status` | `计划中` / `已实现` / `已废弃` |
| `scope` | `前端` / `后端` / `全栈` |
| `source` | `项目自有` / `框架:{框架名}` / `计划` |
| `import` | 导入坐标（Maven GAV / npm 包路径 / 模块路径等） |

**可选字段：**

| 字段 | 说明 |
|------|------|
| `module` | 模块名（由子目录自动推导） |

**条件字段（根据 source 类型选填）：**

| source 类型 | 额外字段 | 用途 |
|------------|---------|------|
| `项目自有` | `symbols` | 关联的代码符号列表（类名、函数名等，用于定位源码） |
| `项目自有` | `content_hash` | 所有关联文件按路径排序拼接后的内容 hash（用于变更检测） |
| `框架:xxx` | `framework_version` | 依赖版本号（用于对比依赖版本是否变化） |
| `计划` | 无额外字段 | sync 时忽略计划中的文档 |

正文三个必含章节：**解决什么问题** / **如何使用** / **使用实例**

## 脚本使用约定

- **执行方式**：通过 Bash 直接执行，使用 `${CLAUDE_PLUGIN_ROOT}` 定位脚本绝对路径
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rebuild_pkr_index.py"
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/compute_content_hash.py" <file1> [file2] ...
  ```
- **禁止 Read+stdin**：不需要先 Read 脚本源码再管道执行，直接 python3 调用即可

## 代码分析工具

如果本地已安装 CodeGraph MCP，**优先使用** CodeGraph 进行代码分析（`codegraph_search` / `codegraph_explore` / `codegraph_callers`）；未安装时降级到 Bash + Grep/Glob。

---

## 工作流程

### 步骤 1：加载现有文档

递归读取 `docs/capabilities/` 和 `docs/conventions/` 下所有 `.md` 文件（含子目录，排除各级 index.md），解析 frontmatter。

### 步骤 2：扫描代码/依赖现状

执行与 init 相同的扫描流程：

1. **识别技术栈**：扫描项目根目录判断技术栈（pom.xml → Java, package.json → Node/TS, 等）
2. **扫描项目自有能力**：按命名模式搜索候选类/接口，应用筛选规则
3. **扫描项目自有规范**：按代码模式搜索候选 Convention
4. **扫描三方框架能力**：读取依赖声明文件，对照 `${CLAUDE_PLUGIN_ROOT}/shared/references/framework-capabilities.md` 匹配已知框架

### 步骤 3：对比差异（智能变更检测）

对每篇现有文档，根据 `source` 采用不同的检测策略：

**source=项目自有：**
- 在代码中查找对应的类/文件是否仍存在
- 若不存在：标记为 `已废弃`
- 若存在：**使用内容 hash 检测变更**
  - 根据 frontmatter 中的 `symbols` 列表，通过 CodeGraph 或 grep 定位符号所在的源文件
  - 计算当前内容 hash（将所有关联文件按路径排序拼接，归一化行尾后计算 SHA-256）：
    ```bash
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/compute_content_hash.py" <file1> <file2> ...
    ```
    脚本内部自动按路径字典序排序，无需手动排序参数
  - 对比 frontmatter 中的 `content_hash` 字段
  - 若 hash 相同 → **跳过**（代码内容未变化）
  - 若 hash 不同 → 重新分析代码并更新文档
  - 更新后写入新的 `content_hash` 值

**source=框架:**
- 检查依赖是否仍存在
- 若不存在：标记为 `已废弃`
- 若存在：**对比依赖版本号**
  - 从依赖声明文件（pom.xml/package.json 等）读取当前版本
  - 对比 frontmatter 中的 `framework_version` 字段
  - 若版本相同 → **跳过**（依赖未变化）
  - 若版本不同 → 更新文档并写入新版本号

**source=计划：**
- **完全忽略**（计划中的能力不需要 sync）

### 步骤 4：幂等合并更新

对需要更新的文档：

**事实性内容（以代码为准）：**
- "如何使用"章节 — 更新 API 签名、配置方式
- "使用实例"章节 — 更新代码示例

**人工编辑（逐字保留）：**
- 任何无法从代码推导的内容（注意事项、最佳实践等）

**冲突处理：**
- 代码事实与文档冲突 → 以代码为准
- 在文档末尾追加变更记录：`> 🔄 最后更新: {日期} — {变更摘要}`

### 步骤 5：展示变更摘要

列出本次 sync 的变更：
- 新增 N 个文档
- 更新 N 个文档
- 标记 N 个文档为已废弃
- 跳过 N 个文档（无变化）

---

## 反模式（禁止行为）

1. **禁止跳过用户确认**：新增候选必须经用户确认后才生成文档
2. **禁止凭空推断**：文档内容必须基于代码事实或用户提供的信息，不得编造 API
3. **禁止删除文档**：只标记 `已废弃`，不删除文件
4. **禁止覆盖人工编辑**：必须保留无法从代码推导的内容
5. **禁止全量加载**：不要一次读取所有源码文件，按需读取
