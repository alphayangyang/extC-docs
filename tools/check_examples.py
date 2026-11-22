#!/usr/bin/env python3
"""活文档里的 extC 示例必须真能编过 / 真能跑 —— 没闸门的例子会先烂。

    python3 tools/check_examples.py          报告
    python3 tools/check_examples.py --gate   有失败 exit 1（check.sh 调用）

规则（施工单 3.3，判据照抄编译器仓库 tools/check_doc_examples.py）：

* 围栏 extc（三个反引号 + extc）且含 fn main => 完整程序：extc --check-c 必须通过，再 --run 一次，
  要求退出码 0（超时算失败；示例应无输入、不发散）。
* 围栏 extc 且不含 fn main => 片段：上一行必须有 <!-- fragment -->，否则算"未标注片段"。
* 负例：上一行必须有 <!-- must-fail -->（旧标记 <!-- expect-error --> 兼容）：示例必须失败 ——
  编译失败算过；编译通过且含 fn main 时，--run 必须非零退出（运行期陷阱/事故演示）。
  编译又运行成功则算失败（标注与例子对不上）。
* 依赖外部夹具的程序（需要同目录的输入文件、.so 等）：上一行写 <!-- no-run -->，只做编译检查、不跑。
* 其它语言的围栏不检查。

编译器：环境变量 EXTC 优先；否则 EXTC_SRC/build/extc（EXTC_SRC 默认 ../extC_Compiler）。
找不到编译器时按 check.sh 跳过协议输出 "  -- 跳过：..." 并 exit 0。
"""

import argparse
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get("EXTC_DOCS") or HERE.parent)
LIVE_DIRS = ("guide", "reference", "design", "plans")
TMP = pathlib.Path("/tmp/extc-docex")
BT = chr(96)
FENCE = BT * 3


def pages():
    for name in ("README.md", "STYLE.md"):
        p = ROOT / name
        if p.is_file():
            yield p
    for d in LIVE_DIRS:
        for p in sorted((ROOT / d).glob("*.md")):
            if p.is_file():
                yield p


def extc_blocks(text):
    """-> [(起始行号, 片段文本, 标注)]；标注取 fragment / must-fail / no-run / ""。"""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        if lines[i].strip().startswith(FENCE):
            lang = lines[i].strip()[len(FENCE):].strip()
            if lang == "extc":
                start = i
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith(FENCE):
                    j += 1
                body = "\n".join(lines[start + 1:j])
                mark = lines[start - 1] if start > 0 else ""
                if "<!-- fragment" in mark:
                    tag = "fragment"
                elif "<!-- must-fail" in mark or "<!-- expect-error" in mark:
                    tag = "must-fail"
                elif "<!-- no-run" in mark:
                    tag = "no-run"
                else:
                    tag = ""
                out.append((start + 1, body, tag))
                i = j
        i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true", help="有失败就 exit 1（check.sh 调用）")
    ap.parse_args()

    src = pathlib.Path(os.environ.get("EXTC_SRC") or (ROOT.parent / "extC_Compiler"))
    extc = os.environ.get("EXTC") or str(src / "build" / "extc")
    if not os.path.isfile(extc):
        print(f"  -- 跳过：找不到 extc（EXTC 或 {src}/build/extc）；示例闸门不检查")
        return 0

    TMP.mkdir(parents=True, exist_ok=True)
    checked, fragments, negative, compile_only, bad = 0, 0, 0, 0, []
    for p in pages():
        rel = p.relative_to(ROOT).as_posix()
        for n, body, tag in extc_blocks(p.read_text(encoding="utf-8", errors="replace")):
            if tag == "fragment":
                fragments += 1
                continue
            f = TMP / (rel.replace("/", "_") + f"-{n}.extc")
            f.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")
            try:
                r = subprocess.run([extc, "--check-c", str(f)], capture_output=True, text=True, timeout=180)
            except subprocess.TimeoutExpired:
                bad.append(f"{rel}:{n}: extc --check-c 超时")
                continue
            if tag == "must-fail":
                negative += 1
                if r.returncode != 0:
                    continue
                if "fn main" not in body:
                    bad.append(f"{rel}:{n}: 标了 must-fail，但片段既没编失败、也没有 fn main")
                    continue
                try:
                    run = subprocess.run([extc, "--run", str(f)], capture_output=True, text=True,
                                         stdin=subprocess.DEVNULL, timeout=30)
                except subprocess.TimeoutExpired:
                    bad.append(f"{rel}:{n}: 负例 --run 超时（期望失败，不该发散）")
                    continue
                if run.returncode == 0:
                    bad.append(f"{rel}:{n}: 标了 must-fail，但示例编过且运行成功（退出码 0）—— 要么改标注，要么改例子")
                continue
            if "fn main" not in body:
                bad.append(f"{rel}:{n}: extC 片段没有 fn main，也没有 <!-- fragment --> / <!-- must-fail --> 标注")
                continue
            if r.returncode != 0:
                tail = (r.stderr or r.stdout).strip().split("\n")[-4:]
                bad.append(f"{rel}:{n}: 示例编不过（extc --check-c rc={r.returncode}）\n      " + "\n      ".join(tail))
                continue
            if tag == "no-run":
                compile_only += 1
                continue
            checked += 1
            try:
                run = subprocess.run([extc, "--run", str(f)], capture_output=True, text=True,
                                     stdin=subprocess.DEVNULL, timeout=30)
            except subprocess.TimeoutExpired:
                bad.append(f"{rel}:{n}: extc --run 超时（示例应无输入、不发散）")
                continue
            if run.returncode != 0:
                tail = (run.stderr or run.stdout).strip().split("\n")[-4:]
                bad.append(f"{rel}:{n}: 示例跑不过（extc --run rc={run.returncode}）\n      " + "\n      ".join(tail))

    print(f"extC 示例：完整程序 {checked} 段（编过且跑过）· 仅编译 {compile_only} 段（no-run）· "
          f"片段 {fragments} 段跳过 · 负例 {negative} 段已核")
    if bad:
        print(f"失败 {len(bad)} 条：")
        for b in bad:
            print("  FAIL " + b)
        return 1
    print("ok  活文档里的 extC 示例全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
