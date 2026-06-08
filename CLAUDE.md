# PKR Marketplace — 开发指引

本项目是 Claude Code 插件市场（Marketplace），提供项目知识注册中心（PKR）能力。

**本项目不直接使用 PKR**，目标项目通过 `/plugin install` 安装后使用。

## 项目结构

```
my-marketplace/
├── .claude-plugin/marketplace.json    # 市场注册文件
├── plugins/
│   └── pkr/                           # PKR 插件
│       ├── .claude-plugin/plugin.json
│       ├── hooks/hooks.json           # PostToolUse Hook
│       ├── scripts/                   # 插件级共享脚本（供 hook 调用）
│       └── skills/pkr-scan/           # Skill 定义
│           ├── SKILL.md
│           ├── templates/
│           ├── references/
│           └── scripts/               # Skill 级脚本副本
└── docs/                              # 示例文档（开发参考用）
```

## 脚本副本一致性验证

`rebuild_pkr_index.py` 存在两份完全相同的副本，修改时必须同步：

```bash
# 验证两份脚本一致
diff plugins/pkr/scripts/rebuild_pkr_index.py \
     plugins/pkr/skills/pkr-scan/scripts/rebuild_pkr_index.py
```

- `plugins/pkr/scripts/` → 被 `hooks/hooks.json` 调用（`${CLAUDE_PLUGIN_ROOT}/scripts/`）
- `plugins/pkr/skills/pkr-scan/scripts/` → 被 SKILL.md 引用

## 开发时测试

在目标项目中安装插件后，通过以下方式验证：

1. `/pkr-scan init` — 确认能扫描出候选并生成文档
2. `/pkr-scan sync` — 确认全量同步能检测代码变更
3. `/pkr-scan update <name>` — 确认单项更新正常
4. `/pkr-scan add` — 确认手动注册正常
5. 写入 `docs/capabilities/*.md` 后确认索引自动重建
