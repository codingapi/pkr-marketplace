---
name: design-token
description: 前端样式必须使用 Design Token 变量，禁止硬编码颜色、间距、字号等值
status: 已实现
scope: 前端
source: 项目自有
import: "@shared/design-tokens"
symbols:
  - tokens.css
  - theme.ts
content_hash: a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a
---

## 解决什么问题

如果直接写死样式值（如 `color: #1677ff`），会导致：

- UI 风格不统一
- 主题切换失效
- 批量修改困难
- Design Token 体系形同虚设

通过强制使用 Design Token，确保所有样式值来自统一的变量体系。

## 如何使用

### 规则

| 属性类别 | 必须使用 Token | 禁止硬编码 |
|----------|---------------|-----------|
| 颜色 | `var(--color-*)` | `#1677ff`, `rgb(22, 119, 255)` |
| 间距 | `var(--spacing-*)` | `8px`, `16px` |
| 字号 | `var(--font-size-*)` | `14px`, `16px` |
| 圆角 | `var(--border-radius-*)` | `4px`, `8px` |
| 阴影 | `var(--shadow-*)` | `0 2px 8px rgba(0,0,0,0.15)` |

### Token 变量命名规范

```
--color-{用途}-{层级}       如 --color-primary, --color-text-secondary
--spacing-{尺寸}            如 --spacing-xs(4px), --spacing-sm(8px), --spacing-md(16px)
--font-size-{尺寸}          如 --font-size-sm(12px), --font-size-md(14px)
--border-radius-{尺寸}      如 --border-radius-sm(4px), --border-radius-md(8px)
```

### 在 CSS 中使用

```css
/* ✅ 正确 */
.card {
  color: var(--color-text-primary);
  padding: var(--spacing-md);
  font-size: var(--font-size-md);
  border-radius: var(--border-radius-md);
}

/* ❌ 错误 — 禁止硬编码 */
.card {
  color: #333333;
  padding: 16px;
  font-size: 14px;
  border-radius: 8px;
}
```

### 在 CSS-in-JS 中使用

```tsx
// ✅ 正确
const Card = styled.div`
  color: ${tokens.color.textPrimary};
  padding: ${tokens.spacing.md};
`;

// ❌ 错误
const Card = styled.div`
  color: #333333;
  padding: 16px;
`;
```

## 使用实例

### 完整的组件样式示例

```css
.button-primary {
  background-color: var(--color-primary);
  color: var(--color-white);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-md);
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-sm);
}

.button-primary:hover {
  background-color: var(--color-primary-hover);
}

.button-primary:disabled {
  background-color: var(--color-disabled);
  cursor: not-allowed;
}
```
