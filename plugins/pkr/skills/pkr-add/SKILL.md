---
name: pkr-add
description: >
  This skill should be used when the user asks to "add capability",
  "register convention", "add PKR doc", "manual register",
  "pkr add", "plan capability", or mentions manually adding knowledge registry entries.
argument-hint: "[plan] [name] <description>"
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion, Glob, Grep, mcp__codegraph__*]
disable-model-invocation: true
---

# PKR Add — 手动注册项目知识

手动注册 Capability 或 Convention 文档。支持两种模式：从代码/框架扫描注册，或注册为计划中能力。

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
| `import` | 导入坐标（Maven GAV / npm 包路径 / 模块路径等） |

**条件字段（根据 source 类型选填）：**

| source 类型 | 额外字段 | 用途 |
|------------|---------|------|
| `项目自有` | `symbols` | 关联的代码符号列表（类名、函数名等，用于定位源码） |
| `项目自有` | `content_hash` | 所有关联文件按路径排序拼接后的内容 hash（用于 sync 变更检测） |
| `框架:xxx` | `framework_version` | 依赖版本号（用于 sync 时对比依赖版本是否变化） |
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

## 命令路由

根据第一个参数选择模式：

| 命令格式 | 模式 | 说明 |
|----------|------|------|
| `/pkr-add <name> <description>` | A — 代码扫描注册（指定名称） | 从代码或框架中查找能力，生成已实现文档 |
| `/pkr-add <description>` | A — 代码扫描注册（自动生成名称） | 扫描后从代码中提取名称 |
| `/pkr-add plan <name> <description>` | B — 计划注册（指定名称） | 不扫描代码，直接生成计划中文档 |
| `/pkr-add plan <description>` | B — 计划注册（自动生成名称） | 从描述中提取名称 |

- 第一个参数为 `plan` → 模式 B
- 其他 → 模式 A

### 自动生成名称规则

当用户未指定 `name` 时，按以下优先级生成英文短横线格式名称：

**模式 A（代码扫描）**：
1. 从扫描到的主类/主文件提取：`RetryEngine` → `retry-engine`，`EventBus` → `event-bus`
2. 若扫描到多个候选，取最具代表性的类名
3. 生成后展示给用户确认，用户可修改

**模式 B（计划注册）**：
1. 从 description 中提取核心名词短语，转为英文短横线格式
2. 例："基于 Drools 的业务规则引擎" → `rule-engine`
3. 例："引入 RocketMQ 作为消息中间件" → `message-queue`
4. 生成后展示给用户确认，用户可修改

---

## 模式 A — 代码扫描注册

从项目代码或三方框架中扫描查找能力，生成 `status: 已实现` 的文档。

### 典型场景

| 场景 | source |
|------|--------|
| 扫描没发现但项目中确实存在的能力 | 项目自有 |
| 速查表中未收录的三方框架能力 | 框架:xxx |
| 扫描遗漏的规范/约定 | 项目自有 |

### 用法

```
# 指定名称
/pkr-add retry-engine "项目自有的重试引擎，支持指数退避和最大重试次数配置"
/pkr-add spring-cache "Spring Cache 的声明式缓存能力"

# 自动生成名称（从代码中提取）
/pkr-add "项目自有的重试引擎，支持指数退避和最大重试次数配置"
/pkr-add "项目的事件总线，基于 Guava EventBus 封装"
```

- `[name]`（可选）：英文短横线格式名称，未提供时从扫描到的代码自动提取
- `<description>`（必填）：描述能力的核心功能，指导扫描方向

### 工作流程

1. **解析参数**：提取 `name`（可选）和 `description`
2. **判断来源类型**：
   - 对照 `${CLAUDE_PLUGIN_ROOT}/shared/references/framework-capabilities.md` 检查是否为已知三方框架
   - 若匹配到框架 → `source = 框架:{框架名}`
   - 若未匹配 → `source = 项目自有`
3. **按 source 定向扫描**：

   **source=项目自有：**
   - 根据 `name` 和 `description` 在代码中搜索相关类/文件
   - 搜索策略：按名称模式（`*{Name}*`、`*{name}*`）搜索，结合 description 中的关键词
   - 分析找到的源码，提取：
     - 公开 API（方法签名、参数、返回值）
     - 配置方式（构造函数、注解、配置文件）
     - 依赖关系
   - 记录 `import` 导入坐标：
     - **Java**：从 `pom.xml` / `build.gradle` 读取能力所在模块的 GAV（`groupId:artifactId`）
     - **Node/TS**：从 `package.json` 读取包名
     - **Python**：从 `pyproject.toml` / `setup.py` 读取包名
     - **Go**：从 `go.mod` 读取模块路径
     - **Rust**：从 `Cargo.toml` 读取 crate 名
   - 记录 `symbols`（关联的代码符号列表：类名、函数名等）
   - 记录 `content_hash`（将所有关联文件按路径排序拼接，归一化行尾后计算 SHA-256）：
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/compute_content_hash.py" <file1> <file2> ...
     ```
     脚本内部自动按路径字典序排序，无需手动排序参数

   **source=框架:xxx：**
   - 从依赖声明文件（pom.xml / package.json 等）读取版本号
   - 根据 description 和框架文档，整理该框架提供的核心能力
   - 记录 `import`：框架的依赖坐标（如 `org.springframework:spring-context`）
   - 记录 `framework_version`

4. **用 AskUserQuestion 确认信息**：
   - 若未提供 name：展示自动生成的名称，用户可修改
   - 展示扫描结果摘要
   - 确认类型：Capability / Convention
   - 确认 scope：前端 / 后端 / 全栈
   - 用户可修正 source 判断（如项目自有 vs 框架）

5. **生成文档**：
   - `name`：用户提供或从代码自动提取的名称
   - 读取对应模板
   - 用扫描结果填充"如何使用"和"使用实例"
   - 写入 `docs/capabilities/` 或 `docs/conventions/`

---

## 模式 B — 计划注册

不扫描代码，基于用户描述生成 `status: 计划中` 的文档。

### 典型场景

| 场景 | source |
|------|--------|
| 计划开发但代码尚未实现的能力 | 计划 |
| PRD/ROADMAP 中规划的功能 | 计划 |
| 团队讨论后决定要引入的框架能力 | 计划 |

### 用法

```
# 指定名称
/pkr-add plan rule-engine "基于 Drools 的业务规则引擎，支持规则定义、条件匹配和动作执行"
/pkr-add plan design-token-v2 "升级版 Design Token 体系，支持暗黑主题和多品牌切换"

# 自动生成名称（从描述中提取）
/pkr-add plan "引入 RocketMQ 作为消息中间件，支持异步解耦和削峰填谷"
/pkr-add plan "基于 Drools 的业务规则引擎"
```

- `plan`（必填）：路由关键词，标识为计划注册模式
- `[name]`（可选）：英文短横线格式名称，未提供时从描述中自动提取
- `<description>`（必填）：描述计划中的能力/规范的核心功能和预期设计

### 工作流程

1. **解析参数**：提取 `name`（可选）和 `description`
2. **若未提供 name**：从 description 中提取核心名词短语，转为英文短横线格式（如"业务规则引擎" → `rule-engine`），展示给用户确认
3. **用 AskUserQuestion 收集补充信息**：
   - 确认类型：Capability / Convention
   - 确认 scope：前端 / 后端 / 全栈
   - 预期实现方式或技术选型（可选）
   - 预计依赖或前置条件（可选）
4. **生成文档**：
   - `name`：用户提供或自动生成的名称
   - `status: 计划中`
   - `source: 计划`
   - `import`：预期导入坐标（根据技术选型推断，如计划引入 Drools 则填 `org.drools:drools-core`）
   - 无条件字段（无 `content_hash`、`symbols`、`framework_version`）
   - "解决什么问题"：基于 description 展开
   - "如何使用"：描述预期的 API 设计和使用方式（标注为"预期设计，待实现"）
   - "使用实例"：描述预期的使用场景和伪代码示例（标注为"预期示例，待实现"）
5. **写入文档**：写入 `docs/capabilities/` 或 `docs/conventions/`

---

## 反模式（禁止行为）

1. **禁止跳过用户确认**：模式 A 的扫描结果和类型/scope 必须经用户确认
2. **禁止凭空推断**：模式 A 的文档内容必须基于代码事实，不得编造 API
3. **禁止删除文档**：只标记 `已废弃`，不删除文件
4. **禁止覆盖人工编辑**：更新已有文档时必须保留无法从代码推导的内容
5. **禁止全量加载**：不要一次读取所有源码文件，按需读取
6. **禁止模式 B 扫描代码**：计划模式不扫描代码，内容完全基于用户描述
