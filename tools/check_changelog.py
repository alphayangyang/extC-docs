#!/usr/bin/env python3
"""开发历史按月分页与索引一致。

    python3 tools/check_changelog.py                   报告
    python3 tools/check_changelog.py --write           重写索引里的月份表
    python3 tools/check_changelog.py --gate            不一致就 exit 1（check.sh 调用）
    python3 tools/check_changelog.py --root DIR --index FILE

分工：正文按月份分页在 devlog/changelog/YYYY-MM.md；每条 ## YYYY-MM-DD · 标题（日期后可带
（...）修饰）必须落在其月份所属的那一页。devlog/changelog/README.md 是索引页：只有月份表
与写法，不存正文。表由 --write 生成，--gate 对着月份页核对条目数与日期范围。

日期字段存在历史笔误（例如 11-32、11-85、12-xx 这类不存在的日期）：本脚本只校验"月份"
与页码一致，不校验日是否真实存在；范围按字符串比较，阅读时按内容顺序理解。
"""

import argparse
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get("EXTC_DOCS") or HERE.parent)
NAME = re.compile(r"^(\d{4})-(\d{2})\.md$")
ENTRY = re.compile(r"^## (\d{4})-(\d{2})-(\d{2})(?:（[^）]*）)?\s*·\s*\S")
HEAD = re.compile(r"^## ")
ROW = re.compile(r"^\|\s*\[(\d{4}-\d{2})\]\(([^)]+)\)\s*\|\s*(\d+)\s*\|\s*([^|]*?)\s*\|\s*$")
BT = chr(96)
BEGIN = "<!-- 月份表：" + BT + "python3 tools/check_changelog.py --write" + BT + " 重新生成 -->"
END = "<!-- /月份表 -->"


def scan(path):
    bad, dates = [], []
    for i, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if not HEAD.match(line):
            continue
        m = ENTRY.match(line)
        if not m:
            bad.append(f"{path.name}:{i}: 标题不是 ## YYYY-MM-DD · 标题：{line[:60]}")
            continue
        ym = f"{m.group(1)}-{m.group(2)}"
        if ym != path.stem:
            bad.append(f"{path.name}:{i}: 条目的月份是 {ym}，却放在 {path.name}")
        dates.append(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
    return len(dates), dates, bad


def survey(directory):
    pages, rows, bad = {}, [], []
    for path in sorted(directory.glob("*.md"), reverse=True):
        if path.name == "README.md":
            continue
        if not NAME.match(path.name):
            bad.append(f"{path.name}: 文件名必须是 YYYY-MM.md")
            continue
        n, dates, errs = scan(path)
        bad += errs
        if not n:
            bad.append(f"{path.name}: 一条 ## 日期 · 标题 都没有")
            continue
        pages[path.stem] = (n, dates)
        rows.append(f"| [{path.stem}]({path.name}) | {n} | {min(dates)} → {max(dates)} |")
    return pages, rows, bad


def dup_headings(directory):
    seen, dup = {}, []
    for path in sorted(directory.glob("*.md")):
        for line in path.read_text(encoding="utf-8").split("\n"):
            if HEAD.match(line):
                if line in seen:
                    dup.append(f"{line[:70]}（{seen[line]} 与 {path.name} 都有一条）")
                seen[line] = path.name
    return dup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "devlog" / "changelog"))
    ap.add_argument("--index", default="")
    ap.add_argument("--gate", action="store_true", help="不一致就 exit 1（check.sh 调用）")
    ap.add_argument("--write", action="store_true", help="重写索引里的月份表")
    args = ap.parse_args()

    directory = pathlib.Path(args.root)
    index = pathlib.Path(args.index) if args.index else directory / "README.md"
    if not directory.is_dir():
        print(f"  -- 跳过：历史目录不存在 {directory}")
        return 0
    if not index.is_file():
        print(f"FAIL 索引页不存在 {index}", file=sys.stderr)
        return 1

    pages, rows, bad = survey(directory)
    if not pages:
        print("FAIL devlog/changelog/ 下没有任何月份页", file=sys.stderr)
        return 1
    bad += dup_headings(directory)
    total = sum(n for n, _ in pages.values())

    text = index.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        bad.append("索引页里找不到月份表的开始/结束标记（见本脚本的 BEGIN/END）")
    for line in text.split("\n"):
        if ENTRY.match(line):
            bad.append(f"索引页不该出现条目正文：{line[:60]}")
            break

    if args.write:
        head, rest = text.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        index.write_text(f"{head}{BEGIN}\n" + "\n".join(rows) + f"\n{END}{tail}", encoding="utf-8")
        print(f"write 月份表：{len(rows)} 行 -> {index}")
        return 0

    if BEGIN in text and END in text:
        want = BEGIN + "\n" + "\n".join(rows) + "\n" + END
        if want not in text:
            bad.append("索引页的月份表与月份页对不上（跑 tools/check_changelog.py --write）")
            got = text.split(BEGIN, 1)[1].split(END, 1)[0].strip().split("\n")[:6]
            for line in got:
                bad.append(f"  表现在：{line}")

    if bad:
        print(f"FAIL 历史分页/索引有 {len(bad)} 处不对", file=sys.stderr)
        for b in bad:
            print(f"  · {b}", file=sys.stderr)
        return 1
    detail = " · ".join(f"{ym}: {n}" for ym, (n, _) in sorted(pages.items(), reverse=True))
    print(f"ok  历史分页：{len(pages)} 页 / {total} 条，月份表一致（{detail}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
