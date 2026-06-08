#!/usr/bin/env python3
"""
PKR 初始化脚本 — 在目标项目中设置 PKR 目录结构和 CLAUDE.md 集成。

跨平台兼容（Windows / macOS / Linux）。

用法:
    python3 pkr_setup.py [project_root]

参数:
    project_root  目标项目根目录（默认为 git 仓库根或当前目录）

功能:
    1. 创建 docs/capabilities/ 和 docs/conventions/ 目录
    2. 在 CLAUDE.md 中添加 PKR 知识查阅约束（幂等，不会重复添加）
"""

import os
import subprocess
import sys
from pathlib import Path


PKR_MARKER = "<!-- PKR-START -->"
PKR_END_MARKER = "<!-- PKR-END -->"

PKR_CONTENT = """\
<!-- PKR-START -->
## PKR 知识查阅（编码前必须）

进入计划模式或实现功能前，必须查阅：
1. [docs/capabilities/index.md](./docs/capabilities/index.md) — 已有可复用能力
2. [docs/conventions/index.md](./docs/conventions/index.md) — 开发规范

已有能力必须复用，禁止重新实现。编码必须遵循已注册的规范。

### 计划模式约束

计划方案中必须包含：
1. **复用了哪些已有能力** — 列出从 PKR 中找到并复用的 Capability
2. **遵循了哪些规范** — 列出遵守的 Convention
3. **是否有新增能力** — 如果本次开发产生了可复用的新能力，完成后通过 `/pkr-add` 注册

### 知识管理命令

| 命令 | 用途 |
|------|------|
| `/pkr-init` | 首次扫描项目，发现候选能力和规范 |
| `/pkr-sync` | 全量同步，对比代码变更 |
| `/pkr-update <name> [desc]` | 单项更新，可带描述指导更新 |
| `/pkr-add` | 手动注册新的能力或规范 |
<!-- PKR-END -->
"""


def get_project_root():
    """确定项目根目录。"""
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    # 尝试 git 仓库根
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip()).resolve()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return Path.cwd().resolve()


def setup_dirs(project_root):
    """创建 docs 目录结构。"""
    print("📁 创建目录结构...")

    for subdir in ["docs/capabilities", "docs/conventions"]:
        dirpath = project_root / subdir
        dirpath.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {subdir}/")

    print()


def update_claude_md(project_root):
    """幂等更新 CLAUDE.md，添加 PKR 约束。"""
    claude_md = project_root / "CLAUDE.md"

    if claude_md.is_file():
        content = claude_md.read_text(encoding="utf-8")
        if PKR_MARKER in content:
            print("📝 CLAUDE.md 已包含 PKR 约束，跳过")
            return

        # 已有内容 — 替换旧块（如果存在）或追加
        if PKR_END_MARKER in content:
            # 替换旧块
            start = content.index(PKR_MARKER)
            end = content.index(PKR_END_MARKER) + len(PKR_END_MARKER)
            content = content[:start] + PKR_CONTENT + content[end:]
            claude_md.write_text(content, encoding="utf-8")
            print("   ✅ 已更新 CLAUDE.md 中的 PKR 约束")
        else:
            # 追加到末尾
            with open(claude_md, "a", encoding="utf-8") as f:
                f.write("\n\n" + PKR_CONTENT)
            print("   ✅ 已追加到 CLAUDE.md 末尾")
    else:
        # 新建文件
        header = "# 项目开发指引\n\n"
        claude_md.write_text(header + PKR_CONTENT, encoding="utf-8")
        print("   ✅ 已创建 CLAUDE.md")


def main():
    project_root = get_project_root()

    print("🔧 PKR 初始化")
    print(f"   项目目录: {project_root}")
    print()

    setup_dirs(project_root)

    print("📝 更新 CLAUDE.md...")
    update_claude_md(project_root)
    print()

    print("✅ PKR 初始化完成！")
    print()
    print("下一步：")
    print("  1. 执行 /pkr-init 首次扫描项目")
    print("  2. 确认候选能力和规范")
    print("  3. 开始知识驱动的编码流程")


if __name__ == "__main__":
    main()
