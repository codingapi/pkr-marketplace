# PKR Marketplace — 开发指引

本项目是 Claude Code 插件市场（Marketplace），提供项目知识注册中心（PKR）能力。

**本项目不直接使用 PKR**，目标项目通过 `/plugin install` 安装后使用。

## 项目结构

```
pkr-marketplace/
├── .claude-plugin/marketplace.json    # 市场注册文件
├── plugins/
│   └── pkr/                           # PKR 插件
│       ├── .claude-plugin/plugin.json
│       ├── hooks/hooks.json           # PostToolUse Hook
│       ├── scripts/                   # 插件级脚本（pkr_create.py, pkr_export.py, rebuild_pkr_index.py, compute_content_hash.py）
│       ├── shared/                    # 跨 skill 共享资源
│       │   ├── templates/
│       │   └── references/
│       └── skills/
│           ├── pkr-create/SKILL.md    # 创建目录结构 + CLAUDE.md
│           ├── pkr-export/SKILL.md    # 导出模块文档
│           ├── pkr-init/SKILL.md      # 扫描项目能力和规范
│           ├── pkr-sync/SKILL.md      # 全量同步
│           ├── pkr-update/SKILL.md    # 单项更新
│           └── pkr-add/SKILL.md       # 手动注册
└── docs/                              # 示例文档（开发参考用）
```

## 开发时测试

在目标项目中安装插件后，通过以下方式验证：

1. `/pkr-create` — 确认创建 docs/capabilities/、docs/conventions/、docs/agents/ 目录，CLAUDE.md 注入
2. `/pkr-export <module>` — 确认导出到 docs/agents/{module}/，source 转换正确，manifest.json 生成
3. `/pkr-init` — 确认自动跳过已有文档，可补充发现同模块下的新文档
4. `/pkr-sync` — 确认全量同步能检测代码变更（递归扫描子目录）
5. `/pkr-update <module>/<name>` — 确认模块文档更新正常（如 `myapp/workflow-engine`、`springboot/cache`）
6. `/pkr-add <module>/<name> <desc>` — 确认指定名称注册正常（如 `springboot/cache`）
7. `/pkr-add <desc>` — 确认自动生成名称注册正常（自动推断模块名）
8. `/pkr-add plan <module>/<name> <desc>` — 确认计划注册正常
9. `/pkr-add plan <desc>` — 确认自动生成名称计划注册正常
10. 写入 `docs/capabilities/**/*.md` 后确认索引自动重建（根目录文件应被跳过并警告）
