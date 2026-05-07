"""
tb_systolic_array.py — 脉动阵列行为模拟
========================================
用 Python 模拟 3×3 Systolic Array 的数据流，
让你直观看到 pixels 和 weights 在阵列中怎么流动。

对应 RTL: systolic_array.sv
"""

def systolic_array_3x3(pixels_3x3, weights_3x3):
    """
    模拟 3×3 脉动阵列的计算过程

    参数:
        pixels_3x3: 3×3 像素矩阵 (list of lists)
        weights_3x3: 3×3 权重矩阵 (卷积核)

    返回:
        results_3x3: 3×3 结果矩阵
    """
    # ============================================================
    # 初始化 3×3 MAC 阵列
    # 每个 MAC 单元有：
    #   - pixel_reg:   当前持有的像素值（从上方来）
    #   - weight_reg:  当前持有的权重值（从左边来）
    #   - psum:        累加的部分和
    # ============================================================
    
    # 为了让你看清数据流动，我们模拟"逐周期"的行为
    # 真正硬件中，每个时钟周期所有 MAC 同时工作

    SIZE = 3
    # 初始化所有寄存器为0
    pixel_reg  = [[0]*SIZE for _ in range(SIZE)]  # pixel 垂直传递
    weight_reg = [[0]*SIZE for _ in range(SIZE)]  # weight 水平传递
    psum       = [[0]*SIZE for _ in range(SIZE)]  # 部分和
    
    # 因为脉动阵列需要"逐列"输入（一次输入一列像素、一行权重）
    # 所以我们要把 3×3 的输入转换成 3 次输入

    results = [[0]*SIZE for _ in range(SIZE)]

    print("=" * 70)
    print("3×3 脉动阵列 — 周期级模拟")
    print("=" * 70)

    # ============================================================
    # 逐列处理
    # ============================================================
    for col in range(SIZE):  # 第 0, 1, 2 列
        print(f"\n{'─'*70}")
        print(f"▶ 第 {col+1} 个时钟周期：输入第 {col} 列像素和第 {col} 行权重")
        print(f"{'─'*70}")
        
        # 本周期输入的像素列和权重组
        pixel_col  = [pixels_3x3[row][col] for row in range(SIZE)]  # 一列3个像素
        weight_row = weights_3x3[col]  # 一行3个权重

        print(f"  输入像素列  ─>  [{pixel_col[0]}, {pixel_col[1]}, {pixel_col[2]}]")
        print(f"  输入权重行  ─>  [{weight_row[0]}, {weight_row[1]}, {weight_row[2]}]")
        
        # ---- 所有 MAC 同时计算 ----
        for i in range(SIZE):      # 行
            for j in range(SIZE):  # 列
                # 数据传递
                if i == 0:
                    pixel_reg[i][j] = pixel_col[j]   # 第一行从输入取 pixel
                else:
                    pixel_reg[i][j] = pixel_reg[i-1][j]  # 其他行从上一行来
                
                if j == 0:
                    weight_reg[i][j] = weight_row[i]  # 第一列从输入取 weight
                else:
                    weight_reg[i][j] = weight_reg[i][j-1]  # 其他列从左边来
                
                # MAC 计算：result = pixel × weight + 左边的部分和
                if j == 0:
                    psum[i][j] = pixel_reg[i][j] * weight_reg[i][j]
                else:
                    psum[i][j] = pixel_reg[i][j] * weight_reg[i][j] + psum[i][j-1]
        
        # ---- 打印本周期后阵列状态 ----
        print(f"\n  周期 {col+1} 后的阵列状态:")
        print(f"  {'MAC':>8} {'pixel':>8} {'weight':>8} {'psum':>8}")
        print(f"  {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
        for i in range(SIZE):
            for j in range(SIZE):
                print(f"  MAC{i}{j}:  {pixel_reg[i][j]:>4}  ×  {weight_reg[i][j]:>4}  =  {psum[i][j]:>6}")

    # ============================================================
    # 结果提取：最后一列的结果就是最终输出
    # ============================================================
    print(f"\n{'═'*70}")
    print("▶ 最终结果（取最后一列 psum 作为输出）")
    print(f"{'═'*70}")
    for i in range(SIZE):
        for j in range(SIZE):
            results[i][j] = psum[i][SIZE-1] if j == SIZE-1 else 0
    
    return results


def main():
    # ============================================================
    # 测试用例：简单 3×3 图像和 3×3 卷积核
    # ============================================================
    # 输入图像（3×3 像素）
    image = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]

    # 卷积核（3×3 权重）
    kernel = [
        [1,  0, -1],
        [1,  0, -1],
        [1,  0, -1]
    ]

    print("\n输入图像:")
    for row in image:
        print(f"  {row}")
    
    print("\n卷积核:")
    for row in kernel:
        print(f"  {row}")

    # 运行脉动阵列
    results = systolic_array_3x3(image, kernel)

    # ============================================================
    # 验证结果
    # ============================================================
    print(f"\n{'='*70}")
    print("验证：手动计算结果")
    print(f"{'='*70}")
    
    expected = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            total = 0
            for ki in range(3):
                for kj in range(3):
                    # 边界检查
                    pi, pj = i + ki - 1, j + kj - 1
                    if 0 <= pi < 3 and 0 <= pj < 3:
                        total += image[pi][pj] * kernel[ki][kj]
            expected[i][j] = total

    print("\n预期结果（标准卷积）:")
    for row in expected:
        print(f"  {row}")
    
    print("\n脉动阵列结果:")
    for row in results:
        print(f"  {row}")

    # ============================================================
    # 核心概念总结
    # ============================================================
    print(f"""
{'='*70}
📖 核心概念总结
{'='*70}

1. 脉动阵列 = 多个 MAC 单元排列成矩阵
   每个 MAC 做 a × b + c

2. 数据流方向
   pixels  ──> 从上往下流动
   weights ──> 从左往右流动
   结果    ──> 从最后一列输出

3. 为什么快？
   传统 CPU：一个 MAC 单元，算完一个再算下一个
            → 9×9=81 个 MAC 操作需要 81 个周期
   NPU 阵列：9个 MAC 同时工作
            → 3 个周期出第一个结果
            → 之后每个周期出 3 个结果

4. 关键设计思想
   数据复用：同一 pixel 被多个 weight 使用
           同一 weight 被多个 pixel 使用
           不像 CPU 每次都要从内存取数据
   
   流水线：初始化有延迟（latency）
           稳定后每个周期都有输出（throughput）

5. 面试能说的
   "脉动阵列通过数据流架构实现了计算效率的突破，
    用空间换时间——用更多的计算单元换更少的访存次数"
""")


if __name__ == "__main__":
    main()
