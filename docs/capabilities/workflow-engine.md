---
name: workflow-engine
description: 通用工作流引擎，支持流程定义、节点编排、状态流转和审批流程
status: 已实现
scope: 后端
source: 项目自有
last_commit: b31f48c
code_files:
  - src/main/java/com/example/workflow/WorkflowEngine.java
  - src/main/java/com/example/workflow/WorkflowNode.java
  - src/main/java/com/example/workflow/WorkflowInstance.java
---

## 解决什么问题

项目中存在大量审批、流程编排需求，如：

- 订单审批流程
- 发布上线流程
- 请假/报销审批

如果每个业务场景都独立实现流程逻辑，会导致：

- 流程代码重复
- 状态管理混乱
- 流程变更困难

Workflow Engine 提供统一的工作流抽象，所有流程类需求都应复用此能力。

## 如何使用

### 核心接口

```java
public interface WorkflowEngine {
    // 定义流程
    WorkflowDefinition define(String name, WorkflowConfig config);

    // 启动流程实例
    WorkflowInstance start(String definitionId, Map<String, Object> variables);

    // 推进节点
    void complete(String instanceId, String nodeId, Map<String, Object> variables);

    // 查询流程状态
    WorkflowInstance getInstance(String instanceId);
}
```

### 注入方式

```java
@Autowired
private WorkflowEngine workflowEngine;
```

### 支持的功能

- 串行/并行节点编排
- 条件分支（Gateway）
- 审批节点（人工审批 + 自动审批）
- 流程变量传递
- 流程监听器（开始/结束/节点事件）

## 使用实例

### 定义一个简单的审批流程

```java
// 定义流程：提交 -> 主管审批 -> 结束
WorkflowDefinition def = workflowEngine.define("leave-approval", WorkflowConfig.builder()
    .node(Node.start("start"))
    .node(Node.userTask("manager-approve").assignee("manager"))
    .node(Node.end("end"))
    .edge("start", "manager-approve")
    .edge("manager-approve", "end")
    .build());

// 启动流程实例
WorkflowInstance instance = workflowEngine.start(def.getId(), Map.of(
    "applicant", "zhangsan",
    "days", 3,
    "reason", "家庭事务"
));

// 主管审批通过
workflowEngine.complete(instance.getId(), "manager-approve", Map.of(
    "approved", true,
    "comment", "同意"
));
```

### 监听流程事件

```java
workflowEngine.addListener("leave-approval", WorkflowEvent.NODE_COMPLETE, event -> {
    log.info("节点完成: {}", event.getNodeId());
});
```
