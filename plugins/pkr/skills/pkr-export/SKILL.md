---
name: pkr-export
description: >
  This skill should be used when the user asks to "export PKR docs",
  "export module", "pkr export", "export capabilities",
  or mentions exporting PKR documents for distribution.
argument-hint: "<module1> [module2] ..."
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion, Glob, Grep]
disable-model-invocation: true
---

# PKR Export — 导出模块文档供其他项目使用

将指定模块的能力和协规文档导出到 `docs/agents/` 目录，按 `capabilities/{module}/` 和 `conventions/{module}/` 分类存放，供其他项目作为外部能力导入使用。

## 用法

```
/pkr-export mylib                    # 导出单个模块
/pkr-export mylib springboot         # 导出多个模块
```

- `<module>`（必填）：要导出的模块名，即 `docs/capabilities/` 或 `docs/conventions/` 下的子目录名

## 导出目录结构

```
docs/agents/
├── capabilities/
│   └── {module}/
│       └── *.md                     # 能力文档
└── conventions/
    └── {module}/
        └── *.md                     # 规范文档
```

> 此结构与 `docs/capabilities/{module}/` 和 `docs/conventions/{module}/` 保持一致，便于 pkr-init 匹配。

## Source 转换规则

导出时根据文档的 `source` 类型进行转换：

| 原始 source | 导出后 source | 处理 |
|------------|--------------|------|
| `项目自有` | `框架:{module}` | 移除 `symbols`/`content_hash`，补充 `framework_version` |
| `框架:xxx` | `框架:xxx`（不变） | 原样复制 |

**项目自有 → 框架** 的具体转换：
- `source: 项目自有` → `source: 框架:{module}`
- 移除 `symbols` 字段（源码级信息，不可移植）
- 移除 `content_hash` 字段（依赖本地文件内容）
- 补充 `framework_version`：从项目配置读取当前版本
- `import` 坐标保持不变

## 脚本使用

通过 Bash 直接执行：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pkr_export.py" <module1> [module2] ...
```

## 下游项目使用方式

框架开发者将 `docs/agents/` 随包发布（如 npm 包的 `agents/` 目录），
下游项目安装后执行：

```bash
# 将导出文件复制到项目的 capabilities/conventions 目录
cp -r node_modules/{package}/agents/capabilities/{module}/ docs/capabilities/{module}/
cp -r node_modules/{package}/agents/conventions/{module}/ docs/conventions/{module}/
```

然后执行 `/pkr-init`，已导入的文档会自动跳过，不再重复分析。

## 反模式（禁止行为）

1. **禁止修改原始文档**：导出是复制操作，不修改 `docs/capabilities/` 和 `docs/conventions/` 下的原文件
2. **禁止导出 index.md**：索引文件由脚本自动生成，不需要导出
3. **禁止跳过确认**：导出前应展示将要导出的文档清单，经用户确认
