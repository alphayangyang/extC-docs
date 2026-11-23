# 体量收敛：把「同一件事的几种答案」删到一种

> 状态：**计划** —— 不是现状。做完的项在文内标「完成」，剩下的按顺序排期。最后核对 2026-11-23。

这份清单是[核心](../design/CORE.md)预算表的执行版。每一项都是行数、判据数、语料里用了几次，以及
「能不能用核心表达」。删之前先看**依赖**：有些项必须等 `slice` 收成纯借用才动，顺序反了会把库改两遍。

口径：行数用 `wc -l`；判据数按 `tests/<套件>/run.sh` 里的用例条目；语料用量按 `use std::<模块>`
的出现文件数。数字是 2026-11 的，删完要更新。

## 一、候选与结论

| 项 | 现状 | 判据 | 语料用量 | 结论 |
|---|---|---|---|---|
| **计数层**（`src/back/reclaim.c` 的计数模式） | 计数分支在发射器里按开关丢弃 | `tests/reclaim-perf/count*` | 0（不默认开） | **推迟**：事件档（`EXTC_RC_SWEEPFREE=1`）与「能证明无环的 unit 自动开计数且不扫」（`unitAllAcyclic`）都压在它上面，`tests/reclaim-acyclic` 与论文的 acyclic 消融臂同时依赖它 |
| **容器** | `prelude.extc` 357 行（不含容器）+ `data/vector.extc` 170 行 + `data/buf.extc` 409 行 | 一套（`tests/stl`、`tests/reclaim-shapes`） | 128 个 .extc 用 `vector<` | **完成**：容器只有 `vector<T>`（存储是 `buf<T>` 的地址预留，增长即归还旧块），`buf`/`block` 退出入门手册 |
| **映射三个**：`hashMap` / `map` / `linMap` | `hashMap.extc` 561 行 / `map.extc` 1,134 行（`linMap`、`linSet` 在同一个模块里） | 各一套（`tests/hashmap`、`tests/map`、`tests/linmap`） | `hashMap` 33 个文件、`map` 36 个文件 | **完成一半**：模块从三个收成两个；`hashMap` 与 `map` 的依据是键能力不同（`hashMap` 要 `i64` 键、`map` 要 `K: <`），等「键类型能提供 `hash()`」或「`map` 接受只有 `==` 的键」之后再合并 |
| **两套 JSON**：`std::json` 的 DOM + `any` 的文本化 | 1,186 行 + 运行期文本 | 各一套 | 40 | **留一条路**：`std::reflect::json(ref any)` 打任意值；DOM 只用于「解析后反复查询」的场景 |
| **两套输出**：`io::cout` 链 + `print`/`println` 内建 | 内建 2 个 + `io` 的缓冲机制 | 两套都测 | 1,379（`cout`） | **留内建**：`print`/`println` 是 90% 的用法；`io::cout` 保留但文档上作为「需要控制格式/分块写」的入口 |
| **两种并行**：`par i in ..` + `parallel::run` | `par` 是语法、`run` 是内建 | 各一套 | 42 / 10 | **留 `par`**：`parallel::run` 只在需要「手工分块传偏移」时用；等 `par` 支持二维折叠后删 |

已删掉的两类重复答案：`varArray<T>`（并入 `vector<T>`）、`linMap` 独立模块（并入 `map` 模块）。
池（`@place` / `poolSlice` / `poolResize` / `stl::pool`）整条机制已退出编译器与标准库，
容器的存储改为 `buf<T>` 的地址预留，所以本清单不再有「池特权」这一类项。

## 二、顺序（每步都要闸门绿）

1. **`slice` 收成纯借用**（独立项）：它决定视图语义；容器合并已按 `buf<T>` 之上的一层完成，不依赖它。
2. **删计数层**：先删运行时分支与 `EXTC_RC_NOCOUNT` 相关产物，再把 `tests/reclaim-perf` 里
   依赖计数的用例改成「扫描臂」判据。注意：论文里「counting on」是一个消融臂，删掉要同步改论文
   的消融表与 limitation（这一步要单独提交，附论文改动）。
3. **合并容器**：完成（`vector<T>` 一套，新增 `insert` / `removeAt` / `truncate` / `reserve`）。
4. **合并映射**：已把 `linMap` / `linSet` 搬进 `map` 模块；下一步是让 `map` 也接受只有 `==` 的键，
   那时 `hashMap` 就只剩「`i64` 键的最快档」一个理由。
5. **合并 JSON**：`std::json` 的 DOM 与 `reflect::json` 各留一个入口，删掉重复的转义实现
   （两份转义是错误来源）。
6. **合并输出与并行**：`parallel::run` 标 `@private` 或删除；`io::cout` 文档降级。
7. **清公开面**：每步之后重跑 `python3 tools/manual_surface.py`，把新增的 `@private` 记进
   [surface](../../extC_Compiler/docs/surface.md)，公开成员只许降。

## 三、每步的验收

- `tests/run.sh` / `smoke` / `docs` / `nobench` 全绿，`ast-freeze` 不涨。
- 相关套件用例数**不降**（合并的项要把两边的判据都保留到一个套件里）。
- 性能不回归：合并容器/映射后跑 `bench/app`（log/route/session）与 `bench/crazy`，比值在
  噪声内；峰值内存**必须**改善（8M 元素一份预留 64 MB）。
- 文档同步：[参考手册](../reference/stdlib.md)、[surface](../../extC_Compiler/docs/surface.md)、changelog（一句症状 + 一句结构
  + 一句判据）。

## 四、不做的事

- 不为了行数删功能：删的是「第二次答案」，不是能力。
- 不动 `coroutine` 那条按名字派发的路径（4 处）——它是「协议」不是容器，等并发回收器定了再说。
- 不删 `any`/`dyn` 任何一方：它们是「结构 vs 名义」两种视图，共用 16 字节载体，不是重复答案。

## 五、前置：决定后面能删什么的两件事

### 1. 返回视图的深度还没有记录

`FuncDef` 只有 `Type *ret`，没有函数级「返回值借自谁」的记录；返回处的深度按语法重算，再被
`poolCallDepth()` 抬到本函数块层级，随后又被 `promoteInto2()` 当成「分配点」改写。调用点不读
callee 的任何记录，而是按自己的实参重算同一公式。

后果是精度损失：一个「返回自己参数存储里的视图」的包装函数，其结果在调用点被当成新分配，于是
要求它活得比实际需要更久 —— `tests/genmatrix` 里那类形状因此被保守拒绝。修法是给 `FuncDef` 记
`retBorrowArg` / `retBorrowField`，让调用点按 `max(slotDepth(arg), 该字段的存储深度)` 取数，
并把 `promoteInto2` 的要求下沉到存储的 `src`。这条改动也是「视图」语义收敛的前置。

### 2. 视图作为实参、由被调方写进元素：还没挡住

<!-- fragment -->
```extc
fn stash(a: mut slice<slice<i64>>, s: slice<i64>) { a[0] = s }
stash(a[..], w.view())     /* 视图进了别人的元素；之后 w 增长再读 a[0][0] 是 UAF */
```

调用点规则只在该参数的效果摘要带「可能保存」位时触发；这里被存下去的是 `a` 的元素，摘要把
「保存」记在 `a` 上，`s` 没有被标。要挡它需要按实参形状推「被调方可能把第 i 个视图参数放进某个
容器」，比字段/元素两条规则大一圈。暂记为洞，判据（ASan 干净）等实现后补。

### 3. 已知缺陷：返回本地容器的视图会悬垂

函数返回自己帧里容器的 `view()` 时编译照过，返回后那块预留已经归还 —— 生成 C 在收视图之后立刻
`release`。`vector`、`buf`、`string` 同病，修法与「视图跨函数要过 `borrow()` 守卫」同一条路
（静态拒绝这种返回并提示 `snapshot()`），细节见[库面计划](LIBRARY-SHAPE.md)的「容器面只剩一个 `vector<T>`」节。
