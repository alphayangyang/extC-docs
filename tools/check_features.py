#!/usr/bin/env python3
'''文档项目特性总表闸门：reference/features.md 与手册章节、证据路径双向对齐。

    python3 tools/check_features.py          报告
    python3 tools/check_features.py --gate   有失败 exit 1（check.sh 调用）

检查四件事：
  1. 每一行的手册章节（reference/ 下某个文件里的二级或三级标题）真的存在；
  2. reference/language.md 的每个二级、三级标题，与 reference/stdlib.md、reference/modules-cabi.md
     的每个二级标题，都至少被一行覆盖（加了新节必须进总表）；
  3. 状态只能是 实现 / 部分；
  4. 证据路径相对编译器仓库（EXTC_SRC）存在。找不到 EXTC_SRC 时这一项跳过。
'''

import argparse
import os
import pathlib
import posixpath
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get('EXTC_DOCS') or HERE.parent)
SRC = pathlib.Path(os.environ.get('EXTC_SRC') or ROOT.parent / 'extC_Compiler')
BT = chr(96)
TABLE = ROOT / 'reference' / 'features.md'
COVER = (('reference/language.md', 3), ('reference/stdlib.md', 2), ('reference/modules-cabi.md', 2))
STATUSES = ('实现', '部分')
LINK = re.compile(r'\[([^\]]*)\]\(([^)]*)\)')


def norm(s):
    s = s.replace(BT, '')
    s = re.sub(r'\s+', ' ', s).strip()
    if s.endswith('\u3002'):
        s = s[:-1]
    return s


def headings(rel, maxdepth):
    p = ROOT / rel
    if not p.is_file():
        return {}
    out = {}
    for line in p.read_text(encoding='utf-8').split('\n'):
        m = re.match(r'^(#{2,4})\s+(.*)$', line)
        if m and len(m.group(1)) <= maxdepth:
            out.setdefault(norm(m.group(2)), m.group(2).strip())
    return out


def cells(line):
    parts = line.strip().strip('|').split('|')
    return [p.strip() for p in parts]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gate', action='store_true', help='有失败就 exit 1（check.sh 调用）')
    ap.parse_args()

    if not TABLE.is_file():
        print('FAIL 缺少 reference/features.md（特性总表）')
        return 1

    have_src = SRC.is_dir()
    issues = []
    covered = {rel: set() for rel, _ in COVER}
    heads = {rel: headings(rel, depth) for rel, depth in COVER}
    rows = 0

    for i, line in enumerate(TABLE.read_text(encoding='utf-8').split('\n'), 1):
        if not line.strip().startswith('|'):
            continue
        cs = cells(line)
        if len(cs) < 4 or cs[0] in ('特性', '---') or set(cs[0]) <= set('-:'):
            continue
        rows += 1
        manual, status, evidence = cs[1], cs[2], cs[3]
        m = LINK.search(manual)
        if not m:
            issues.append((i, 'merge', '手册一栏要写成 [文件](文件) \u00b7 章节标题：' + manual))
            continue
        target = m.group(2).strip()
        if ' \u00b7 ' in manual:
            section = manual.split(' \u00b7 ', 1)[1]
        else:
            section = ''
        rel = posixpath.normpath(posixpath.join('reference', target))
        if rel not in heads:
            issues.append((i, 'target', '手册文件不在覆盖范围里：' + rel))
            continue
        if not section.strip():
            issues.append((i, 'section', '缺章节标题（文件后面要写 \u00b7 章节标题）'))
            continue
        key = norm(section)
        if key not in heads[rel]:
            issues.append((i, 'section', '手册里没有这个标题：' + section.strip()))
            continue
        covered[rel].add(key)
        if status not in STATUSES:
            issues.append((i, 'status', '状态只能是实现/部分，实为：' + status))
        paths = [p.strip().strip(BT) for p in evidence.split('\u00b7') if p.strip().strip(BT)]
        if not paths:
            issues.append((i, 'evidence', '缺证据路径'))
        elif have_src:
            for p in paths:
                if not (SRC / p).exists():
                    issues.append((i, 'evidence', '证据路径不存在：' + p))

    for rel, _ in COVER:
        for key, title in heads[rel].items():
            if key not in covered[rel]:
                issues.append((0, 'cover', rel + ' 的章节没有进总表：' + title))

    for i, kind, msg in issues:
        where = '第 ' + str(i) + ' 行 ' if i else ''
        print('FAIL ' + where + '[' + kind + '] ' + msg, file=sys.stderr)

    if not have_src:
        print('  --   跳过证据路径检查：找不到编译器仓库 ' + str(SRC))
    if issues:
        print('FAIL 特性总表：' + str(len(issues)) + ' 处不一致（' + str(rows) + ' 行）', file=sys.stderr)
        return 1
    total = sum(len(heads[rel]) for rel, _ in COVER)
    print('ok  特性总表：' + str(rows) + ' 行 · 手册章节覆盖 ' + str(total) + '/' + str(total) + ' · 证据路径存在')
    return 0


if __name__ == '__main__':
    sys.exit(main())