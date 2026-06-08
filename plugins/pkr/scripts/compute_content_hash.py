#!/usr/bin/env python3
"""
PKR Content Hash 计算工具 — 跨平台确定性文件内容 hash。

将多个关联文件按路径字典序排序后拼接，归一化行尾为 LF（消除 CRLF/LF 差异），
计算单个 SHA-256 hash 值。

仅依赖 Python 标准库，跨平台兼容（Windows / macOS / Linux）。

用法:
    python3 compute_content_hash.py <file1> [file2] [file3] ...

输出:
    64 位十六进制 SHA-256 hash 字符串（单行）

示例:
    python3 compute_content_hash.py src/WorkflowEngine.java src/WorkflowNode.java
"""

import hashlib
import sys


def compute_hash(file_paths):
    """
    计算文件内容 hash。

    1. 文件路径按字典序排序
    2. 读取文件内容（二进制模式）
    3. 将 \\r\\n 替换为 \\n（消除行尾差异）
    4. 拼接后计算 SHA-256
    """
    sorted_paths = sorted(file_paths)
    h = hashlib.sha256()
    for path in sorted_paths:
        with open(path, "rb") as f:
            content = f.read()
        # 归一化行尾：CRLF → LF
        content = content.replace(b"\r\n", b"\n")
        h.update(content)
    return h.hexdigest()


def main():
    if len(sys.argv) < 2:
        print("用法: python3 compute_content_hash.py <file1> [file2] ...", file=sys.stderr)
        sys.exit(1)

    file_paths = sys.argv[1:]
    print(compute_hash(file_paths))


if __name__ == "__main__":
    main()
