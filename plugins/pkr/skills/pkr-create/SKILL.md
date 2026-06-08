---
name: pkr-create
description: >
  This skill should be used when the user asks to "create PKR structure",
  "initialize PKR directories", "setup PKR", "pkr create",
  or mentions first-time PKR project setup.
argument-hint: ""
allowed-tools: [Bash]
disable-model-invocation: true
---

# PKR Create — 创建项目知识管理结构

在目标项目中创建 PKR 所需的目录结构，并在 CLAUDE.md 中注入知识查阅约束。

## 功能

1. 创建目录：
   - `docs/capabilities/` — 能力文档目录
   - `docs/conventions/` — 规范文档目录
   - `docs/agents/` — 外部模块导出文档目录
2. 在 CLAUDE.md 中注入 PKR 知识查阅约束（幂等，不会重复添加）

## 用法

```
/pkr-create
```

执行后调用脚本完成所有操作：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkr_create.py"
```

## 脚本行为

- **目录创建**：`mkdir -p` 语义，已存在则跳过
- **CLAUDE.md 注入**：使用 HTML 注释标记实现幂等
  - 已有标记 → 跳过
  - 有旧标记 → 替换
  - 无标记 → 追加到末尾
  - 文件不存在 → 新建

## 下一步

执行完成后：
1. 如有外部模块的导出文档，将其复制到 `docs/capabilities/{module}/` 和 `docs/conventions/{module}/`
2. 执行 `/pkr-init` 扫描项目能力和规范
