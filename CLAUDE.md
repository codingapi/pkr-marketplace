# 项目知识注册中心（PKR）

## 编码前必须查阅

在进行任何编码计划（plan mode）或实现功能之前，**必须**先查阅 PKR 文档：

### 1. 查阅已有能力（避免重复造轮子）

阅读 [docs/capabilities/index.md](./docs/capabilities/index.md) 了解项目已有哪些可复用能力。

按需深入阅读对应的能力详情文档。

**规则**：如果已有能力可以解决需求，**必须复用**，禁止重新实现。

### 2. 查阅开发规范（避免违反约束）

阅读 [docs/conventions/index.md](./docs/conventions/index.md) 了解项目的开发规范。

按需深入阅读对应的规范详情文档。

**规则**：编码必须遵循已注册的规范，禁止违反。

---

## 计划模式（Plan Mode）约束

进入计划模式时，计划方案中必须包含：

1. **复用了哪些已有能力** — 列出从 PKR 中找到并复用的 Capability
2. **遵循了哪些规范** — 列出遵守的 Convention
3. **是否有新增能力** — 如果本次开发产生了可复用的新能力，计划结束后应通过 `/pkr-scan add` 注册

### 计划模板参考

```markdown
## PKR 检查

### 复用能力
- workflow-engine: 复用流程编排能力
- spring-cache: 复用声明式缓存

### 遵循规范
- design-token: 样式使用 Token 变量
- event-publish: 事件使用 ApplicationEventPublisher

### 新增能力（如有）
- rule-engine: 本次新增规则引擎，完成后需注册到 PKR
```

---

## 知识管理命令

| 命令 | 用途 |
|------|------|
| `/pkr-scan init` | 首次扫描项目，发现候选能力和规范 |
| `/pkr-scan update` | 增量更新，对比代码变更 |
| `/pkr-scan add` | 手动注册新的能力或规范 |
