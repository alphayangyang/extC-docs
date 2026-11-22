# 简洁度语料（devlog/conciseness）

这里是**度量语料与脚本**，不是文档：四个程序各写一份 extC 与一份等价的 Python，用同一把尺子量
"同样的事写出来有多长"。数字属于基准语料（写作当时的口径），不代表任何实现承诺。

| 文件 | 是什么 |
|---|---|
| `matmul.extc` / `matmul.py` | 矩阵乘：循环与下标 |
| `stats.extc` / `stats.py` | 统计：累加、分支、输出 |
| `stencil.extc` / `stencil.py` | 模板计算：邻域访问 |
| `wordcount.extc` / `wordcount.py` | 词频：字符串与关联容器 |
| `stats.py` | 统计脚本：量行数/记号数并输出对照表 |

用法：`python3 devlog/conciseness/stats.py`（在文档仓库根目录跑）。`.extc` 侧可以用
`../extC_Compiler/build/extc --check-c` 核对语法仍然成立，但它们不是编译器测试套件的一部分；
结论与糖清单见 `plans/CONCISENESS.md`。
