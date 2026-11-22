#!/usr/bin/env python3
"""文档项目活文档样式闸门（施工单 3.3 / STYLE.md）。

    python3 tools/check_style.py          报告
    python3 tools/check_style.py --gate   有失败 exit 1（check.sh 调用）

范围：README.md、STYLE.md、guide/*.md、reference/*.md、design/*.md、plans/*.md。
devlog/ 与 archive/ 是历史材料，豁免（见各自 README）。

检查：
  1. H1 之后五行内必须有 "> 状态：" 块；
  2. 无数字锚点：file.c:123、file.c:1-20、裸 :123、第 N 行、§N；
  3. 无绝对路径：/home、/tmp 等、~/、file://、Windows 盘符；
  4. 无历史词（词表抄自编译器仓库 tools/check_no_history.py 的 RULES）；
  5. 相对链接可解析（http/https/mailto/#锚点 跳过）；
  6. 无空链接 / 空链接文字。
"""

import argparse
import os
import pathlib
import re
import sys
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get("EXTC_DOCS") or HERE.parent)
LIVE_DIRS = ("guide", "reference", "design", "plans")
ROOT_DOCS = ("README.md", "STYLE.md")

STATUS = re.compile(r"^>\s*状态：")
ANCHOR_FILE = re.compile(r"[A-Za-z0-9_./+~-]+\.(?:c|h|inc|py|sh|extc):\d+")
ANCHOR_BARE = re.compile(r"(?<![\w:.\x22]):\d{1,5}(?!\d)")
ANCHOR_RANGE = re.compile(r"(?<![\w:.\x22]):\d{1,5}[-–—]\d")
ANCHOR_LINE = re.compile(r"第\s*\d+\s*行")
ANCHOR_SEC = re.compile(r"§\s*\d+(?:\.\d+)*")
ABS_PATH = re.compile(
    r"(?<![\w:])/(?:home|Users|tmp|root|mnt|opt|srv|var|usr|etc)(?:/|$)"
    r"|(?<!\w)~[/\\]"
    r"|[A-Za-z]:[\\/]"
    r"|file://")
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)]*)\)")
BT = chr(96)
FENCE = re.compile(BT * 3 + r".*?" + BT * 3, re.S)

# 抄自编译器仓库 tools/check_no_history.py 的 RULES（保持同一份词表，便于两侧口径一致）。
# 该脚本已删除围栏代码块——被禁词的「引例」应当写在围栏里。
HIST_RULES = [
    ("decision-number", re.compile(r"定案\s*\d+")),
    ("plan-number", re.compile(r"PLAN\s*#\s*\d+")),
    ("history-word", re.compile(r"以前|曾经|(?<!往)(?<!标记)回退|一开始|那次|一度|原先是|本来是|旧版|旧的实现")),
    ("measure-narrative", re.compile(r"实测(过|出)|量过|测过|量出来")),
    ("audit-reference", re.compile(r"\baudit\b|审计")),
    ("history-en", re.compile(r"\bused to\b|\bmeasured\b|\bno longer\b|\bearlier (version|implementation|code)\b|\bpreviously\b|\boriginally\b")),
]


def strip_fences(text):
    """去掉围栏代码块，但保留行数（方便报行号）。"""
    return FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def live_files():
    out = []
    missing = []
    for name in ROOT_DOCS:
        p = ROOT / name
        if p.is_file():
            out.append(p)
        else:
            missing.append(name)
    for d in LIVE_DIRS:
        for p in sorted((ROOT / d).glob("*.md")):
            if p.is_file():
                out.append(p)
    return out, missing


def check_file(p, issues):
    rel = p.relative_to(ROOT).as_posix()
    raw = p.read_text(encoding="utf-8", errors="replace")
    lines = raw.split("\n")

    # 规范页里「禁止写法」的围栏本身是反例，豁免正文外的围栏内容。
    body = strip_fences(raw) if rel == "STYLE.md" else raw
    blines = body.split("\n")
    hist_lines = strip_fences(raw).split("\n")

    if not any(STATUS.match(line) for line in lines[:5]):
        issues.append((rel, 1, "status", 'H1 之后五行内缺 "> 状态：" 块'))

    for i, line in enumerate(blines, 1):
        for rule, rx in (("anchor-file", ANCHOR_FILE), ("anchor-bare", ANCHOR_BARE),
                         ("anchor-range", ANCHOR_RANGE), ("anchor-line", ANCHOR_LINE),
                         ("anchor-section", ANCHOR_SEC)):
            m = rx.search(line)
            if m:
                issues.append((rel, i, rule, m.group(0)))
                break
        m = ABS_PATH.search(line)
        if m:
            issues.append((rel, i, "abs-path", m.group(0)))

    for i, line in enumerate(hist_lines, 1):
        for rule, rx in HIST_RULES:
            m = rx.search(line)
            if m:
                issues.append((rel, i, rule, m.group(0)))
                break

    for i, line in enumerate(blines, 1):
        for m in LINK.finditer(line):
            text, target = m.group(2), m.group(3).strip()
            if not target:
                issues.append((rel, i, "empty-link", m.group(0)[:80]))
                continue
            if not text.strip():
                issues.append((rel, i, "empty-link-text", m.group(0)[:80]))
            t = target.split()[0]
            if t.startswith("<") and t.endswith(">"):
                t = t[1:-1]
            low = t.lower()
            if low.startswith(("http://", "https://", "mailto:", "tel:", "data:")) or t.startswith("#"):
                continue
            if t.startswith("/") or t.startswith("~"):
                continue  # 绝对路径由 abs-path 规则报
            pathpart = urllib.parse.unquote(t.split("#")[0])
            if not pathpart:
                continue
            q = p.parent / pathpart
            if not q.exists():
                issues.append((rel, i, "dead-link", t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true", help="有失败就 exit 1（check.sh 调用）")
    ap.parse_args()

    files, missing = live_files()
    if missing:
        print("FAIL 缺少活文档：" + "、".join(missing) + "（README/STYLE 由 Lead 维护）", file=sys.stderr)
        return 1
    issues = []
    for p in files:
        check_file(p, issues)

    print(f"活文档 {len(files)} 篇（README.md + STYLE.md + guide/reference/design/plans）")
    if issues:
        print(f"失败 {len(issues)} 条：")
        for rel, line, rule, msg in issues:
            print(f"  FAIL {rel}:{line}: [{rule}] {msg[:160]}")
        return 1
    print("ok  状态块齐全 · 无数字锚点 · 无绝对路径 · 无历史词 · 链接可解析 · 无空链接")
    return 0


if __name__ == "__main__":
    sys.exit(main())
