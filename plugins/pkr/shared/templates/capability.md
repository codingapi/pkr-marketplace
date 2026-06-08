---
name: {module}/{short-name}           — 格式：module/short-name，模块名/短名称
module: {module_name}                 — 模块名（必填，与子目录名一致。项目自有用项目模块名，框架用框架名）
description: {description}
status: {计划中 | 已实现 | 已废弃}
scope: {前端 | 后端 | 全栈}
source: {项目自有 | 框架:{框架名} | 计划}
import: "{导入坐标，如 Maven GAV / npm 包路径 / 模块路径}"
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

<!-- 描述该能力解决的核心痛点，以及哪些业务场景需要复用此能力 -->

## 如何使用

<!-- 核心接口/API 说明、注入方式、依赖说明、配置方式 -->

## 使用实例

<!-- 可运行的代码示例，展示典型用法 -->
