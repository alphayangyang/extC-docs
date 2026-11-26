# 风格指南：把程序写成对象

> 状态：**规范**（建议，不是编译器强制）· 最后核对 2026-11-23

extC 没有 `class`、没有继承、没有属性语法。它的对象就是**一个 struct 加一组方法**：
数据写在字段里，行为写在 `impl` 块里，调用点永远是 `对谁做什么`。这份指南只讲写法，
讲的是怎么让读代码的人第一眼就看见对象；编译器能挡的规则都已经写进
[语言现状](../reference/language.md) 了。

## 1. 对象 = 数据 + 方法

- **字段装状态，方法装行为。** 方法有两种合法位置：写在 struct 体内（数据与行为相邻，
  标准库统一这么写），或写在 `impl` 块里（给 @ext 外来类型加方法时必须用 impl；
  类型自己也可以）。**同一个类型的全部方法放在同一处**，不要一半在体内、一半散在 impl 块里。
- **字段默认藏起来。** 公开的数据面用 `@private` 收紧，外面只通过方法读；要交出视图就
  给一个返回 `slice<T>` 的方法（`view()` / `viewMut()`），而不是公开字段让别人自己拼。
- **方法签名三档，按“调用者对对象做什么”选：**

| 调用者要做什么 | `self` 怎么写 | 例子 |
|---|---|---|
| 只读 | `self: ref T` | `fn len(self: ref vector<T>) -> i64` |
| 改 | `self: mut ref T` | `fn push(self: mut ref vector<T>, v: T)` |
| 拿走所有权 | `self: T`（`@noCopy` 才有意义） | `@drop` 钩子、`release` |

不要写 `getX` / `setX` 这样的逐字段存取器；要么给出有语义的方法（`moveCount()`、`isFull()`），
要么直接公开成字段（纯数据传输的 struct 可以全是公开字段，别硬套方法）。

## 2. 构造：`T::new` / `T::withX`

构造入口是**不带 `self` 的关联函数**，返回 `T` 自己：

```extc
use std::io

struct counter {
    n: i64
    step: i64

    fn new() -> counter {
        return counter { n: i64(0), step: i64(1) }
    }

    fn withStep(step: i64) -> counter {
        return counter { n: i64(0), step: step }
    }

    fn next(self: mut ref counter) -> i64 {
        self.n = self.n + self.step
        return self.n
    }
}

fn main() {
    var a: counter = counter::new()
    var b: counter = counter::withStep(i64(10))
    println(f"{a.next()} {b.next()} {b.next()}")
}
```

- 一个类型留**一个**规范构造入口（`new`），带参数的变体用 `withX` 命名；不要同时提供
  半打近似构造。
- `T {}` 是零值字面量，只在“零值就是有意义的初值”时用（比如棋盘全是空格子）；
  需要初始化逻辑就写 `new()`。

## 3. 只读参数写借，不按值收

形参类型就是调用点的语义：**`ref T` = 借来看，`T` = 复制（或移动）一份**。所以
“只读”的参数一律写 `ref T` 或 `slice<T>` 视图，别按值收——按值收等于强迫调用者复制，
容器类型还会直接编译失败（`@noCopy` 不许按值复制）。

<!-- fragment -->
```extc
// 读：借
fn total(self: ref board) -> i64 { … }
// 写：可变借
fn play(self: mut ref board, idx: i64, side: cell) -> bool { … }
// 要第二个所有者：让调用者显式 clone()，函数签名不要偷偷复制
```

同理，两个对象比较时写成 `v == w`（运算符的形参是 `ref`，两边都不复制）；需要内容快照
而对象会被改时，显式写 `snapshot()` / `clone()`，让复制出现在调用点。

## 4. 状态用枚举 + match，枚举也能挂方法

把一个东西的“状态”写成枚举，而不是一组 `bool` 标志或魔数；枚举可以像 struct 一样挂
`impl`，所以状态相关的行为就写在状态类型上：

<!-- fragment -->
```extc
type cell = | empty | black | white

impl cell {
    fn glyph(self: ref cell) -> slice<u8> {
        var g: slice<u8> = "?"
        match *self {
            empty => { g = "." }
            black => { g = "X" }
            white => { g = "O" }
        }
        return g
    }
}
```

- `match` 是**语句**，不是表达式：函数体里先 `var` 一个结果，`match` 里各臂赋值，最后
  `return`。别指望 `let x = match e { … }`。
- 臂里写**裸变体名**（`empty =>`），不写 `cell.empty =>`。
- 枚举方法的接收者写 `ref cell`，体内 `match *self`。

## 5. 多态：先 trait 静态派发，异构才 `dyn`

- trait 名**大写开头**（编译器要求，用来和类型名分开），类型名 camelCase 小写开头。
- 只在同一个位置上要放多种实现（策略、插件、异构容器）时才用 `dyn Trait`；否则用泛型 /
  静态 trait 派发，零虚表开销。
- `dyn` 的方法形参写 `ref T`：引用在虚表签名里也是指针，写值会生成签名不一致的 C
  （`--check-c` 会抓到）。

## 6. 错误：`result` + `?`，`trap` 只给不变式

- 可恢复的失败用 `result<T, E>` 返回，调用点用 `?` 往上抛，用 `??` 给默认值：

<!-- fragment -->
```extc
fn load(path: slice<u8>) -> result<config, err> {
    let text = readAll(path)?
    let cfg = parse(text)?
    return success(cfg)
}
```

- `?` 只出现在**语句的值位置**（声明、赋值、返回、裸调用、`if` 条件、`match` 的臂体与
  scrutinee）；`&&` / `||` / `??` 的右侧、`while` 条件、lambda 体里不行，先 `let v = e?`。
- `trap(msg)` 只用于“程序自己的不变式坏了”（越界、状态机走不到的分支）；用户的坏输入
  走 `result`。

## 7. 热路径按数据布局写

对象好看不等于对象快。内层循环里跟着热点走的是**布局**：

- 定长、尺寸已知的表用定长数组内联（`[15][15]cell`），不要 `vector<vector<cell>>`；
  多维内联数组的行是连续的，遍历顺序按行。
- 每个元素都小的结构，优先“数组的数组”（SoA）而不是“对象的数组”；需要并行时更是如此。
- 循环里不要 `new` 容器、不要 `clone` 字符串；要预留就用 `withCap` / `reserve`。
- 字面量默认是 `i64`；要别的宽度就写出来（`i32(0)`、`u8(255)`），别指望隐式窄化。

完整例子：[`examples/gomoku.extc`](../../extC_Compiler/examples/gomoku.extc)（对局程序，棋盘内联）与
[`examples/gomoku-board.extc`](../../extC_Compiler/examples/gomoku-board.extc)（纯棋盘对象）。

## 8. 命名与写法：一个概念一个拼写

**大小写表**（`tools/check_naming.py` 会机械核对，越界即红）：

| 声明 | 写法 | 例子 |
|---|---|---|
| `struct` / `type`（含枚举） | lowerCamel | `struct board`、`hashMap<K, V>`、`type side = ...` |
| `trait` | UpperCamel | `trait Strategy` |
| `fn` / 方法 | lowerCamel | `fn place`、`fn withCap` |
| 整数常量（顶层 `const`） | UPPER_SNAKE | `const BOARD_SIZE: i64 = 225` |
| 其它全局（顶层 `let` / `var`） | lowerCamel | `let version`、`var lastWinner` |
| 类型参数 | 单大写字母 | `T`、`K`、`V` |
| 私有实现 | lowerCamel + `@private` | `@private fn findSlot` |
| 枚举变体 | lowerCamel | `type side = | black | white` |

**顶层三种声明，按"值什么时候知道"分**：

- `const NAME: T = <整数字面量>` —— 编译期常量。**还能当数组长度**（`[N][N]u8`）。
  值的位置允许常量表达式（`const A: i64 = 15 * 15` 可用），但当长度只认字面量。
- `let name: T = <常量表达式>` —— 不可变全局：字符串、枚举、结构体字面量的每个字段都是
  常量表达式。字段不能引用别的全局（C 的静态初始化式不许引用 `static const` 对象）。
- `var name: T` —— 可变全局，C 静态存储期零初始化。
- 全局 = 深度 0：含引用的全局类型不能存在（没有东西可借）。
- ⚠️ 全局变量名**不要与类型名同名**：生成的 C 里类型是 `typedef`、全局是 `static` 变量，
  两者共用同一个标识符空间（实测 `let cfg: cfg = ...` 报 `redeclared as different kind of symbol`）。

**一个概念一个拼写**（下面每一条都由门禁查，新的同义词会直接红）：

- 元素个数一律 `len()`：没有 `length()` / `size()` / `used()`（屏幕尺寸是 `dims()`）。
- 容量一律 `capacity()`：没有 `capOf()`。
- 收缩分两种：缩到长度叫 `shrinkToFit()`；缩到指定长度叫 `shrink(k)`。
- 构造：`new()` 与 `withX()`；提前留容量是 `string::withCapacity(n)` / `vector::withCap(n)`，
  没有 `create()`。
- 视图：借是 `view()` / `viewMut()`（没有 `asMutSlice()`）；要一份独立的拷贝写 `snapshot()`。
- `find` 一律返回 `?i64`（没有 -1 哨兵）；内部槽位索引用 `findSlot()` 并且 `@private`。

**模块**：`use std::data::vector` 显式导入；对外门面用 `pub use` 列清单，内部实现用
`@private` 藏起来。公开的类型要配 `@code` 例子（公开面闸门会拿手册核对这些成员有没有被写到）。

## 9. 一个完整的对象

下面这段把上面的规矩合起来：状态枚举带方法、`board` 有唯一构造入口、读方法写 `ref self`、
写方法写 `mut ref self`、多态用 trait + `dyn`、棋盘用定长数组内联。

```extc
use std::io

type cell = | empty | black | white

impl cell {
    fn glyph(self: ref cell) -> slice<u8> {
        var g: slice<u8> = "?"
        match *self {
            empty => { g = "." }
            black => { g = "X" }
            white => { g = "O" }
        }
        return g
    }
}

struct board {
    cell: [3][3]cell
    @private moves: i64

    fn new() -> board {
        return board {}
    }

    fn moveCount(self: ref board) -> i64 {
        return self.moves
    }

    fn play(self: mut ref board, idx: i64, side: cell) -> bool {
        let x: i64 = idx % 3
        let y: i64 = idx / 3
        if self.cell[y][x] != cell.empty { return false }
        self.cell[y][x] = side
        self.moves = self.moves + 1
        return true
    }

    fn render(self: ref board) {
        for y in 0..3 {
            for x in 0..3 {
                io::cout << self.cell[y][x].glyph()
            }
            println("")
        }
    }
}

trait Strategy {
    fn pick(self: ref Self, b: ref board) -> i64
}

struct firstFree {
    tag: i64
}

impl Strategy for firstFree {
    fn pick(self: ref firstFree, b: ref board) -> i64 {
        for i in 0..9 {
            let x: i64 = i % 3
            let y: i64 = i / 3
            if b.cell[y][x] == cell.empty { return i }
        }
        return 0 - 1
    }
}

fn main() {
    var b: board = board::new()
    let s = firstFree { tag: 1 }
    var d: dyn Strategy = dyn Strategy(s)
    let at: i64 = d.pick(ref b)
    println(f"at={at} ok={b.play(at, cell.black)}")
    b.render()
    println(f"moves={b.moveCount()}")
}
```

这段的输出是 `at=0 ok=true`，三行棋盘（第一行 `X..`），最后 `moves=1`。留意两点：
`Strategy::pick` 收 `ref board` 而不是 `board`（不复制棋盘），`d.pick(ref b)` 的 `ref` 是
调用点写的借，不是 `dyn` 的要求。

## 改完代码的检查单

- [ ] 字段和它的方法在同一个类型上，字段用 `@private` 收紧了吗？
- [ ] 每个类型只有一个规范构造入口吗？`T {}` 用的地方零值有意义吗？
- [ ] 只读形参写 `ref` / 视图了吗？有没有签名在偷偷复制？
- [ ] 状态是枚举 + `match`，而不是 `bool` 组合或魔数吗？
- [ ] 可恢复错误走 `result` + `?`，`trap` 只留给不变式吗？
- [ ] 热路径内层循环里没有分配、没有隐藏的 `clone` 吗？
- [ ] 加了语言特性/标准库 API，是否同时更新了[语言现状](../reference/language.md) /
      [标准库现状](../reference/stdlib.md) 与 [特性总表](../reference/features.md)？
- [ ] 新名字过了命名门禁吗（`python3 tools/check_naming.py --check`）？长度/容量/构造/视图
      没有引入第二种拼写吗？