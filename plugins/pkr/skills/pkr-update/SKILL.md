---
name: pkr-update
description: >
  This skill should be used when the user asks to "update PKR doc",
  "refresh capability doc", "update convention",
  "pkr update", or mentions updating a specific knowledge registry document.
argument-hint: "<name> [description]"
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion, Glob, Grep, mcp__codegraph__*]
disable-model-invocation: true
---

# PKR Update — 单项更新项目知识文档

针对单个已注册的 Capability 或 Convention 文档，重新扫描代码并更新。

## 文档存储位置

- Capability 文档 → `docs/capabilities/{module}/{name}.md`（所有文档必须在模块子目录下）
- Capability 索引 → `docs/capabilities/index.md`（由脚本自动维护）
- Convention 文档 → `docs/conventions/{module}/{name}.md`
- Convention 索引 → `docs/conventions/index.md`（由脚本自动维护）

## 文档格式

更新文档时，保持与模板一致的格式：
- Capability → `${CLAUDE_PLUGIN_ROOT}/shared/templates/capability.md`
- Convention → `${CLAUDE_PLUGIN_ROOT}/shared/templates/convention.md`

YAML Front Matter 字段：

**必填字段：**

| 字段 | 说明 |
|------|------|
| `name` | 名称，格式 `module/short-name`（如 `myapp/workflow-engine`、`springboot/cache`） |
| `module` | 模块名（与子目录名一致。项目自有用项目模块名，框架用框架名） |
| `description` | 一句话描述 |
| `status` | `计划中` / `已实现` / `已废弃` |
| `scope` | `前端` / `后端` / `全栈` |
| `source` | `项目自有` / `框架:{框架名}` / `计划` |
| `import` | 导入坐标（Maven GAV / npm 包路径 / 模块路径等） |

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

## 用法

```
/pkr-update workflow-engine
/pkr-update springboot/cache
/pkr-update workflow-engine "新增了重试机制和超时配置"
/pkr-update springboot/cache "升级到 Caffeine 3.x"
```

- `<name>`（必填）：对应文档 frontmatter 中的 `name` 字段值，支持 `module/name` 格式
- `[description]`（可选）：用户提供的更新提示，描述本次变更的重点内容

## 工作流程

1. **定位文档**：在 `docs/capabilities/` 和 `docs/conventions/` 的子目录中查找 `{short-name}.md`
   - `<name>` 必须为 `module/short-name` 格式（如 `springboot/cache`）→ 查找 `{module}/{short-name}.md`
   - 递归搜索所有子目录匹配 short-name
   - 若找不到 → 提示用户该文档不存在，建议用 `/pkr-add` 新建
2. **读取文档**：解析 frontmatter，获取 `source`、`status` 和条件字段
3. **按 source 定向扫描**：
   - **source=项目自有** → 根据 `symbols` 列表在代码中定位符号所在文件，分析当前 API
     - 若提供了 `description`：重点关注描述中提到的功能点（如新增的 API、配置项）
   - **source=框架:xxx** → 检查依赖是否仍存在，对比 `framework_version`
     - 若提供了 `description`：结合描述更新框架使用方式
   - **source=计划** → 检查代码中是否已实现该能力
     - 若已实现：提示升级为 `已实现`，并补充实现细节
4. **幂等合并更新**：
   - **事实性内容（以代码为准）**：更新 API 签名、配置方式、代码示例
   - **人工编辑（逐字保留）**：任何无法从代码推导的内容（注意事项、最佳实践等）
   - **冲突处理**：代码事实与文档冲突 → 以代码为准
   - 若提供了 `description`：确保文档内容体现了描述中提到的变更
5. **更新 frontmatter 条件字段**：
   - `source=项目自有` → 将所有关联文件按路径排序拼接，归一化行尾后计算 hash，更新 `content_hash`：
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/compute_content_hash.py" <file1> <file2> ...
     ```
   - `source=框架:xxx` → 更新 `framework_version` 为当前版本
6. **追加变更记录**：
   - 格式：`> 🔄 最后更新: {日期} — {变更摘要}`
   - 若提供了 `description`：使用 description 作为变更摘要
   - 若未提供：根据实际扫描结果生成摘要

## 与 sync 的区别

| | `/pkr-sync` | `/pkr-update <name> [description]` |
|---|---|---|
| 范围 | 全部文档 | 单个文档 |
| 变更检测 | 自动（content hash / 版本号） | 自动 + 可选手动提示 |
| 速度 | 慢（全量扫描） | 快（定向分析） |
| 适用场景 | 定期全量同步 | 改了某个能力后立即更新 |
| description 参数 | 不支持 | 支持（指导更新重点） |

---

## 反模式（禁止行为）

1. **禁止跳过用户确认**：如需新增文档，必须经用户确认
2. **禁止凭空推断**：文档内容必须基于代码事实或用户提供的信息，不得编造 API
3. **禁止删除文档**：只标记 `已废弃`，不删除文件
4. **禁止覆盖人工编辑**：必须保留无法从代码推导的内容
5. **禁止全量加载**：不要一次读取所有源码文件，按需读取
