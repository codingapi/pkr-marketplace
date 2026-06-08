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
/pkr-scan init
```

Claude 会扫描项目代码、依赖和规划文档，列出候选的能力和规范，由你确认后生成文档。

### 4. 日常维护

```bash
# 修改了某个能力后，立即更新对应文档
/pkr-scan update workflow-engine

# 定期全量同步（检查所有文档与代码的一致性）
/pkr-scan sync

# 手动注册遗漏的能力或规范
/pkr-scan add
```

## 命令详解

### `/pkr-scan init` — 首次构建

扫描项目代码、依赖声明和规划文档，发现候选知识：

| 来源 | 发现方式 | 示例 |
|------|----------|------|
| **项目自有能力** | 模式匹配扫描代码 | WorkflowEngine、EventBus |
| **三方框架能力** | 扫描依赖声明文件 | Spring Cache、Redisson Lock |
| **计划中能力** | 扫描 PRD/ROADMAP + 手动注册 | Rule Engine（规划中） |

扫描完成后会列出候选清单，由你逐个确认/排除，确认后自动生成文档。

### `/pkr-scan sync` — 全量同步

对比所有现有文档与代码/依赖现状，**智能检测变更**后批量更新：

- **项目自有**：通过 Git commit hash 检测关联源码是否变化，未变化则跳过
- **三方框架**：通过依赖版本号检测，版本未变则跳过
- **计划中**：完全忽略（计划中的能力不参与 sync）
- 新增的 → 提示添加
- 消失的 → 标记为 `已废弃`（不删除）
- 变更的 → 幂等合并（事实以代码为准，人工编辑保留）

### `/pkr-scan update <name>` — 单项更新

针对单个已注册的能力或规范文档，重新扫描代码并更新：

```bash
/pkr-scan update workflow-engine
/pkr-scan update design-token
```

适用于修改了某个能力后立即更新对应文档，比全量 sync 更快。

### `/pkr-scan add` — 手动注册

通用的手动入口，用于补漏和扩展：

| 场景 | status | source |
|------|--------|--------|
| 扫描没发现但项目中确实存在的能力 | 已实现 | 项目自有 |
| 计划开发但代码尚未实现的能力 | 计划中 | 计划 |
| 速查表中未收录的三方框架能力 | 已实现 | 框架:xxx |
| 扫描遗漏的规范/约定 | 已实现 | 项目自有 |

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

**条件字段（sync 变更检测用）：**

| source 类型 | 字段 | 说明 |
|------------|------|------|
| `项目自有` | `last_commit` | 关联源码的 git commit hash，用于检测代码是否变化 |
| `项目自有` | `code_files` | 关联的源码文件列表 |
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
│  /pkr-scan update <name> → 更新变更的能力文档           │
│  /pkr-scan add → 注册新产生的能力                       │
└─────────────────────────────────────────────────────────┘
```

## 开发本项目

本项目是插件市场项目，不直接使用 PKR。开发时参考 [CLAUDE.md](./CLAUDE.md)。
