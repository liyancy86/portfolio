#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""发布前检查：本仓 README 里还有没有没替换的仓库链接占位符。

为什么要一个脚本而不是一行 grep：占位符这个串本身会出现在检查命令里，
`grep -rn "<占位符>" .` 会命中它自己，于是"grep 不到"永远不成立 —— 这类自指检查
放在文档里当验收步骤是不成立的。这里把占位符拆成两段拼出来（`PLACE_A + PLACE_B`），
脚本源码里不存在那个完整的串，所以它不会命中自己 —— 包括本行。

用法（从本仓根目录）：
    python tools/check_links.py          # 检查，退出码 0 = 干净，1 = 还有占位符
    python tools/check_links.py --fix    # 直接替换（需要 --user 指定真实用户名）

只改 Markdown 里的**链接目标**（`https://github.com/<占位符>/…`），
不动目录名、不动正文里对仓名的引用。
"""
import argparse
import os
import re
import sys

PLACE_A = "GITHUB"
PLACE_B = "_USER"
PLACEHOLDER = PLACE_A + PLACE_B

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERN = re.compile(r"github\.com/" + PLACE_A + PLACE_B + r"/([\w.-]+)")


def scan():
    hits = []
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for fn in files:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    for m in PATTERN.finditer(line):
                        hits.append((os.path.relpath(path, HERE), i, m.group(1)))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="用 --user 给的用户名替换链接里的占位符")
    ap.add_argument("--user", default=None, help="真实 GitHub 用户名")
    args = ap.parse_args()

    hits = scan()
    if not args.fix:
        if not hits:
            print("OK：没有未替换的仓库链接占位符。")
            return 0
        print("还有 %d 处未替换的仓库链接：" % len(hits))
        for path, line, repo in hits:
            print("   %s:%d  ->  %s" % (path, line, repo))
        print()
        print("替换：python tools/check_links.py --fix --user <你的用户名>")
        return 1

    if not args.user:
        print("--fix 需要 --user <用户名>")
        return 2
    changed = 0
    for path, _, _ in {(p, 0, r) for p, _, r in hits}:
        full = os.path.join(HERE, path)
        with open(full, encoding="utf-8") as f:
            text = f.read()
        new = PATTERN.sub("github.com/%s/\\1" % args.user, text)
        if new != text:
            with open(full, "w", encoding="utf-8", newline="\n") as f:
                f.write(new)
            changed += 1
            print("已改：%s" % path)
    print("共改 %d 个文件。" % changed)
    left = scan()
    print("复查：剩余 %d 处。" % len(left))
    return 0 if not left else 1


if __name__ == "__main__":
    sys.exit(main())
