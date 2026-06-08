# pkr-marketplace

面向 Claude Code 的 **项目知识注册中心（PKR）** 插件市场。扫描项目代码，自动发现并注册可复用能力（Capability）和开发规范（Convention），让 AI 在编码前知道项目已有什么、该怎么做。

## 什么是 PKR？

**PKR** 是 **Project Knowledge Registry**（项目知识注册中心）的缩写。

它的核心理念是：**AI 编码前应该先了解项目已有什么**。

传统开发中，新成员入职会先看项目文档、问老员工"项目里有哪些工具类、用什么规范"。但在 AI 辅助编码场景下，Claude 虽然能读代码，却不知道：
- 项目已经有哪些可复用的能力（如 WorkflowEngine、EventBus）
- 项目有哪些必须遵循的开发规范（如 Design Token、事件发布规则）

**PKR 就是给 AI 准备的"项目知识库"**：
- 通过结构化文档记录项目的 **能力（Capability）** 和 **规范（Convention）**
- 在 AI 编码前自动注入这些知识到上下文
- 避免重复造轮子和违反规范

## 核心理念

```
代码源码 → 扫描发现 → Capability/Convention 文档 → AI 编码前查询
```

**解决两个核心问题：**

1. **重复造轮子** — AI 不知道项目已有 Workflow Engine，又写了一个
2. **违反规范** — AI 写死 `color: #1677ff` 而非使用 Design Token 变量

## 前置条件

- Claude Code CLI 已安装并登录
- Git 已初始化（`git init`）
- Python 3（用于索引重建脚本）

## 推荐配置：CodeGraph

**强烈推荐**安装 [CodeGraph](https://github.com/colbymchenry/codegraph)，可显著提升代码分析的速度和准确性。

## 快速开始

### 1. 安装插件

安装插件市场，首次需要
```bash
/plugin marketplace add git@github.com:codingapi/pkr-marketplace.git
```

安装pkr插件
```bash
/plugin install pkr@pkr-marketplace
```

### 2. 初始化项目

执行插件提供的初始化脚本，自动创建目录结构并配置 CLAUDE.md：

```bash
python3 "$CLAUDE_PLUGIN_ROOT/scripts/pkr_setup.py"
```

该脚本会：
- 创建 `docs/capabilities/` 和 `docs/conventions/` 目录
- 在项目的 `CLAUDE.md` 中添加 PKR 知识查阅约束（幂等，不会重复添加）

### 3. 首次扫描

```bash
/pkr-init
```

Claude 会扫描项目代码、依赖和规划文档，列出候选的能力和规范，由你确认后生成文档。

### 4. 日常维护

```bash
# 修改了某个能力后，立即更新对应文档
/pkr-update workflow-engine

# 带描述信息，指导更新重点
/pkr-update workflow-engine "新增了重试机制"

# 定期全量同步（检查所有文档与代码的一致性）
/pkr-sync

# 从代码中扫描注册（名称自动从代码提取）
/pkr-add "项目自有的重试引擎，支持指数退避"

# 注册计划中的能力（名称从描述提取）
/pkr-add plan "基于 Drools 的业务规则引擎"
```

## 命令详解

### `/pkr-init` — 首次构建

扫描项目代码、依赖声明和规划文档，发现候选知识：

| 来源 | 发现方式 | 示例 |
|------|----------|------|
| **项目自有能力** | 模式匹配扫描代码 | WorkflowEngine、EventBus |
| **三方框架能力** | 扫描依赖声明文件 | Spring Cache、Redisson Lock |
| **计划中能力** | 扫描 PRD/ROADMAP + 手动注册 | Rule Engine（规划中） |

扫描完成后会列出候选清单，由你逐个确认/排除，确认后自动生成文档。

### `/pkr-sync` — 全量同步

对比所有现有文档与代码/依赖现状，**智能检测变更**后批量更新：

- **项目自有**：通过 Git commit hash 检测关联源码是否变化，未变化则跳过
- **三方框架**：通过依赖版本号检测，版本未变则跳过
- **计划中**：完全忽略（计划中的能力不参与 sync）
- 新增的 → 提示添加
- 消失的 → 标记为 `已废弃`（不删除）
- 变更的 → 幂等合并（事实以代码为准，人工编辑保留）

### `/pkr-update <name> [description]` — 单项更新

针对单个已注册的能力或规范文档，重新扫描代码并更新：

```bash
# 仅更新文档
/pkr-update workflow-engine

# 带描述信息，指导更新重点
/pkr-update workflow-engine "新增了重试机制和超时配置"
/pkr-update design-token "添加了暗黑主题支持"
```

**参数说明**：
- `<name>`（必填）：文档名称（对应 frontmatter 中的 `name` 字段）
- `[description]`（可选）：变更描述，用于指导 Claude 重点关注哪些变化

**description 的作用**：
- 帮助 Claude 聚焦于你关心的变更点（如新增 API、配置项）
- 在变更记录中作为变更摘要
- 确保文档内容体现了描述中提到的功能

适用于修改了某个能力后立即更新对应文档，比全量 sync 更快。

### `/pkr-add [name] <description>` — 从代码注册

从项目代码或三方框架中扫描查找能力，生成 `已实现` 文档：

```bash
# 指定名称注册
/pkr-add retry-engine "项目自有的重试引擎，支持指数退避和最大重试次数"

# 自动生成名称（从扫描到的代码类名提取，如 RetryEngine → retry-engine）
/pkr-add "项目自有的重试引擎，支持指数退避"
/pkr-add "项目的事件总线，基于 Guava EventBus 封装"
```

**参数说明**：
- `[name]`（可选）：英文短横线格式名称，未提供时从代码自动提取
- `<description>`（必填）：描述能力功能，指导扫描方向

Claude 会自动判断来源是项目自有还是三方框架，扫描代码后展示结果供确认。

### `/pkr-add plan [name] <description>` — 计划注册

不扫描代码，基于描述生成 `计划中` 文档：

```bash
# 指定名称
/pkr-add plan rule-engine "基于 Drools 的业务规则引擎，支持规则定义和条件匹配"

# 自动生成名称（从描述提取核心名词，如"消息中间件" → message-queue）
/pkr-add plan "引入 RocketMQ 作为消息中间件，支持异步解耦"
/pkr-add plan "升级版 Design Token 体系，支持暗黑主题"
```

**参数说明**：
- `plan`（必填）：路由关键词，标识为计划注册
- `[name]`（可选）：英文短横线格式名称，未提供时从描述自动提取
- `<description>`（必填）：描述计划中能力的核心功能和预期设计

## 文档格式

每个 `.md` 文件使用统一格式：

```markdown
---
name: workflow-engine
description: 通用工作流引擎，支持流程定义、节点编排、状态流转
status: 已实现
scope: 后端
source: 项目自有
---

## 解决什么问题

该能力/规范解决的核心痛点。

## 如何使用

API 说明、配置方式、依赖说明。

## 使用实例

具体代码示例。
```

### 字段说明

**必填字段：**

| 字段 | 值 | 说明 |
|------|-----|------|
| `name` | 英文短横线格式 | 文档名称（与文件名一致） |
| `description` | 一句话 | 简要描述 |
| `status` | `已实现` / `计划中` / `已废弃` | 当前状态 |
| `scope` | `前端` / `后端` / `全栈` | 适用范围 |
| `source` | `项目自有` / `框架:{名称}` / `计划` | 知识来源 |
| `import` | Maven GAV / npm 包路径 / 模块路径 | 导入坐标（复用此能力时需要的依赖声明） |

**条件字段（sync 变更检测用）：**

| source 类型 | 字段 | 说明 |
|------------|------|------|
| `项目自有` | `symbols` | 关联的代码符号列表（类名、函数名等），用于定位源码 |
| `项目自有` | `content_hash` | 所有关联文件按路径排序拼接后的内容 hash，用于检测代码是否变化 |
| `框架:{名称}` | `framework_version` | 依赖版本号，用于检测依赖是否升级 |

## 目录结构（安装后）

安装插件并执行初始化后，目标项目的 docs 目录结构：

```
docs/
├── capabilities/
│   ├── index.md              # 自动生成，请勿手动编辑
│   ├── workflow-engine.md
│   └── event-bus.md
└── conventions/
    ├── index.md              # 自动生成，请勿手动编辑
    └── design-token.md
```

`index.md` 由 Hook 在每次文档写入/编辑后自动重建。

## CLAUDE.md 集成

初始化脚本会自动在项目的 `CLAUDE.md` 中添加以下内容：

```markdown
## PKR 知识查阅（编码前必须）

进入计划模式或实现功能前，必须查阅：
1. [docs/capabilities/index.md](./docs/capabilities/index.md) — 已有可复用能力
2. [docs/conventions/index.md](./docs/conventions/index.md) — 开发规范

已有能力必须复用，禁止重新实现。编码必须遵循已注册的规范。
```

这确保 Claude 在每次编码前都会查阅 PKR 文档，形成知识驱动的编码流程。

## 工作流程

```
┌─────────────────────────────────────────────────────────┐
│  编码前                                                  │
│  ↓                                                      │
│  Claude 读取 CLAUDE.md                                  │
│  ↓                                                      │
│  查阅 docs/capabilities/index.md → 了解已有能力         │
│  查阅 docs/conventions/index.md → 了解开发规范          │
│  ↓                                                      │
│  制定方案（复用已有能力、遵循规范）                     │
│  ↓                                                      │
│  编码实现                                               │
│  ↓                                                      │
│  编码后                                                 │
│  ↓                                                      │
│  /pkr-update <name> [desc] → 更新能力文档               │
│  /pkr-add [name] <desc> → 从代码注册（名称可自动提取）  │
│  /pkr-add plan [name] <desc> → 计划注册（名称可自动生成）│
└─────────────────────────────────────────────────────────┘
```

## 开发本项目

本项目是插件市场项目，不直接使用 PKR。开发时参考 [CLAUDE.md](./CLAUDE.md)。
