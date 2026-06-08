# pkr-marketplace

面向 Claude Code 的 **项目知识注册中心（PKR）** 插件市场。扫描项目代码，自动发现并注册可复用能力（Capability）和开发规范（Convention），让 AI 在编码前知道项目已有什么、该怎么做。

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

## 安装

```bash
# 安装 PKR 插件
/plugin install <marketplace-url> pkr
```

安装后在目标项目中初始化 docs 目录：

```bash
mkdir -p docs/capabilities docs/conventions
```

## 命令

| 命令 | 用途 |
|------|------|
| `/pkr-scan init` | 首次扫描：代码 + 依赖 + 规划文档，发现候选能力和规范 |
| `/pkr-scan sync` | 全量同步：扫描所有文档，对比代码变更，批量更新 |
| `/pkr-scan update <name>` | 单项更新：针对指定文档重新扫描代码并更新 |
| `/pkr-scan add` | 手动注册：补漏或注册计划中的能力 |

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

| 字段 | 值 | 说明 |
|------|-----|------|
| `status` | `已实现` / `计划中` / `已废弃` | 当前状态 |
| `scope` | `前端` / `后端` / `全栈` | 适用范围 |
| `source` | `项目自有` / `框架:{名称}` / `计划` | 知识来源 |

## 目录结构（安装后）

安装插件后，目标项目的 docs 目录结构：

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

## 三类知识来源

| 来源 | 发现方式 | 示例 |
|------|----------|------|
| **项目自有能力** | 模式匹配扫描代码 | WorkflowEngine、EventBus |
| **三方框架能力** | 扫描依赖声明文件 | Spring Cache、Redisson Lock |
| **计划中能力** | 扫描 PRD/ROADMAP + 手动注册 | Rule Engine（规划中） |

## 在 CLAUDE.md 中集成

建议在目标项目的 `CLAUDE.md` 中添加以下约束，确保 AI 编码前查阅 PKR：

```markdown
## PKR 知识查阅（编码前必须）

进入计划模式或实现功能前，必须查阅：
1. [docs/capabilities/index.md](./docs/capabilities/index.md) — 已有可复用能力
2. [docs/conventions/index.md](./docs/conventions/index.md) — 开发规范

已有能力必须复用，禁止重新实现。编码必须遵循已注册的规范。
```
