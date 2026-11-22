# 分析报告（devlog/analysis）

这里是**证据报告**，不是手册：测量、归因、复核、行号映射与模型草案都放这里。每一篇回答一个具体问题，
数字来自写作当时的那棵树（file:line 锚点也钉在当时的树上），**不能当现状读**——现状以 `guide/`、
`reference/`、`design/` 为准。

## 读之前先知道

- **锚点会漂**：报告里的 `file.c:123` 指向写作当时的源码行；代码搬过之后行号就对不上，按语义找，
  不要按行号找。
- **数字有口径**：同一指标在不同报告里可能换了机器、温度、语料或测量方式。每篇开头/表格里都写了
  当时的口径（`taskset`、REPS、min/median、冻结树版本）。跨报告对比前先对齐口径。
- **不是承诺**：报告里的"候选方向""下一步"只是当时的判断，是否落地看 `plans/TODO.md` 与代码。

## 按主题

### 模型与总览

| 报告 | 一句话 |
|---|---|
| `MEMORY-MODEL-CURRENT.md` | 现有内存管理模型的源码级技术文档（区域、RcPlan、清扫、基质） |
| `MEMORY-FIRST-MODEL.md` | memory-first 模型草案（E16）|
| `GC-MODEL-DRAFT.md` | GC 策略的 Roofline 模型草案 v0.1（正式版见 `GC-ROOFLINE.md`）|
| `GC-ROOFLINE.md` | Roofline 式形式化模型与优化方案 v2.0（停顿、预算、成本上界）|
| `QUOTA-MODEL.md` | 字节节奏配额（P）与惰性 freelist（B）的形式化 |
| `MODEL-UPDATE-P1.md` | P1 落地后对配额模型、memory-first 模型与 roofline 脚本的修正 |
| `COMPILE-SIDE.md` | 编译侧内存决策的事实清单（哪些决策在编译期做）|
| `RUNTIME.md` | 运行时内存管理的事实清单（以源码与产物为准）|

### 实现报告

| 报告 | 一句话 |
|---|---|
| `P0-PROTOTYPE.md` | P0 原型：页归还、惰性 freelist、字节节奏回收 |
| `P0-IMPL.md` | P0 落地：字节配额（P）+ 懒复用链重建（B）|
| `P1-ADMISSION.md` | 分配准入按请求字节 |
| `P1-CLOSING-QUEUE.md` | region 级延迟关闭队列 |
| `P1-REGIONFREE-BATCH.md` | regionFree 延迟释放队列 + 有界排空 |
| `P1-QUOTA-FASTPATH.md` | 配额记账快路、elide O(1)、ELIDE_VERIFY 收口 |
| `P1-RQ3-CHUNK.md` | `EXTC_RC_SCAN_CHUNK` 取舍实验 |
| `P1-SEG-TAIL.md` | 单步 p99.9 的真实构成：续扫段成本、宿主噪声、chunk 的内存代价 |
| `P1-SLAB-QUANTUM.md` | slab 栅格从 1 MiB 收到 128 KiB 的墙钟收益 |
| `P1-STEP-TAIL.md` | markStep / 续扫段超长步（58–871 µs 尾部）的子相位归因 |
| `P1-ZEROINIT-FILL.md` | 清零跳表 + 块整块发槽 + 512 KiB 栅格 |
| `P1-7-SWEEP-ELIDE.md` | 全死 slab 批量重置（sweep elision）：实现、证据、限制 |
| `P1-8-MUTATOR-COST.md` | 分配点 / 屏障微优化的取证、实现与实测 |
| `P1-PARITY.md` | 四形状与 C++/Rust 的持平台账 |
| `CONVERGED-MODEL-PROTO.md` | 收敛模型原型：chunk 记账 + 水位归还的 A/B 实测 |
| `T2-CAPACITY-AND-T1-WIDENING.md` | T2 清扫的容量成本与 T1 拓宽的收益 |
| `UNLINK-DEFERRAL.md` | 大对象跨区引用撤销：为什么摊到多步不是答案 |
| `COUNT-TIER-ADR.md` | 计数路线（event tier）去留的 ADR |

### 测量与标定

| 报告 | 一句话 |
|---|---|
| `MEASUREMENTS.md` | 内存管理模型的本机基线测量 |
| `MEASUREMENTS-GC-P0.md` | 阶段 0 门禁基线与 after（G8/G9/G4/G1/G12–G17）|
| `MEASUREMENTS-P0-IMPL.md` | P0 实现（按字节配额 + 惰性 freelist）的 before/after |
| `MEASUREMENTS-P1.md` | P1 四项落地的实测与判定（chunk / 配额记账 / regionFree 批处理 / G1② 通道拆分）|
| `MEASUREMENTS-TIER1.md` | 事件档（tier 1）的自动接线、税、内存与停顿 |
| `MEASUREMENTS-V2-AFTER.md` | `bench/gc/v2` 重测与旧数据对比（FREEZE v4）|
| `CALIBRATION.md` | GC 模型参数标定（阶段 3）|
| `ALLOC-COST.md` | 分配成本归因 |
| `RESERVE-GROWTH.md` | 预留地址 + 按需 commit 取代拷贝增长的原型实测 |
| `TABLE-REDESIGN-PROTO.md` | 表存储八种模型在同一 workload 上的对拍 |
| `ARENA-CONTAINERS.md` | arena 手写容器 vs pool 容器的五条对照 |
| `VIPER-CROSSLANG.md` | Viper 1.0.6-dev.194 与 extC 的同卡具对比 |
| `WIN-MINGW.md` | Windows / MinGW 跨 OS 复核实验 |
| `CORPUS-TORTURE.md` | 语料扩容：真实程序与对抗程序 |
| `WMARK-REACH.md` | wmark 的覆盖面：大槽类型与跨区边在语料里的常见度 |
| `EXTENT-R1.md` | extent 的三个未知量：VA 预算 / THP×归还 / slack 策略 |

### 复核与审计

| 报告 | 一句话 |
|---|---|
| `AUDIT-GC-P0.md` | 阶段 0–2 GC patch 的独立复核（含冻结树静态核对）|
| `AUDIT-MEMORY-MODEL.md` | `MEMORY-MODEL-CURRENT.md` 的源码逐条核对 |
| `AUDIT-P0-IMPL.md` | 字节配额 + 惰性 freelist 落地的独立复核 |
| `AUDIT-P1.md` | P1 四项改动与文档口径的独立复核 |
| `AUDIT-P1-RESPONSE.md` | AUDIT-P1 的处置记录 |
| `DOC-AUDIT.md` | 文档断言 vs 源码对账 |
| `GC-STATUS.md` | 回收运行期的完成度与门禁地图 |

### 行号 / 引用映射

| 报告 | 一句话 |
|---|---|
| `REFS-V4.md` | `MEMORY-MODEL-CURRENT.md` 中 reclaim.c 行号引用的 v4 权威映射 |
| `REFS-V7.md` · `REFS-V7-BATCH2.md` | reclaim.c 行号 v5/v6 → v7 的语义映射与全量复核 |
| `REFS-V18.md` · `REFS-V21.md` · `REFS-V23.md` · `REFS-V24.md` · `REFS-V25.md` · `REFS-V28.md` · `REFS-V29.md` · `REFS-V30.md` · `REFS-V31.md` · `REFS-V33.md` · `REFS-V34.md` · `REFS-V35.md` · `REFS-V36.md` | 相邻版本之间 reclaim.c 的行号换算表（每篇一波改动）|
| `REFS-E2.md` · `REFS-E3.md` · `REFS-CODEGEN-V4.md` | codegen.c 的分节坐标、行号换算与引用语义重建 |

### 子目录

- `archive/` —— 更早的冻结报告（如 `GC-ROOFLINE-v1.0-567l.md`）；与 `archive/` 同规矩，只作考古。
- `model/` —— Roofline 模型脚本与生成的表（`roofline.py`、`roofline-table.md`、`roofline.png`）。
- `evidence/` —— 报告里的小段 C 样例（`example-alloc-in-block.c`、`example-new.c`）。
