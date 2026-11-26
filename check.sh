#!/usr/bin/env bash
# 文档项目闸门：样式 -> 索引 -> 特性总表 -> 示例 -> 历史索引
# 用法：./check.sh
#       EXTC_SRC=/path/to/extC_Compiler ./check.sh   指定编译器仓库（默认 ../extC_Compiler）
#       EXTC=/path/to/extc ./check.sh               指定编译器二进制
# 任一闸门失败则整体非零退出；找不到编译器时示例闸门记"跳过"，不算失败。

DOCS_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -z "$EXTC_DOCS" ]; then EXTC_DOCS="$DOCS_DIR"; fi
if [ -z "$EXTC_SRC" ]; then EXTC_SRC="$DOCS_DIR/../extC_Compiler"; fi
export EXTC_DOCS EXTC_SRC
cd "$DOCS_DIR" || exit 1

ok=0
skip=0
fail=0
summary=""

run_gate() {
  name="$1"
  shift
  echo ""
  echo "== $name"
  out=$("$@" 2>&1)
  rc=$?
  printf '%s\n' "$out"
  if [ "$rc" -ne 0 ]; then
    fail=$((fail + 1))
    summary="$summary
FAIL  $name"
  elif printf '%s\n' "$out" | grep -q '^  --'; then
    skip=$((skip + 1))
    summary="$summary
跳过  $name"
  else
    ok=$((ok + 1))
    summary="$summary
ok    $name"
  fi
}

run_gate "样式：状态块 / 数字锚点 / 绝对路径 / 历史词 / 链接" python3 "$DOCS_DIR/tools/check_style.py" --gate
run_gate "索引：README 与活文档集合一致" python3 "$DOCS_DIR/tools/check_index.py" --gate
run_gate "特性：总表覆盖每章手册，证据路径存在" python3 "$DOCS_DIR/tools/check_features.py" --gate
run_gate "示例：活文档里的 extC 围栏编译并运行" python3 "$DOCS_DIR/tools/check_examples.py" --gate
run_gate "历史：changelog 月份页与索引一致" python3 "$DOCS_DIR/tools/check_changelog.py" --gate

echo ""
echo "== 汇总"
printf '%s\n' "$summary" | sed '/^$/d'
echo "ok $ok · 跳过 $skip · 失败 $fail"
if [ "$fail" -ne 0 ]; then
  exit 1
fi
exit 0
