#!/usr/bin/env python3
"""文档项目索引闸门：README 是唯一索引，活文档一个不能漏、一个不能多。

    python3 tools/check_index.py          报告
    python3 tools/check_index.py --gate   有失败 exit 1（check.sh 调用）

活文档集合 = guide/*.md 4 + reference/*.md 3 + design/*.md 16 + plans/*.md 5 + STYLE.md。
README 里的这些链接集合必须与之相等；devlog/archive/跨仓库链接不计入集合，但链接本身
由 check_style 负责可解析。
"""

import argparse
import os
import pathlib
import posixpath
import re
import sys
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get("EXTC_DOCS") or HERE.parent)
LIVE_DIRS = ("guide", "reference", "design", "plans")
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)]*)\)")


def link_targets(path):
    out = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for i, line in enumerate(text.split("\n"), 1):
        for m in LINK.finditer(line):
            t = m.group(3).strip().split(" ")[0]
            if t.startswith("<") and t.endswith(">"):
                t = t[1:-1]
            low = t.lower()
            if low.startswith(("http://", "https://", "mailto:", "data:")) or t.startswith("#"):
                continue
            t = urllib.parse.unquote(t.split("#")[0])
            if not t:
                continue
            out.append((i, posixpath.normpath(t)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true", help="有失败就 exit 1（check.sh 调用）")
    ap.parse_args()

    readme = ROOT / "README.md"
    if not readme.is_file():
        print("FAIL 缺少 README.md（文档项目唯一索引）", file=sys.stderr)
        return 1

    expected = set()
    for d in LIVE_DIRS:
        for p in sorted((ROOT / d).glob("*.md")):
            expected.add(f"{d}/{p.name}")
    if (ROOT / "STYLE.md").is_file():
        expected.add("STYLE.md")

    live_prefixes = tuple(d + "/" for d in LIVE_DIRS)
    actual, dead = set(), []
    for line, target in link_targets(readme):
        if target == "STYLE.md" or target.startswith(live_prefixes):
            if (ROOT / target).is_file():
                actual.add(target)  # 同一页允许在多个入口表格里出现（去重后比较集合）
            else:
                dead.append(f"README.md:{line}: 索引条目指向不存在的文件 {target}")

    missing = sorted(expected - actual)
    extra = sorted(actual - expected)

    print(f"索引：README 覆盖活文档 {len(actual)}/{len(expected)} 篇")
    if missing:
        print(f"失败：{len(missing)} 篇活文档没进 README 索引（孤儿页）")
        for x in missing:
            print("  FAIL 未索引  " + x)
    if extra:
        print(f"失败：{len(extra)} 条索引不在活文档集合里")
        for x in extra:
            print("  FAIL 多余条目 " + x)
    for x in dead:
        print("  FAIL 死条目  " + x)
    if missing or extra or dead:
        return 1
    print("ok  README 索引与活文档集合一致（无孤儿、无死条目）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
