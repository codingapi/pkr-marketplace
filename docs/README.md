# 项目知识注册中心（PKR）文档

本目录存放项目的 **Capability（能力）** 和 **Convention（规范）** 文档，供 AI 编码前查询，避免重复造轮子和违反项目规范。

## 目录结构

```
docs/
├── README.md              # 本文件 — 格式说明
├── capabilities/          # 项目能力文档
│   ├── index.md           # 能力索引（自动生成）
│   └── workflow-engine.md
└── conventions/           # 项目规范文档
    ├── index.md           # 规范索引（自动生成）
    └── design-token.md
```

| 目录 | 说明 |
|------|------|
| `capabilities/` | 项目具备的可复用能力，如 Workflow Engine、Event Bus 等 |
| `conventions/` | 项目开发规范和约束，如 Design Token、事件发布规则等 |

## 文档格式

每个 `.md` 文件必须使用以下统一格式：

```markdown
---
name: 名称
description: 描述信息
status: 计划中 | 已实现 | 已废弃
scope: 前端 | 后端 | 全栈
source: 项目自有 | 框架:{框架名} | 计划
---

## 解决什么问题

描述该能力/规范要解决的核心痛点。

## 如何使用

使用说明、API、配置方式。

## 使用实例

具体代码示例。
```

### Front Matter 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 能力或规范的名称，使用英文短横线格式（如 `workflow-engine`） |
| `description` | ✅ | 一句话描述 |
| `status` | ✅ | `计划中` — 已规划但未实现；`已实现` — 已在项目中落地；`已废弃` — 不再使用 |
| `scope` | ✅ | `前端` / `后端` / `全栈` |
| `source` | ✅ | `项目自有` — 项目代码实现；`框架:xxx` — 三方框架提供；`计划` — 规划中的能力 |

### 正文章节说明

| 章节 | 说明 |
|------|------|
| **解决什么问题** | 核心痛点和使用场景 |
| **如何使用** | API 说明、配置方式、依赖说明 |
| **使用实例** | 可运行的代码示例 |

## 如何新增文档

1. 确定类型：Capability → `capabilities/`，Convention → `conventions/`
2. 使用上述格式创建 `.md` 文件
3. 文件名与 `name` 字段保持一致（如 `event-bus.md`）
