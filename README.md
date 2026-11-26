# extC 文档

> 状态：**索引** · 对应 extC 0.0.1-alpha · 最后核对 2026-11-23

extC 是一门编译到 C11 的系统语言：没有虚拟机、没有共享运行库，作用域 arena + 区域回收决定了大部分内存
不用写释放代码。**这个仓库是 extC 唯一的文档来源**——现在有什么、怎么用、为什么这么设计、还差什么。

配套的编译器在兄弟目录 `../extC_Compiler`（两个仓库作为兄弟目录一起克隆，名字保持 extC_Compiler 与 extc-docs）。
编译器仓库的 `docs/` 只留随代码一起生成或与用例绑定的四页：驱动开关页、公开面清单、语法糖手册、注释规范；
其余都在这里，别在编译器仓库里找手册。

## 从哪开始

| 我是谁 | 先读 |
|---|---|
| 第一次听说 extC | [项目一句话](guide/getting-started.md) · 编译器仓库的 `README.zh.md` |
| 要写 extC 程序 | [上手](guide/getting-started.md) → [语言现状](reference/language.md) → [标准库](reference/stdlib.md) |
| 关心内存/回收 | [内存回收（通俗版）](guide/memory-model.md) → [回收机制](design/RECLAMATION.md) |
| 要调 C 或用 C 调 extC | [模块与 C 互操作](reference/modules-cabi.md) |
| 要让编辑器认识它 | [编辑器支持](guide/editor.md) |
| 要改编译器 | [编译器内部结构](guide/internals.md) → [六条核心决定](design/CORE.md) |
| 想知道还差什么 | [待做清单](plans/TODO.md) |

## 文档地图

文档分四类（按"读者想问什么"分，不按文件新旧分）：指南（怎么用）、参考（有什么）、解释（为什么）、计划（还差什么）。
开发记录与历史材料单独放在 `devlog/` 与 `archive/`，可信度低，别当现状读。

### 指南 `guide/` —— 怎么用

| 页面 | 内容 |
|---|---|
| [上手](guide/getting-started.md) | 依赖 · 构建 · 编译器全部选项 · 验收怎么跑 |
| [内存回收](guide/memory-model.md) | 通俗讲法：作用域是地基、回收器兜什么、停顿与代价 |
| [编译器内部结构](guide/internals.md) | 流水线 · 分层 · 闸门体系 · 构建产物 |
| [编辑器支持](guide/editor.md) | VS Code 扩展：诊断/符号/悬停/补全，连不通怎么查 |
| [风格指南](guide/style.md) | 把程序写成对象：方法形态、构造、错误、数据布局、命名 |

### 参考 `reference/` —— 有什么

| 页面 | 内容 |
|---|---|
| [语言现状](reference/language.md) | 语法、类型、内存模型、错误与逃生舱、注解、语句与表达式 |
| [标准库现状](reference/stdlib.md) | prelude 与各模块的公开面 |
| [模块与 C 互操作](reference/modules-cabi.md) | 模块系统 · `extern!` · 导出 · 动态加载 |
| [特性总表](reference/features.md) | 每个语言/标准库/互操作特性的手册锚点、状态与证据路径 |

### 解释 `design/` —— 为什么这么设计

| 页面 | 一句话 |
|---|---|
| [CORE](design/CORE.md) | 六条不许破的决定与预算表——动别处之前先看这页 |
| [TYPE-MODEL](design/TYPE-MODEL.md) | 值、引用、复合，各自装在什么载体里；拷贝/移动/借出/快照 |
| [MEMORY-MODEL](design/MEMORY-MODEL.md) | 三种存储（帧 / 板块 / 对象表）与"该用哪个"的判据 |
| [ALLOCATORS](design/ALLOCATORS.md) | 分配器分层：arena、板块、对象表各管什么 |
| [BUF-INVARIANT](design/BUF-INVARIANT.md) | 可增长数组：一片预留、四个动作、视图何时失效 |
| [HASHMAP](design/HASHMAP.md) | 哈希表：三列平坦存储、值内联、不承诺元素地址 |
| [CONTAINER-OWNERSHIP](design/CONTAINER-OWNERSHIP.md) | 容器与元素的所有权规则（R1–R5）|
| [DESTRUCTORS](design/DESTRUCTORS.md) | 析构：`@drop` 的全部时机与顺序 |
| [RECLAMATION](design/RECLAMATION.md) | 四层回收：按分配点选策略、运行期何时整体删掉 |
| [WEAK-REFS](design/WEAK-REFS.md) | 弱引用：24 字节句柄、目标死亡零工作 |
| [PARALLEL](design/PARALLEL.md) | `par` 的证明义务；线程与回收的规则 |
| [EFFECTS](design/EFFECTS.md) | `request`/`suspend`/`handle`：等待是类型、驱动器是词法作用域 |
| [FUSION](design/FUSION.md) | 视图融合：什么形状能合、逐位一致的硬约束 |
| [ARRAY](design/ARRAY.md) | 数组与视图语义、rank 与形状 |
| [MODULES](design/MODULES.md) | 模块身份、导入、门面、所有权边界 |
| [VOCABULARY](design/VOCABULARY.md) | 词汇表：一词一义，以及命名冲突的候选方案 |

### 计划 `plans/` —— 还差什么

| 页面 | 内容 |
|---|---|
| [TODO](plans/TODO.md) | 全项目唯一的待做清单（做完搬进 guide/reference 或删掉）|
| [TRIM](plans/TRIM.md) | 体量收敛：哪些重复答案先删、按什么顺序 |
| [LIBRARY-SHAPE](plans/LIBRARY-SHAPE.md) | 标准库该长什么样 |
| [CONCISENESS](plans/CONCISENESS.md) | 简洁度量尺与糖清单 |
| [ELEMENT-REFS](plans/ELEMENT-REFS.md) | 元素引用：借容器里的东西而不拷贝 |

## 开发记录 `devlog/` 与历史 `archive/`

| 目录 | 是什么 | 可信度 |
|---|---|---|
| [`devlog/changelog/`](devlog/changelog/README.md) | 开发历史（按月分页，索引在页首）| 当时的事实；日期字段有历史笔误，按内容顺序读 |
| [`devlog/analysis/`](devlog/analysis/README.md) | 测量、归因、复核报告（证据，不是手册）| 写作当时成立；数字有口径，路径锚点钉在当时的树 |
| [`devlog/conciseness/`](devlog/conciseness/README.md) | 简洁度度量语料与脚本 | 基准语料 |
| [`archive/`](archive/README.md) | 旧时代快照（旧树）| **只作考古，不要当现状读** |

## 怎么验证这些文档

文档里的示例是要跑的判据，不是装饰：

```sh
./check.sh        # 状态块 · 无行号锚点 · 无历史词 · 链接可解析 · 示例能编译
```

闸门需要能用的编译器（默认 `../extC_Compiler/build/extc`）：先在编译器仓库 `make -j`，或用环境变量
`EXTC` 指定别的二进制。编译器仓库还用自己的 `./check.sh docs` 核对三件事：驱动开关页与 `extc --help`
一致、公开面清单与源码一致、语法糖手册与 `tests/sugar/` 双向点名。

GitHub Actions 里由 `.github/workflows/docs.yml` 把编译器仓库 checkout 到子目录 `extC_Compiler/` 并
`make -j`，再跑同一套 `./check.sh`；CI 中任何"跳过"都算失败。要在本地复现这个布局，把编译器克隆到
`extC_Compiler/` 并设 `EXTC_SRC=$PWD/extC_Compiler`。

## 维护

写作规范见 [STYLE.md](STYLE.md)。两条硬规矩：**引用符号不引行号**（行号必漂），**README 是本项目唯一索引**
（新增/改名/删除活文档必须同步本页，`check_index` 会红）。

## 版本与适用范围

- 本项目的"现状"指 extC `0.0.1-alpha`（Linux x86_64 / WSL2）；alpha 阶段语义与 API 都可能变。
- 页面里的性能数字只在标注的口径下成立；要引数字，跑对应 `bench/` 或读 `devlog/analysis/` 的原始报告。
- 页面状态块（`> 状态：…`）写的就是这篇的可用程度：**当前口径**（现在的事实）、**设计稿**（未实现）、
  **研究稿**（候选方案）、**计划**（待做）、**索引**（本页）。
