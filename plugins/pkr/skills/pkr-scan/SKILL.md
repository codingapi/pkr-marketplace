---
name: pkr-scan
description: >
  This skill should be used when the user asks to "scan project knowledge",
  "build PKR docs", "discover capabilities", "discover conventions",
  "update PKR", "add capability", "register convention",
  "pkr", or mentions project knowledge registry.
argument-hint: "[init|sync|update <name>|add]"
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion, Glob, Grep]
disable-model-invocation: true
---

# PKR Scan — 项目知识注册中心扫描工具

扫描项目代码、依赖和规划文档，发现并注册 Capability（能力）和 Convention（规范）。

## 文档存储位置

- Capability 文档 → `docs/capabilities/{name}.md`
- Capability 索引 → `docs/capabilities/index.md`（由脚本自动维护）
- Convention 文档 → `docs/conventions/{name}.md`
- Convention 索引 → `docs/conventions/index.md`（由脚本自动维护）

## 文档格式

生成文档前，先读取对应模板：
- Capability → `./templates/capability.md`
- Convention → `./templates/convention.md`

YAML Front Matter 字段：

| 字段 | 说明 |
|------|------|
| `name` | 英文短横线格式名称（如 `workflow-engine`） |
| `description` | 一句话描述 |
| `status` | `计划中` / `已实现` / `已废弃` |
| `scope` | `前端` / `后端` / `全栈` |
| `source` | `项目自有` / `框架:{框架名}` / `计划` |

正文三个必含章节：**解决什么问题** / **如何使用** / **使用实例**

## 脚本使用约定

- **引用方式**：SKILL.md 中通过相对 markdown link 引用脚本
  [./scripts/rebuild_pkr_index.py](./scripts/rebuild_pkr_index.py)
- **执行方式**：通过 Bash 直接执行，使用 `${CLAUDE_PLUGIN_ROOT}` 定位脚本绝对路径
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/skills/pkr-scan/scripts/rebuild_pkr_index.py"
  ```
- **禁止 Read+stdin**：不需要先 Read 脚本源码再管道执行，直接 python3 调用即可

## 项目初始化

首次使用前，需执行初始化脚本配置目标项目：

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/pkr-setup.sh"
```

该脚本会：
1. 创建 `docs/capabilities/` 和 `docs/conventions/` 目录
2. 在项目的 `CLAUDE.md` 中添加 PKR 知识查阅约束（幂等，不会重复添加）

## 命令模式

根据用户传入的参数选择工作流：
- `init` 或无参数且 `docs/capabilities/` 为空 → 模式 A
- `sync` → 模式 B（全量同步）
- `update <name>` → 模式 C（单项更新）
- `add` → 模式 D
- 无参数且已有文档 → 询问用户选择 init 还是 sync

---

## 模式 A — `init`（首次构建）

### 阶段 1：识别项目技术栈

扫描项目根目录判断技术栈：
- 存在 `pom.xml` 或 `build.gradle` → Java
- 存在 `package.json` → Node/TS
- 存在 `requirements.txt` 或 `pyproject.toml` → Python
- 存在 `go.mod` → Go
- 存在 `Cargo.toml` → Rust

### 阶段 2：扫描项目自有能力（Capability）

按命名模式搜索候选类/接口（排除测试目录）：

**Java 模式**：
```
*Engine, *Bus, *Lock, *Registry, *Dispatcher, *Scheduler,
*Factory, *Gateway, *Proxy, *Adapter, *Strategy, *Template
```

**TS/JS 模式**：
```
*Engine, *Bus, *Lock, *Registry, *Dispatcher, *Scheduler,
*Factory, *Gateway, *Proxy, *Adapter, *Strategy, *Manager（非业务类）
```

**Python 模式**：
```
*_engine, *_bus, *_lock, *_registry, *_dispatcher, *_scheduler,
*_factory, *_gateway, *_proxy, *_adapter, *_strategy
```

筛选规则：
1. 排除业务类（Controller、Service、Repository、DAO、DTO、VO、Entity、Model）
2. 排除测试类
3. 优先关注：有接口+实现的类、被多处引用的工具类
4. 对每个候选，用 Grep 检查引用次数 — 引用 ≥ 3 次优先

### 阶段 3：扫描项目自有规范（Convention）

按代码模式搜索候选 Convention：

| 规范类型 | 搜索模式 |
|----------|----------|
| Design Token | CSS 变量定义文件（`--color-`, `--spacing-`, `--font-`）|
| 状态管理 | Redux/Zustand/Pinia store 文件 |
| 请求封装 | axios/fetch 封装层 |
| 事件规范 | EventPublisher / EventBus 使用模式 |
| 异常处理 | 全局异常处理器 |
| 日志规范 | 日志格式配置 |

### 阶段 4：扫描三方框架能力

1. 读取依赖声明文件（`pom.xml` / `package.json` / `requirements.txt` 等）
2. 提取依赖列表
3. 对照 `./references/framework-capabilities.md` 匹配已知框架
4. 列出每个匹配框架提供的核心能力

### 阶段 5：扫描计划中能力

1. 扫描项目根目录下的规划文档：
   - `PRD.md`, `ROADMAP.md`, `TODO.md`, `PLAN.md`
   - `docs/plan/`, `.github/`
2. 提取文档中提及的能力关键词
3. 与已扫描到的代码能力对比 — 代码中不存在的标记为候选 Planned Capability

### 阶段 6：汇总候选，用户确认

用 AskUserQuestion 分组展示候选清单：

```
📦 项目自有能力（N 个候选）：
  1. WorkflowEngine — 工作流引擎（引用 12 次）
  2. EventBus — 事件总线（引用 8 次）
  ...

📚 三方框架能力（N 个候选）：
  1. spring-context → Spring IoC 容器
  2. spring-boot-starter-cache → Spring Cache 声明式缓存
  ...

🗓️ 计划中能力（N 个候选）：
  1. Rule Engine — PRD.md 中提及
  ...
```

用户可逐个确认或批量确认。

### 阶段 7：逐个生成文档

对每个确认项：
1. Read 对应模板文件
2. 分析源码/依赖/规划文档，提取信息
3. 按模板填充内容
4. Write 到 `docs/capabilities/` 或 `docs/conventions/`
5. 文件名 = `name` 字段值（英文短横线格式）+ `.md`

---

## 模式 B — `sync`（全量同步）

扫描所有现有文档，与代码/依赖现状对比，批量更新。

### 步骤 1：加载现有文档

读取 `docs/capabilities/` 和 `docs/conventions/` 下所有 `.md` 文件（排除 index.md），解析 frontmatter。

### 步骤 2：扫描代码/依赖现状

执行与模式 A 相同的阶段 1-4 扫描。

### 步骤 3：对比差异

对每篇现有文档：

**source=项目自有：**
- 在代码中查找对应的类/文件是否仍存在
- 若存在：检查 API 签名是否变化
- 若不存在：标记为 `已废弃`

**source=框架:**
- 检查依赖是否仍存在
- 若不存在：标记为 `已废弃`

**source=计划：**
- 检查代码中是否已实现
- 若已实现：提示升级为 `已实现`

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

## 模式 C — `update <name>`（单项更新）

针对单个已注册的能力或规范文档，重新扫描代码并更新。

### 用法

```
/pkr-scan update workflow-engine
/pkr-scan update design-token
```

`<name>` 对应文档 frontmatter 中的 `name` 字段值。

### 工作流

1. **定位文档**：在 `docs/capabilities/` 和 `docs/conventions/` 中查找 `{name}.md`
   - 若找不到 → 提示用户该文档不存在，建议用 `add` 新建
2. **读取文档**：解析 frontmatter，获取 `source` 和 `status`
3. **按 source 定向扫描**：
   - **source=项目自有** → 在代码中定位对应的类/文件，分析当前 API
   - **source=框架:xxx** → 检查依赖是否仍存在，查阅框架文档
   - **source=计划** → 检查代码中是否已实现该能力
4. **幂等合并更新**（同模式 B 步骤 4）
5. **追加变更记录**

### 与 sync 的区别

| | `sync` | `update <name>` |
|---|---|---|
| 范围 | 全部文档 | 单个文档 |
| 速度 | 慢（全量扫描） | 快（定向分析） |
| 适用场景 | 定期全量同步 | 改了某个能力后立即更新 |

---

## 模式 D — `add`（手动注册/补漏）

扫描不可能覆盖所有情况，此模式是通用的手动入口。

### 典型场景

| 场景 | status | source |
|------|--------|--------|
| 扫描没发现但项目中确实存在的能力 | 已实现 | 项目自有 |
| 计划开发但代码尚未实现的能力 | 计划中 | 计划 |
| 速查表中未收录的三方框架能力 | 已实现 | 框架:xxx |
| 扫描遗漏的规范/约定 | 已实现 | 项目自有 |

### 工作流

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

1. **禁止跳过用户确认**：init 模式下，候选清单必须经用户确认后才生成文档
2. **禁止凭空推断**：文档内容必须基于代码事实或用户提供的信息，不得编造 API
3. **禁止删除文档**：sync/update 时只标记 `已废弃`，不删除文件
4. **禁止覆盖人工编辑**：sync/update 时必须保留无法从代码推导的内容
5. **禁止全量加载**：不要一次读取所有源码文件，按需读取
