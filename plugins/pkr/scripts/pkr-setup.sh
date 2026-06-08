#!/usr/bin/env bash
#
# PKR 初始化脚本 — 在目标项目中设置 PKR 目录结构和 CLAUDE.md 集成
#
# 用法:
#   bash "$CLAUDE_PLUGIN_ROOT/scripts/pkr-setup.sh" [project_root]
#
# 参数:
#   project_root  目标项目根目录（默认为当前目录或 git 仓库根）
#
# 功能:
#   1. 创建 docs/capabilities/ 和 docs/conventions/ 目录
#   2. 在 CLAUDE.md 中添加 PKR 知识查阅约束（幂等，不会重复添加）
#

set -euo pipefail

# 确定项目根目录
if [[ $# -gt 0 ]]; then
    PROJECT_ROOT="$1"
elif git rev-parse --show-toplevel &>/dev/null; then
    PROJECT_ROOT="$(git rev-parse --show-toplevel)"
else
    PROJECT_ROOT="$(pwd)"
fi

# 转为绝对路径
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"

echo "🔧 PKR 初始化"
echo "   项目目录: $PROJECT_ROOT"
echo ""

# ============================================
# Step 1: 创建目录结构
# ============================================

echo "📁 创建目录结构..."

mkdir -p "$PROJECT_ROOT/docs/capabilities"
mkdir -p "$PROJECT_ROOT/docs/conventions"

echo "   ✅ docs/capabilities/"
echo "   ✅ docs/conventions/"
echo ""

# ============================================
# Step 2: 更新 CLAUDE.md
# ============================================

CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"

# 检查是否已包含 PKR 约束
PKR_MARKER="<!-- PKR-START -->"

if [[ -f "$CLAUDE_MD" ]] && grep -q "$PKR_MARKER" "$CLAUDE_MD"; then
    echo "📝 CLAUDE.md 已包含 PKR 约束，跳过"
else
    echo "📝 更新 CLAUDE.md..."

    # PKR 内容块
    PKR_CONTENT="
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
3. **是否有新增能力** — 如果本次开发产生了可复用的新能力，完成后通过 \`/pkr-scan add\` 注册

### 知识管理命令

| 命令 | 用途 |
|------|------|
| \`/pkr-scan init\` | 首次扫描项目，发现候选能力和规范 |
| \`/pkr-scan sync\` | 全量同步，对比代码变更 |
| \`/pkr-scan update <name>\` | 单项更新指定能力或规范 |
| \`/pkr-scan add\` | 手动注册新的能力或规范 |
<!-- PKR-END -->
"

    if [[ -f "$CLAUDE_MD" ]]; then
        # CLAUDE.md 已存在，追加到末尾
        echo "" >> "$CLAUDE_MD"
        echo "$PKR_CONTENT" >> "$CLAUDE_MD"
        echo "   ✅ 已追加到 CLAUDE.md 末尾"
    else
        # CLAUDE.md 不存在，创建新文件
        echo "# 项目开发指引" > "$CLAUDE_MD"
        echo "" >> "$CLAUDE_MD"
        echo "$PKR_CONTENT" >> "$CLAUDE_MD"
        echo "   ✅ 已创建 CLAUDE.md"
    fi
fi

echo ""

# ============================================
# Step 3: 完成提示
# ============================================

echo "✅ PKR 初始化完成！"
echo ""
echo "下一步："
echo "  1. 执行 /pkr-scan init 首次扫描项目"
echo "  2. 确认候选能力和规范"
echo "  3. 开始知识驱动的编码流程"
