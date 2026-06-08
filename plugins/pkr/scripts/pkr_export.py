#!/usr/bin/env python3
"""
PKR Export — 导出指定模块的文档供其他项目使用。

将 docs/capabilities/{module}/ 和 docs/conventions/{module}/ 下的文档
导出到 docs/agents/capabilities/{module}/ 和 docs/agents/conventions/{module}/，
并转换 source 类型。

用法:
    python3 pkr_export.py <module1> [module2] ... [project_root]

仅依赖 Python 标准库，跨平台兼容。
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path


def get_project_root(args):
    """确定项目根目录。"""
    # 最后一个参数如果不是已有目录，则作为模块名处理
    # 尝试 git 仓库根
    try:
        result = __import__("subprocess").run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (FileNotFoundError, __import__("subprocess").TimeoutExpired):
        pass
    return Path.cwd()


def detect_project_version(project_root):
    """从项目配置文件中检测当前版本号。"""
    # Java: pom.xml
    pom = project_root / "pom.xml"
    if pom.is_file():
        content = pom.read_text(encoding="utf-8")
        # 匹配顶层 <version> 标签（非子模块的）
        match = re.search(r"<project[^>]*>.*?<version>([^<]+)</version>", content, re.DOTALL)
        if match:
            return match.group(1)

    # Node/TS: package.json
    pkg = project_root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            if "version" in data:
                return data["version"]
        except (json.JSONDecodeError, KeyError):
            pass

    # Python: pyproject.toml
    pyproject = project_root / "pyproject.toml"
    if pyproject.is_file():
        content = pyproject.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if match:
            return match.group(1)

    # Go: go.mod 无版本号
    go_mod = project_root / "go.mod"
    if go_mod.is_file():
        return "module"

    # Rust: Cargo.toml
    cargo = project_root / "Cargo.toml"
    if cargo.is_file():
        content = cargo.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if match:
            return match.group(1)

    return "unknown"


def parse_frontmatter(filepath):
    """解析 Markdown 文件的 YAML frontmatter。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except (IOError, OSError):
        return None, content if "content" in dir() else ""

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, content

    fm = {}
    fm_text = match.group(1)
    rest = content[match.end():]

    for line in fm_text.split("\n"):
        line_stripped = line.strip()
        if ":" in line_stripped and not line_stripped.startswith("#"):
            key, _, value = line_stripped.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                fm[key] = value
            elif key:
                fm[key] = ""

    return fm, content


def transform_frontmatter(content, module, version):
    """转换 frontmatter：项目自有 → 框架:{module}。"""
    match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
    if not match:
        return content

    fm_text = match.group(2)
    lines = fm_text.split("\n")
    new_lines = []
    source = ""
    skip_next_list_item = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 跳过 symbols 和 content_hash 字段
        if stripped.startswith("symbols:"):
            i += 1
            # 跳过列表项
            while i < len(lines) and lines[i].strip().startswith("- "):
                i += 1
            continue
        if stripped.startswith("content_hash:"):
            i += 1
            continue

        # 处理 source 字段
        if stripped.startswith("source:"):
            _, _, value = stripped.partition(":")
            value = value.strip()
            if value == "项目自有" or value.startswith("项目自有"):
                new_source = f"框架:{module}"
                new_lines.append(f"source: {new_source}")
                source = new_source
            else:
                new_lines.append(line)
                source = value
            i += 1
            continue

        new_lines.append(line)
        i += 1

    # 如果原来是项目自有，添加 framework_version
    if source.startswith("框架:"):
        # 检查是否已有 framework_version
        has_fw = any(l.strip().startswith("framework_version:") for l in new_lines)
        if not has_fw:
            # 在 import 行后面插入
            insert_idx = None
            for idx, l in enumerate(new_lines):
                if l.strip().startswith("import:"):
                    insert_idx = idx + 1
                    break
            if insert_idx:
                new_lines.insert(insert_idx, f"framework_version: \"{version}\"")
            else:
                new_lines.append(f"framework_version: \"{version}\"")

    new_fm = "\n".join(new_lines)
    return f"{match.group(1)}{new_fm}{match.group(3)}{content[match.end():]}"


def export_module(module, project_root, version):
    """导出单个模块的文档。"""
    docs_dir = project_root / "docs"
    agents_dir = docs_dir / "agents"

    stats = {"capabilities": 0, "conventions": 0}

    for category in ["capabilities", "conventions"]:
        src_dir = docs_dir / category / module
        dst_dir = agents_dir / category / module

        if not src_dir.is_dir():
            continue

        dst_dir.mkdir(parents=True, exist_ok=True)

        for md_file in sorted(src_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue

            content = md_file.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(md_file)

            if fm is None:
                continue

            source = fm.get("source", "")

            # 转换 frontmatter
            if source == "项目自有" or source.startswith("项目自有"):
                content = transform_frontmatter(content, module, version)

            # 写入目标文件
            dst_file = dst_dir / md_file.name
            dst_file.write_text(content, encoding="utf-8")
            stats[category] += 1
            print(f"   ✅ {category}/{module}/{md_file.name} → agents/{category}/{module}/{md_file.name}")

    return stats




def main():
    if len(sys.argv) < 2:
        print("用法: python3 pkr_export.py <module1> [module2] ... [project_root]", file=sys.stderr)
        sys.exit(1)

    args = sys.argv[1:]

    # 尝试判断最后一个参数是否为目录（项目根目录）
    last_arg = Path(args[-1])
    if last_arg.is_dir():
        project_root = last_arg.resolve()
        modules = args[:-1]
    else:
        project_root = get_project_root(args)
        modules = args

    if not modules:
        print("错误: 请指定至少一个模块名", file=sys.stderr)
        sys.exit(1)

    version = detect_project_version(project_root)
    docs_dir = project_root / "docs"
    agents_dir = docs_dir / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 PKR Export")
    print(f"   项目目录: {project_root}")
    print(f"   项目版本: {version}")
    print(f"   导出模块: {', '.join(modules)}")
    print()

    for module in modules:
        print(f"📤 导出模块: {module}")

        # 检查源目录是否存在
        has_caps = (docs_dir / "capabilities" / module).is_dir()
        has_convs = (docs_dir / "conventions" / module).is_dir()

        if not has_caps and not has_convs:
            print(f"   ⚠️  模块 {module} 在 docs/capabilities/ 和 docs/conventions/ 中均未找到文档，跳过")
            continue

        stats = export_module(module, project_root, version)

        total = stats["capabilities"] + stats["conventions"]
        print(f"   ✅ 共导出 {total} 篇文档")
        print()

    print("✅ 导出完成！")
    print()
    print("下一步（下游项目）：")
    print("  1. 将导出的文件复制到目标项目：")
    print("     agents/capabilities/{module}/ → docs/capabilities/{module}/")
    print("     agents/conventions/{module}/  → docs/conventions/{module}/")
    print("  2. 执行 /pkr-init 扫描项目（已导入的文档会自动跳过）")


if __name__ == "__main__":
    main()
