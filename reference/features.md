# 特性总表：手册章节与证据的对照

> 状态：当前口径（最后核对 2026-11-26）

这张表回答一个问题：手册里的每一节对应哪种能力、到什么程度、由哪份证据证明。
`tools/check_features.py` 双向核对它：表里每一行指向的手册章节必须真的存在（标题改了不跟着改，闸门红）；
`reference/language.md` 的每个二级、三级标题都必须在表里出现（加了一节却没进总表，闸门红）。

加一门语言特性要**同时**动三处：手册（`reference/language.md` / `reference/stdlib.md`）、本表、
证据（`tests/` 或 `examples/` 下的用例）。只改手册不改本表，闸门红；只加用例不加手册，等于没发布。

状态只有两种：

- `实现`：手册里写的形状都能编过并跑出结果，边界写在手册那一节里。
- `部分`：只有手册写明的子集成立，该节写明缺哪一块；再往后做的进 `plans/`。

证据一栏是**路径**，相对编译器仓库根解析；每条都在 `tests/` 或 `examples/` 里，闸门会检查它存在。

## 语言：`reference/language.md`

| 特性 | 手册 | 状态 | 证据 |
|---|---|---|---|
| 一个源文件编成可执行文件，入口是 main | [language.md](language.md) · `1. 一个完整的程序` | 实现 | `examples/hello.extc` |
| 注释、标识符、字面量、换行与分隔 | [language.md](language.md) · `2. 词法` | 实现 | `examples/chars.extc` |
| 记号与字面量的写法（整数/浮点/字符/字符串） | [language.md](language.md) · `2.1 记号` | 实现 | `examples/float-literal-forms.extc` |
| f-string 插值与格式 | [language.md](language.md) · 2.2 格式化字符串 `f"…"` | 实现 | `tests/fstring` |
| 类型是编译期的，只有值/引用/载体三类 | [language.md](language.md) · `3. 类型` | 实现 | `examples/types.extc` |
| 整数位宽、浮点、bool、u8 字符串视图 | [language.md](language.md) · `3.1 内建类型` | 实现 | `examples/types.extc` |
| struct、两种枚举、定长数组、视图、函数类型的构造与零值 | [language.md](language.md) · `3.2 聚合` | 实现 | `examples/enums.extc` · `examples/payload-enum.extc` |
| 每种类型的零值，以及字面量怎么落到目标类型 | [language.md](language.md) · `3.3 零值与字面量适配` | 实现 | `examples/canary-zero-array-nullref.extc` |
| 显式转换的写法与窄化规则 | [language.md](language.md) · `3.4 转换` | 实现 | `examples/narrow-wrap.extc` |
| 函数指针与闭包值、捕获怎么进环境 | [language.md](language.md) · 3.5 可调用的值：`fn(...)` 与闭包 | 实现 | `tests/lambda` |
| 泛型实例里的闭包环境布局 | [language.md](language.md) · `3.6 泛型体里的 lambda：环境按实例布局` | 实现 | `examples/instance-closure.extc` |
| any 的装箱与拆箱 | [language.md](language.md) · 3.7 动态值 `any`：类型只在运行期知道 | 实现 | `tests/any` |
| 在 any 上调用动态方法 | [language.md](language.md) · 3.8 `any` 上的动态方法调用 | 实现 | `tests/any` |
| 从 JSON 读出 any 并按类型分发 | [language.md](language.md) · 3.10 读一个运行期才知道类型的值：`json::json` / `json::typeName` | 实现 | `tests/json` |
| any 拥有自己的载荷（与 dyn 的借语义相对） | [language.md](language.md) · 3.9 `any` 拥有它装的值 | 实现 | `tests/any` |
| 泛型函数与泛型类型，按实例单态化 | [language.md](language.md) · `4. 泛型` | 实现 | `examples/generics.extc` |
| 给泛型实例挂方法（slice<T> 的方法集） | [language.md](language.md) · 3.11 `impl` 挂在泛型实例上：`slice<T>` 的方法 | 实现 | `tests/instimpl` |
| 无载荷/带载荷枚举挂方法，trait 与 dyn 一起可用 | [language.md](language.md) · 3.12 `impl` 也能给枚举挂方法 | 实现 | `tests/impl/enum_methods.extc` · `tests/impl/enum_trait_dyn.extc` |
| 定长数组的 `.len`：编译期长度，可进循环界与下标范围，不可赋值 | [language.md](language.md) · `3.2 聚合` | 实现 | `tests/features/len.extc` |
| 超过 `i64` 上限的整数字面量（类型 `u64`），以及 `u64` 的 f-string / 说明符输出 | [language.md](language.md) · `2.2 格式化字符串 f"…"` | 实现 | `tests/features/u64.extc` |
| 导入另一个模块的 `const` 当定长数组长度（名单 / 通配 / 限定名三条路） | [language.md](language.md) · `6.1 顶层 const：值先定，也能当数组长度` | 实现 | `tests/features/importconst` |
| `u64` 的 `popcount()` / `clz()` / `ctz()` | [stdlib.md](stdlib.md) · `1. prelude：不用 use 就能用` | 实现 | `tests/features/bits.extc` |
| 静态分发与动态分发，协议实现的规则 | [language.md](language.md) · 5. 协议：`trait` 与 `dyn` | 实现 | `tests/dyn` |
| let/var/多名字声明、遮蔽、零初始化、全局的常量初始化式 | [language.md](language.md) · `6. 变量与可变性` | 实现 | `examples/shadowing.extc` |
| 模块级 const，整数常量当数组长度 | [language.md](language.md) · 6.1 顶层 `const`：值先定，也能当数组长度 | 实现 | `tests/constgen/const_global.extc` · `tests/constgen/run.sh` |
| 三种引用的形状与借用边界 | [language.md](language.md) · `7. 引用与视图` | 实现 | `examples/refs.extc` |
| ref / mut ref / ?ref 能指向什么 | [language.md](language.md) · `7.1 三种引用` | 实现 | `examples/refs.extc` |
| 什么时候要写 * | [language.md](language.md) · `7.2 解引用与自动解引用` | 实现 | `examples/deref.extc` |
| 视图的坐标、切片、可写视图与只读视图的关系，以及视图的返回与整体赋值（悬垂视图被拒、`copyInto`） | [language.md](language.md) · 7.3 视图 `slice<T>` | 实现 | `examples/slices.extc` · `tests/features/views` |
| 定长数组的整数组表达式（rank-1 子集） | [language.md](language.md) · 7.4 整数组表达式 `out = a + b` | 部分 | `examples/array-expr.extc` |
| 默认输入口径与显式读取 | [language.md](language.md) · `7.5 输入：默认"读一行再解析"` | 实现 | `tests/io` |
| 相邻循环自动融合（输入/输出配对） | [language.md](language.md) · `7.6 相邻循环的融合（临时视图消失）` | 实现 | `tests/fuse` |
| 不延长寿命的引用与 upgrade | [language.md](language.md) · 7.7 弱引用 `weak<T>` | 实现 | `tests/weak` |
| 存储去哪、什么时候回收（编译期决定） | [language.md](language.md) · `8. 内存模型` | 实现 | `examples/escape-promotion.extc` |
| 作用域即区域，块退出整块回收 | [language.md](language.md) · `8.1 arena 按词法块` | 实现 | `tests/arena` |
| 两个拥有存储的容器的口径 | [language.md](language.md) · 8.2 两个动态数组：`vector<T>`、`buf<T>` | 实现 | `examples/vector.extc` |
| 循环里换缓冲会让预留反复搬家的警告 | [language.md](language.md) · `8.3 循环里换缓冲：一条警告` | 实现 | `examples/growth-factor.extc` |
| 运行期检查、! 与 @unchecked 两个通道、trap | [language.md](language.md) · `9. 错误与逃生舱` | 实现 | `tests/traps` |
| 越界、陈旧句柄、冻结缓冲都在运行期确定性 trap | [language.md](language.md) · `9.1 运行时检查` | 实现 | `tests/traps` |
| 把"应该成立"写成 ! 断言 | [language.md](language.md) · 9.2 `!`：先检查，再 trap | 实现 | `examples/bang-assign.extc` |
| 显式放弃检查的唯一写法 | [language.md](language.md) · 9.3 `@unchecked`：唯一的 UB 通道 | 实现 | `tests/hostile` |
| 程序自己触发的 trap 与退出码 | [language.md](language.md) · 9.4 `trap(msg)` | 实现 | `tests/traps` |
| 可空值与错误传播 | [language.md](language.md) · 9.5 `option` / `result` 与 `?` | 实现 | `examples/option-result.extc` |
| 空合并的求值顺序 | [language.md](language.md) · 9.6 `??`：可能没有就兜底 | 实现 | `examples/coalesce.extc` |
| @private/@inline/@unchecked/@noCopy/@sharesStorage/@frozen/@export/@builtin/@overwrite/@ext | [language.md](language.md) · `10. 注解` | 实现 | `examples/showcase-impl.extc` |
| 语句与表达式的分工（没有 if/match 表达式） | [language.md](language.md) · `11. 语句与表达式` | 实现 | `examples/tour-expr.extc` |
| 表达式语句、赋值、块的作用 | [language.md](language.md) · `11.1 语句` | 实现 | `examples/tour-expr.extc` |
| match 的形态与穷尽性 | [language.md](language.md) · 11.2 `match` 是语句 | 实现 | `examples/match.extc` |
| 三种 for：区间、数组/视图元素、迭代协议 iter()/next()/value() | [language.md](language.md) · 11.3 `for` 的形态 | 实现 | `examples/for-loops.extc` |
| 13 个可重载运算符、派生规则、操作数按形参类型借或复制 | [language.md](language.md) · `11.4 运算符与重载` | 实现 | `tests/ops` |
| @noCopy 类型的运算符（两侧都写 ref 形参，比较不复制） | [language.md](language.md) · `11.4 运算符与重载` | 实现 | `tests/nocopy/ops.extc` · `tests/nocopy/run.sh` |
| 内建类型的输出与自定义 << | [language.md](language.md) · 11.5 输出与 `<<` | 实现 | `examples/print-desc-check.extc` |
| 一条语句同时给多个目标赋值（按右值同时求值） | [language.md](language.md) · `11.6 并行赋值` | 实现 | `examples/tour-expr.extc` |
| 在条件位做匹配绑定 | [language.md](language.md) · 11.7 `if let` / `while let` | 实现 | `tests/iflet` |
| par 循环的形状与限制 | [language.md](language.md) · 11.8 `par`：数据并行 | 部分 | `tests/par` |
| 默认参数的求值与省略规则 | [language.md](language.md) · `11.9 默认参数` | 实现 | `tests/defaults` |
| 手册明确列出写不出来的形状与替代写法 | [language.md](language.md) · `12. 结果：现在写不出来的写法` | 部分 | `tests/errors` |
| 剩下哪些形状只支持一部分 | [language.md](language.md) · `13. 已知局限` | 部分 | `tests/errors` |

## 标准库：`reference/stdlib.md`

| 特性 | 手册 | 状态 | 证据 |
|---|---|---|---|
| 模块到文件的路径怎么找 | [stdlib.md](stdlib.md) · `目录（导入路径）` | 实现 | `stdlib/INDEX` |
| prelude 送进每个文件的类型与函数 | [stdlib.md](stdlib.md) · 1. prelude：不用 `use` 就能用 | 实现 | `stdlib/prelude.extc` |
| vector/buf/string/hashMap/linMap/dense/nd 等容器面 | [stdlib.md](stdlib.md) · 2. `stl::*`：容器 | 实现 | `stdlib/std/data/vector.extc` · `stdlib/std/data/buf.extc` |
| vector 的容器方法面：insert / removeAt / truncate / reserve / contains / indexOf / sort / reverse / fill / == | [stdlib.md](stdlib.md) · 2. `stl::*`：容器 | 实现 | `stdlib/std/data/vector.extc` · `tests/stl/vector_ops.extc` |
| hashMap 遍历器 `iterKeys()` / `iterValues()`（`iter`/`next`/`value` 协议，for 与 while 通用） | [stdlib.md](stdlib.md) · 2. `stl::*`：容器 | 实现 | `stdlib/std/data/hashMap.extc` · `tests/hashmap/iter.extc` |
| io/fs/net/http/proc/parallel/coro/json 等模块 | [stdlib.md](stdlib.md) · 3. `std::*`：模块 | 实现 | `stdlib/std/` |
| 终端屏幕对象 `screen`、`color`、`key` 解码（备用屏/光标/定位/颜色 + 方向键与 Ctrl）；PTY 判据 | [stdlib.md](stdlib.md) · 3. `std::*`：模块 | 实现 | `stdlib/std/tui.extc` · `tests/tui` |
| 控制台对象 `stdin` / `stdout` / `stderr`（对象方法；与 `cin` / `cout` / `cerr` 同一份缓冲与读位置，可混用） | [stdlib.md](stdlib.md) · 3. `std::*`：模块 | 实现 | `tests/io/console_objects.extc` · `tests/io/console_range.extc` · `tests/io/run.sh` |
| 程序级流 `fs::fout` / `fs::fin` 的对象口（`open` / `flush` / `close`；关过可重开） | [stdlib.md](stdlib.md) · 3. `std::*`：模块 | 实现 | `tests/fs/objects.extc` · `tests/fs/run.sh` |
| JSON 对象层 `json::doc` / `json::value`（按字段读不再传四片参数） | [stdlib.md](stdlib.md) · 3. `std::*`：模块 | 实现 | `tests/json/object.extc` · `tests/json/run.sh` |
| 容器与引用/视图/所有权组合时容易写错的形状 | [stdlib.md](stdlib.md) · `4. 今天会咬人的组合` | 部分 | `tests/stl` |

## 模块与 C 互操作：`reference/modules-cabi.md`

| 特性 | 手册 | 状态 | 证据 |
|---|---|---|---|
| 一个文件一个模块、路径、四种 use、门面、@module | [modules-cabi.md](modules-cabi.md) · `1. 模块系统` | 实现 | `tests/module` |
| extern! / effects / @export / @frozen / @noCopy / std::dl | [modules-cabi.md](modules-cabi.md) · `2. C 互操作` | 实现 | `tests/cabi` · `tests/extbind` |
