# no-division-calculator

一个基于 Python3 的解释型命令行计算器，可以进行加、减、乘、幂四则运算，并支持代数多项式乘积结果化简等功能

## 如何使用

### 环境

- Python 3.8（理论上 Python3.6+应该也是可以使用的，但是没有进行集成测试）

### 下载

点击绿色的下载按钮，如果你看不见这个绿色的按钮，也可以前往[Release 页面](https://github.com/LonelySteve/no-division-calculator/releases)下载最新版本。

把下载好的压缩包解压到任意目录，然后打开终端，使用`cd`命令将当前工作目录切换到解压目录，使用`ls`命令列出当前工作目录下的文件或文件夹，如果你看到了类似以下的输出，则证明你做对了！

```powershell
Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       2019/11/29     19:54                src
d-----       2019/11/29     19:50                tests
-a----       2019/11/28     16:55           1350 .gitignore
-a----       2019/11/28     16:51          35823 LICENSE
-a----       2019/11/29     20:17            336 README.md
```

### 命令行交互

使用以下命令进入交互式计算模式：

```powershell
python -m src.ndc
```

如果你看到了以下输出，说明你再次做对了！

```powershell
Welcome to the no-division-calculator!
no-division-calculator Copyright (C) 2019 JLoeve
>
```

`>` 符号后面就可以输入表达式，按回车确定，如果表达式符合约定，就能得到结果：

```powershell
Welcome to the no-division-calculator!
no-division-calculator Copyright (C) 2019 JLoeve
>1+1
2
```

按下 `Ctrl+C` 即可退出交互式计算器环境

### 命令行参数

#### -c \<expression\>

执行指定的表达式，并将结果输出到标准输出流

#### -h, --help

打印帮助信息

## 支持的表达式形式

- 整数/小数的加、减、乘、幂
- 变量的加、减、乘、幂

以上形式均可使用括号进行嵌套使用，符号之间的空白会被自动忽略

### 例子

```powershell
>1 + 1 - 2 * (2^2)
-6
```

```powershell
>x^1+x^2+x^2+x^3+x^3+x^3
x+2x^2+3x^3
```

```powershell
>3*(x^1+x^2+x^2+x^3+x^3+x^3)
3x+6x^2+9x^3
```

注意：**本计算器并不完全支持计算的输出作为输入**，例如，如果像上面输出结果一样，输入以下表达式会出错：

```powershell
>3x+6x^2+9x^3
unexpected 'x' at pos 1
```

解决方案是给每个数字和变量间添加上 `*` 符号：

```powershell
>3*x+6*x^2+9*x^3
3x+6x^2+9x^3
```

## 版权声明

本软件使用了部分 Jinja 代码，由于 Jinja 采用了 BSD 许可证，故这里附加[此许可证](LICENSE.rst)。

另外，本项目还附加一个 [GPL 许可证](LICENSE)

## 为啥不提供 pypi 源

暂时不提供，原因是这个计算器只是个作业，仅供学习用途使用
