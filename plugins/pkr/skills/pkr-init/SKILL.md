---
name: pkr-init
description: >
  This skill should be used when the user asks to "scan project knowledge",
  "build PKR docs", "discover capabilities", "discover conventions",
  "pkr init", "initialize PKR", or mentions first-time project knowledge setup.
argument-hint: ""
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion, Glob, Grep, mcp__codegraph__*]
disable-model-invocation: true
---

# PKR Init — 首次构建项目知识库

扫描项目代码、依赖和规划文档，发现候选的 Capability（能力）和 Convention（规范），由用户确认后生成 PKR 文档。

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

## 项目初始化

首次使用前，需执行初始化脚本配置目标项目：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkr_setup.py"
```

该脚本会：
1. 创建 `docs/capabilities/` 和 `docs/conventions/` 目录
2. 在项目的 `CLAUDE.md` 中添加 PKR 知识查阅约束（幂等，不会重复添加）

---

## 工作流程

### 阶段 1：识别项目技术栈

扫描项目根目录判断技术栈：
- 存在 `pom.xml` 或 `build.gradle` → Java
- 存在 `package.json` → Node/TS
- 存在 `requirements.txt` 或 `pyproject.toml` → Python
- 存在 `go.mod` → Go
- 存在 `Cargo.toml` → Rust

### 阶段 2：扫描项目自有能力（Capability）

按命名模式搜索候选类/接口（排除测试目录）。

**搜索的命名模式**：

- **Java**：`*Engine`, `*Bus`, `*Lock`, `*Registry`, `*Dispatcher`, `*Scheduler`, `*Factory`, `*Gateway`, `*Proxy`, `*Adapter`, `*Strategy`, `*Template`
- **TS/JS**：同上 + `*Manager`（非业务类）
- **Python**：`*_engine`, `*_bus`, `*_lock`, `*_registry`, `*_dispatcher`, `*_scheduler`, `*_factory`, `*_gateway`, `*_proxy`, `*_adapter`, `*_strategy`

**筛选规则**：

1. 排除业务类（Controller、Service、Repository、DAO、DTO、VO、Entity、Model）
2. 排除测试类
3. 优先关注：有接口+实现的类、被多处引用的工具类
4. 对每个候选，检查引用次数 — 引用 ≥ 3 次优先

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
3. 对照 `${CLAUDE_PLUGIN_ROOT}/shared/references/framework-capabilities.md` 匹配已知框架
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
4. **根据 source 类型写入条件字段**：
   - **source=项目自有** → 记录 `last_commit` 和 `code_files`
     ```bash
     git log -1 --format=%h -- <关联的源码文件>
     ```
   - **source=框架:xxx** → 从依赖声明文件读取并记录 `framework_version`
   - **source=计划** → 无需额外字段
5. Write 到 `docs/capabilities/` 或 `docs/conventions/`
6. 文件名 = `name` 字段值（英文短横线格式）+ `.md`

---

## 反模式（禁止行为）

1. **禁止跳过用户确认**：候选清单必须经用户确认后才生成文档
2. **禁止凭空推断**：文档内容必须基于代码事实或用户提供的信息，不得编造 API
3. **禁止删除文档**：只标记 `已废弃`，不删除文件
4. **禁止覆盖人工编辑**：必须保留无法从代码推导的内容
5. **禁止全量加载**：不要一次读取所有源码文件，按需读取
