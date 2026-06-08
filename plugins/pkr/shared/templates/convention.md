---
name: {name}
description: {description}
status: {计划中 | 已实现 | 已废弃}
scope: {前端 | 后端 | 全栈}
source: {项目自有 | 框架:{框架名} | 计划}
# 以下字段根据 source 类型选填：
# source=项目自有 时必填：
# symbols:                            — 关联的代码符号列表（类名、函数名等）
#   - {SymbolName1}
#   - {SymbolName2}
# content_hash: {sha256}              — 所有关联文件按路径排序拼接后的内容 hash（通过 compute_content_hash.py 计算）
# source=框架:{名称} 时必填：
# framework_version: {version}        — 框架依赖版本
---

## 解决什么问题

<!-- 描述不遵守此规范会导致的问题 -->

## 如何使用

<!-- 规范的具体规则、命名约定、代码模式要求 -->

## 使用实例

<!-- ✅ 正确示例 和 ❌ 错误示例 的对比 -->
