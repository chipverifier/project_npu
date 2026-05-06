# Tiny-NPU (AI 自动生成版本)

## 项目简介
这是一个自研的轻量级AI芯片项目，重点围绕NPU的架构探索与验证展开。
作为芯片验证工程师，通过该项目深入理解NPU核心业务逻辑，并构建可验证的硬件模型。

**核心认知：NPU = 把软件算法搬进硬件实现加速。**

## 项目结构

```
tiny_npu_auto/
├── model/
│   └── conv_demo.py      ← Python 参考模型（Golden Model）
│                            模拟 RGB 图像 3x3 卷积全过程
│                            纯 Python 实现，零依赖
│
├── rtl/
│   └── mac_unit.sv        ← SystemVerilog RTL
│                            NPU 最核心的乘累加单元 (MAC)
│                            对应 Python 中的 mac_result += pixel * weight
│
└── sim/
    ├── tb_mac_unit.py     ← Python 测试台
    │                        定向测试 + 边界测试 + 3x3卷积累加 + 随机测试
    └── run.py             ← 一键运行脚本
```

## 已完成的功能

### ✅ Phase 1: Python 行为模型
- **`conv_demo.py`** — RGB图像3x3卷积演示
  - 生成8x8 RGB测试图像
  - 手动实现卷积（双重for循环模拟MAC运算）
  - ReLU激活函数
  - 建立了软件算法 → 硬件模块的概念映射

### ✅ Phase 2: RTL 最小单元
- **`mac_unit.sv`** — 乘累加单元
  - 输入：a(8bit) × b(8bit) + c(16bit)
  - 输出：result(16bit)
  - 带 valid/clock/reset 控制信号
  - 对应 Python 中的 `mac_result += pixel * weight`

### ✅ Phase 3: 验证平台
- **`tb_mac_unit.py`** — MAC单元测试台
  - 基本运算验证（4组定向测试）
  - 边界值测试（最大值/溢出）
  - 3x3卷积累加测试（模拟9次连续MAC）
  - 随机约束测试（100组，全部通过）

## 一键运行

```bash
# 运行 Python 参考模型（3x3 卷积演示）
python tiny_npu_auto/model/conv_demo.py

# 运行 MAC 单元测试台
python tiny_npu_auto/sim/run.py
```

## 核心概念：软件 vs 硬件对应关系

| 软件 (Python) | 硬件 (SystemVerilog / NPU) |
|:---:|:---:|
| 双重 for 循环 (i, j) | 脉动阵列 (Systolic Array) |
| 取 3x3 窗口 (window) | 行缓冲器 (Line Buffer) |
| `pixel * weight` | MAC单元中的乘法器 (Multiplier) |
| `mac_result` 累加 | MAC单元中的累加器 (Accumulator) |
| 函数调用传参 | valid_in / valid_out 握手信号 |
| ReLU 函数 | 激活单元 (Activation Unit) |

## 规划功能
- [x] 基础张量运算（Python 参考模型）
- [x] 验证测试平台（Python 测试台）
- [x] 简单RTL实现（MAC单元）
- [ ] Systolic Array（脉动阵列）
- [ ] Line Buffer（行缓冲器）
- [ ] 完整的图像卷积硬件加速器
- [ ] 安装 iverilog 进行真正的 RTL 仿真验证

## 免责声明
1. **非商业与学习目的**：本项目仅为个人学习NPU架构与芯片验证技术而创建，所有内容基于公开可获取的技术资料，不涉及任何公司或组织的商业机密、未公开技术及工作内容。
2. **AI生成内容说明**：项目中大部分代码及文档初稿由AI工具辅助生成，经个人整理、修改后发布。
3. **手动实现版本参考**：手动实现版本参考自开源项目 [tiny-npu-manual](https://github.com/chipverify/tiny-npu-manual)。

## 许可证声明
```
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute
this software, either in source code form or as a compiled binary, for any
purpose, commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of
this software dedicate any and all copyright interest in the software to
the public domain. We make this dedication for the benefit of the public
at large and to the detriment of our heirs and successors. We intend this
dedication to be an overt act of relinquishment in perpetuity of all
present and future rights to this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org/>
```

## 仓库说明
本仓库为AI自动生成版本，手动实现版本请见 [tiny-npu-manual](https://github.com/chipverify/tiny-npu-manual)
