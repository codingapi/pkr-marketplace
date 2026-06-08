#!/usr/bin/env python3
"""
PKR Index Rebuilder — 分别在各子目录下生成独立的 index.md。

扫描 docs/capabilities/ 和 docs/conventions/ 下的文档（含子目录），
从 YAML frontmatter 提取 name/description/status/scope/source/module，
按模块分组，分别在各自目录下生成 index.md。

生成文件:
  - docs/capabilities/index.md
  - docs/conventions/index.md

仅依赖 Python 标准库，幂等，原子写入。

用法:
    python3 rebuild_pkr_index.py [project_root]

默认 project_root 为 git 仓库根目录，若不在 git 仓库中则为当前目录。
"""

import os
import re
import sys
import tempfile
from pathlib import Path


def get_project_root():
    """获取项目根目录。"""
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return Path.cwd()


def parse_frontmatter(filepath):
    """从 Markdown 文件解析 YAML frontmatter，返回字典。"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (IOError, OSError):
        return None

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    fm = {}
    for line in match.group(1).split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                fm[key] = value

    if "name" not in fm:
        return None

    fm.setdefault("description", "")
    fm.setdefault("status", "已实现")
    fm.setdefault("scope", "全栈")
    fm.setdefault("source", "项目自有")

    return fm


def collect_category_docs(category_dir):
    """递归收集某个分类目录下的所有文档（排除各级 index.md）。"""
    items = []
    if not category_dir.is_dir():
        return items
    for md_file in sorted(category_dir.rglob("*.md")):
        if md_file.name == "index.md":
            continue
        fm = parse_frontmatter(md_file)
        if fm:
            relpath = md_file.relative_to(category_dir)
            # 提取 module：一级子目录名，根目录文件无 module
            parts = relpath.parts
            if len(parts) > 1:
                fm["_module"] = parts[0]
            else:
                fm["_module"] = fm.get("module", "")
            fm["_relpath"] = str(relpath)
            fm["_filename"] = md_file.name
            items.append(fm)
    return items


def generate_category_index(title, title_cn, items):
    """为某个分类生成独立的 index.md 内容，按模块分组。"""
    lines = [
        f"# {title_cn}（{title}）",
        "",
        "> 🔄 此文件由 `rebuild_pkr_index.py` 自动生成，请勿手动编辑。",
        "",
    ]

    if not items:
        lines.append(f"_暂无已注册的{title_cn}文档。_")
        lines.append("")
        return "\n".join(lines) + "\n"

    # 按 module 分组：无 module 的归为"核心"
    modules = {}
    for item in items:
        mod = item.get("_module", "") or "核心"
        modules.setdefault(mod, []).append(item)

    for status in ["已实现", "计划中", "已废弃"]:
        # 收集该状态下的所有模块和条目
        status_modules = {}
        for mod, mod_items in sorted(modules.items()):
            group = [i for i in mod_items if i.get("status") == status]
            if group:
                status_modules[mod] = group

        if not status_modules:
            continue

        status_icon = {"已实现": "✅", "计划中": "🗓️", "已废弃": "⚠️"}.get(status, "")
        lines.append(f"## {status_icon} {status}")
        lines.append("")
        lines.append("| 名称 | 模块 | 描述 | 范围 | 来源 |")
        lines.append("|------|------|------|------|------|")

        for mod, group in sorted(status_modules.items()):
            for item in group:
                name = item["name"]
                desc = item.get("description", "")
                scope = item.get("scope", "")
                source = item.get("source", "")
                relpath = item.get("_relpath", "")
                link = f"[{name}](./{relpath})" if relpath else name
                mod_label = "" if mod == "核心" else mod
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                lines.append(f"| {link} | {mod_label} | {desc} | {scope} | {source} |")

        lines.append("")

    # 统计
    total = len(items)
    implemented = len([i for i in items if i.get("status") == "已实现"])
    planned = len([i for i in items if i.get("status") == "计划中"])
    deprecated = len([i for i in items if i.get("status") == "已废弃"])

    lines.append("---")
    lines.append("")
    lines.append(f"**统计**: 共 {total} 篇 — "
                 f"已实现 {implemented} / 计划中 {planned} / 已废弃 {deprecated}")

    return "\n".join(lines) + "\n"


def atomic_write(filepath, content):
    """原子写入文件。"""
    dirpath = filepath.parent
    dirpath.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=dirpath, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, filepath)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def main():
    project_root = get_project_root()
    docs_dir = project_root / "docs"

    categories = [
        ("capabilities", "Capabilities", "能力"),
        ("conventions", "Conventions", "规范"),
    ]

    results = []
    for dirname, title, title_cn in categories:
        category_dir = docs_dir / dirname
        items = collect_category_docs(category_dir)
        index_content = generate_category_index(title, title_cn, items)

        # 确保目录存在
        category_dir.mkdir(parents=True, exist_ok=True)
        index_path = category_dir / "index.md"
        atomic_write(index_path, index_content)
        results.append((title_cn, len(items), index_path))

    for title_cn, count, path in results:
        print(f"✅ {title_cn}索引已更新: {path} ({count} 篇)")


if __name__ == "__main__":
    main()
