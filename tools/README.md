# 文档项目闸门

全部脚本纯 python3 标准库，不依赖网络与第三方包。在文档项目根目录跑 ./check.sh 即可。

| 脚本 | 检查什么 | 豁免 |
|---|---|---|
| tools/check_style.py | 活文档（README.md、STYLE.md、guide/reference/design/plans 下的 .md）的状态块、数字锚点、绝对路径、历史词、相对链接可解析、空链接 | devlog/ 与 archive/ 是历史材料，整体豁免；STYLE.md 的「禁止写法」围栏内是反例，按正文判定 |
| tools/check_index.py | README.md 的活文档链接集合 == guide 4 + reference 3 + design 16 + plans 5 + STYLE.md，无孤儿、无死条目 | devlog/archive/跨仓库链接不计入集合（其可解析性由 check_style 管） |
| tools/check_examples.py | 活文档里 extc 围栏：含 fn main 的完整程序必须 extc --check-c 通过并 --run 退出 0；片段必须标 <!-- fragment -->；负例标 <!-- must-fail -->（兼容旧 <!-- expect-error -->）且必须编不过 | 其它语言围栏不检查；找不到编译器时整项跳过（输出以 "  --" 开头） |
| tools/check_changelog.py | devlog/changelog/YYYY-MM.md 每条 ## YYYY-MM-DD · 标题 落在正确月份页；README.md 的月份表与页一致（--write 重生成） | 日期字段存在历史笔误（如 11-85），只校验月份、不校验日是否真实存在 |

用法：

    ./check.sh                          # 全部闸门
    ./check.sh docs                     # 不存在此参数；check.sh 总跑全部
    EXTC_SRC=../extC_Compiler ./check.sh
    EXTC=/path/to/extc ./check.sh

环境变量：EXTC_DOCS（默认脚本所在目录）、EXTC_SRC（默认 ../extC_Compiler）、EXTC（默认 EXTC_SRC/build/extc）。

自测方法（闸门必须能红能绿）：把本目录复制到临时目录，造一个缺状态块、一个 file.c:123、一个死链、
一个未标注片段，跑 ./check.sh 应为红；恢复干净副本再跑应为绿。示例编译项依赖编译器，
没有 build/extc 时记"跳过"。
