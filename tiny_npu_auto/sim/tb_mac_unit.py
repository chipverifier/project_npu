"""
tb_mac_unit.py — MAC 单元测试台
=================================
用 Python 模拟 mac_unit.sv 的行为，验证它的逻辑是否正确。

这个测试台对应硬件验证中的"定向测试 + 随机测试"。
"""

def mac_unit(a, b, c):
    """
    模拟 mac_unit.sv 的行为：
    result = a * b + c
    """
    product = a * b          # 对应 always_comb: product = a * b
    result = product + c     # 对应 always_ff: result <= product + c
    return result


def run_test(name, a, b, c, expected):
    """运行一个测试用例并比对结果"""
    result = mac_unit(a, b, c)
    if result == expected:
        print(f"  ✅ {name}: {a} × {b} + {c} = {result}")
    else:
        print(f"  ❌ {name}: {a} × {b} + {c} = {result} (期望 {expected})")


def main():
    print("=" * 50)
    print("MAC Unit 测试台")
    print("=" * 50)

    # ============================================================
    # 测试 1：基本运算
    # ============================================================
    print("\n【测试 1：基本运算】")
    run_test("3×4+0",    a=3,   b=4,   c=0,    expected=12)
    run_test("5×6+10",   a=5,   b=6,   c=10,   expected=40)
    run_test("0×255+0",  a=0,   b=255, c=0,    expected=0)
    run_test("1×1+100",  a=1,   b=1,   c=100,  expected=101)

    # ============================================================
    # 测试 2：边界值
    # ============================================================
    print("\n【测试 2：边界值】")
    run_test("最大×最大", a=255, b=255, c=0,     expected=65025)  # 255*255=65025
    run_test("最大+最大", a=255, b=255, c=65535, expected=130560) # 溢出测试

    # ============================================================
    # 测试 3：连续累加 — 模拟 3x3 卷积窗口的 9 次 MAC
    # ============================================================
    print("\n【测试 3：连续累加 — 模拟 3x3 卷积】")
    # 模拟一个 3x3 窗口的像素和权重
    pixels  = [10, 20, 30, 40, 50, 60, 70, 80, 90]  # 9个像素值
    weights = [ 1,  0, -1,  1,  0, -1,  1,  0, -1]  # 9个权重值

    acc = 0
    for i in range(9):
        acc = mac_unit(pixels[i], weights[i], acc)
        print(f"  第{i+1}次MAC: {pixels[i]}×{weights[i]} + 累加器={acc}")
    print(f"  3x3 窗口卷积结果: {acc}")

    # ============================================================
    # 测试 4：完全随机测试
    # ============================================================
    print("\n【测试 4：随机测试】")
    import random
    passed = 0
    failed = 0
    for i in range(100):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = random.randint(0, 65535)
        result = mac_unit(a, b, c)
        expected = a * b + c
        if result == expected:
            passed += 1
        else:
            failed += 1
            print(f"  ❌ 随机测试 {i}: {a}×{b}+{c}={result} (期望{expected})")

    print(f"  随机测试: 通过 {passed}/100, 失败 {failed}/100")

    # ============================================================
    # 总结
    # ============================================================
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)
    print(f"""
Python 模拟的 MAC 单元与 RTL 代码的对应关系：

  mac_unit.sv                          tb_mac_unit.py
  ──────────                          ──────────────
  always_comb product = a * b   →     product = a * b
  always_ff result <= product+c →     result = product + c
  valid_in / valid_out          →     函数调用传参/返回值

看到没？SystemVerilog 描述的硬件和 Python 描述的算法，
本质上在做同样的计算！
""")


if __name__ == "__main__":
    main()
