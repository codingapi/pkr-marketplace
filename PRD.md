# Project Knowledge Registry (PKR)

## 项目愿景

构建一个面向 AI Coding（Claude Code、Codex、Cursor 等）的项目知识注册中心（Project Knowledge Registry）。

目标不是生成文档。

目标不是生成架构图。

目标不是代码导航。

目标是让 AI 在编码之前知道：

- 项目已经拥有哪些能力（Capabilities）
- 项目依赖框架拥有哪些能力（Framework Capabilities）
- 项目未来规划拥有哪些能力（Planned Capabilities）
- 项目有哪些开发规范和约束（Conventions）

从而实现：

- 避免重复造轮子
- 优先复用已有能力
- 遵循项目规范开发
- 降低 AI 产生技术债务的概率

---

# 问题背景

当前 AI Coding 工具存在一个核心问题：

AI 能理解代码。

但无法理解：

项目已经有什么能力。

项目有哪些开发约束。

因此经常出现：

## 重复造轮子

项目已经存在：

- Workflow Engine
- Script Engine
- Event Bus
- Distributed Lock

AI 仍然重新实现：

- ApprovalFlow
- EventManager
- ScriptRunner
- LockManager

---

## 违反项目规范

例如：

项目存在：

Design Token

AI 仍然编写：

css color: #1677ff; padding: 8px; font-size: 14px; 

而不是：

css color: var(--primary-color); padding: var(--spacing-md); font-size: var(--font-size-md); 

导致：

- UI 不统一
- Token 无法统一管理
- 后续主题切换失效

---

# 核心思想

项目知识分为三类：

## 1. Capability

项目具备的可复用能力。

回答：

项目能做什么？

---

## 2. Convention

项目开发规范和约束。

回答：

项目应该怎么做？

---

## 3. Architecture（后续阶段）

项目如何组织。

回答：

项目是如何构建的？

Architecture 优先级最低。

Capability 和 Convention 优先级最高。

---

# Capability 定义

Capability：

可被多个业务场景复用的抽象能力。

---

属于 Capability：

- Workflow Engine
- Script Engine
- Event Bus
- Distributed Lock
- Rule Engine
- Permission Engine
- Form Designer
- Workflow Designer

---

不属于 Capability：

- OrderService
- UserController
- ProductPage
- UserListPage

因为它们属于具体业务实现。

---

# Capability 分类

## Project Capability

项目自身提供。

例如：

Workflow Engine

Script Engine

Event Bus

---

## Framework Capability

第三方框架提供。

例如：

Spring Event

Spring Cache

Spring Retry

MyBatis ORM

Redisson Distributed Lock

Flowable Workflow

---

## Planned Capability

已经规划。

但尚未实现。

例如：

java public interface WorkflowEngine { } 

实现尚不存在。

---

# Capability 生命周期

Capability 应支持生命周期管理。

---

## Proposed

已发现未来需要该能力。

---

## Designed

能力契约已定义。

例如：

java WorkflowEngine 

---

## Implemented

能力已经实现。

---

## Stable

已被多个业务复用。

---

## Deprecated

已废弃。

---

# Convention 定义

Convention：

项目开发过程中必须遵循的规则。

回答：

应该如何使用能力。

---

Convention 不解决：

项目有什么能力。

Convention 解决：

如何正确使用能力。

---

# Convention 分类

## Frontend Convention

例如：

Design Token

State Management

Request Framework

Component Development Rules

Theme Rules

---

## Backend Convention

例如：

Transaction Rules

Event Rules

DTO Rules

DDD Rules

Layer Rules

Exception Rules

---

# Design Token Convention 示例

yaml name: design-token  type: frontend  rules:    color:     must_use_token: true    spacing:     must_use_token: true    font_size:     must_use_token: true    radius:     must_use_token: true 

---

# Event Convention 示例

yaml name: event-publish  type: backend  rules:    must_use:     ApplicationEventPublisher    forbidden:     EventManager 

---

# 与 CodeGraph 的关系

CodeGraph 是事实来源。

Project Knowledge Registry 不负责代码解析。

关系：

Code

↓

CodeGraph

↓

Capability Discovery

↓

Capability Registry

↓

Claude Code

---

# Claude 集成目标

Claude 在开始编码前：

优先查询：

1. Convention Registry

了解开发约束。

2. Capability Registry

了解已有能力。

3. 再开始编码。

目标：

优先复用。

避免重复实现。

遵循项目规范。

---
