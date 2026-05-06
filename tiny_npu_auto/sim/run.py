"""
run.py — 一键运行 MAC 单元测试
用法: python run.py
"""

import subprocess
import sys
import os

# 切换到脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("NPU MAC Unit - 一键测试")
print("=" * 50)

# 运行 Python 测试台
print("\n▶ 运行 Python 测试台 tb_mac_unit.py...\n")
result = subprocess.run(
    [sys.executable, "tb_mac_unit.py"],
    capture_output=False,
    text=True
)

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
print(f"""
当前项目结构：
  tiny_npu_auto/
  ├── model/
  │   └── conv_demo.py     ← Python 参考模型（3x3 卷积）
  ├── rtl/
  │   └── mac_unit.sv      ← SystemVerilog RTL（MAC 单元）
  └── sim/
      ├── tb_mac_unit.py   ← Python 测试台
      └── run.py            ← 一键运行脚本

下一步可以做的：
  1. 安装 iverilog，用真正的 RTL 仿真器运行 mac_unit.sv
  2. 把多个 mac_unit 拼成 systolic_array.sv（脉动阵列）
  3. 把 systolic_array 连上 line_buffer 做真正的卷积
""")
