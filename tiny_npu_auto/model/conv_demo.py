"""
conv_demo.py — 最小闭环：RGB 图像卷积演示（纯 Python，零依赖）
===============================================================
目标：模拟 NPU 最核心的操作 —— 对一张 RGB 图像做 3x3 卷积。
纯 Python 实现，不依赖任何第三方库，理解 NPU 的 MAC 运算本质。

运行方式：python conv_demo.py
"""

# ============================================================
# 第一步：造一张小 RGB 测试图像（8x8，方便观察）
# ============================================================
print("=" * 50)
print("第一步：生成一张 8x8 的 RGB 测试图像")
print("=" * 50)

H, W = 8, 8  # 图像高宽

# 用 list 表示 RGB 三个通道，每个通道是 HxW 的二维列表
# rgb[0] = R通道, rgb[1] = G通道, rgb[2] = B通道
rgb_image = [
    [[0]*W for _ in range(H)],  # R 通道
    [[0]*W for _ in range(H)],  # G 通道
    [[0]*W for _ in range(H)],  # B 通道
]

# 填充一些简单的图案方便观察卷积效果
# R 通道：左上角白色方块 (1..3行, 1..3列)
for i in range(1, 4):
    for j in range(1, 4):
        rgb_image[0][i][j] = 255

# G 通道：右下角白色方块 (5..7行, 5..7列)
for i in range(5, 8):
    for j in range(5, 8):
        rgb_image[1][i][j] = 255

# B 通道：中心十字
for i in range(H):
    for j in range(W):
        if (3 <= i < 5) or (3 <= j < 5):
            rgb_image[2][i][j] = 100

def print_channel(ch, name):
    """打印一个通道的二维数据"""
    print(f"\n{name} 通道 ({len(ch)}x{len(ch[0])}):")
    for row in ch:
        print("  " + " ".join(f"{v:4d}" for v in row))

print_channel(rgb_image[0], "R")
print_channel(rgb_image[1], "G")
print_channel(rgb_image[2], "B")

# ============================================================
# 第二步：定义一个 3x3 卷积核（图像增强：锐化滤波）
# ============================================================
print("\n" + "=" * 50)
print("第二步：定义 3x3 卷积核（锐化滤波器）")
print("=" * 50)

# 锐化核：中间高亮，周围负值
kernel = [
    [ 0, -1,  0],
    [-1,  5, -1],
    [ 0, -1,  0]
]

print("卷积核 (3x3):")
for row in kernel:
    print("  " + " ".join(f"{v:4d}" for v in row))

# ============================================================
# 第三步：手动实现卷积——这就是 NPU 的核心：MAC 运算！
# ============================================================
print("\n" + "=" * 50)
print("第三步：手动卷积 —— 这就是 NPU 的核心运算")
print("=" * 50)

def conv2d_single_channel(image_ch, kernel):
    """
    对单通道图像做 2D 卷积。
    这个函数模拟了 NPU 中一个 Processing Element (PE) 做的事：
    一个窗口一个窗口地做 Multiply-Accumulate (MAC) 运算。

    参数:
        image_ch: 二维列表，HxW
        kernel: 二维列表，KhxKw
    返回:
        二维列表，输出特征图
    """
    H = len(image_ch)
    W = len(image_ch[0])
    Kh = len(kernel)
    Kw = len(kernel[0])
    out_h = H - Kh + 1  # 输出高
    out_w = W - Kw + 1  # 输出宽

    # 初始化输出
    output = [[0]*out_w for _ in range(out_h)]

    for i in range(out_h):
        for j in range(out_w):
            # ★★★ 这就是 NPU 最核心的 MAC 运算 ★★★
            # Multiply: 取 3x3 窗口，每个像素 × 卷积核对应位置
            # Accumulate: 把所有乘积加起来
            mac_result = 0
            for ki in range(Kh):
                for kj in range(Kw):
                    pixel = image_ch[i + ki][j + kj]
                    weight = kernel[ki][kj]
                    mac_result += pixel * weight  # ← 这就是一次 MAC 操作！
            output[i][j] = mac_result

    return output

print("对每个通道做卷积...")
output_r = conv2d_single_channel(rgb_image[0], kernel)
output_g = conv2d_single_channel(rgb_image[1], kernel)
output_b = conv2d_single_channel(rgb_image[2], kernel)

print_channel(output_r, "R 卷积结果")
print_channel(output_g, "G 卷积结果")
print_channel(output_b, "B 卷积结果")

# ============================================================
# 第四步：激活函数（ReLU）— NPU 的后处理
# ============================================================
print("\n" + "=" * 50)
print("第四步：ReLU 激活函数（负值变0）")
print("=" * 50)

def relu_2d(matrix):
    """ReLU: max(0, x) — NPU 中常见的激活函数"""
    H = len(matrix)
    W = len(matrix[0])
    result = [[0]*W for _ in range(H)]
    for i in range(H):
        for j in range(W):
            result[i][j] = matrix[i][j] if matrix[i][j] > 0 else 0
    return result

output_r_relu = relu_2d(output_r)
output_g_relu = relu_2d(output_g)
output_b_relu = relu_2d(output_b)

print_channel(output_r_relu, "R ReLU 后")
print_channel(output_g_relu, "G ReLU 后")
print_channel(output_b_relu, "B ReLU 后")

# ============================================================
# 第五步：统计信息 — 理解 NPU 的数据流
# ============================================================
print("\n" + "=" * 50)
print("第五步：NPU 运算统计")
print("=" * 50)

# 输出特征图大小: (H-2) x (W-2) = 6x6
# 每个输出像素需要 3x3=9 次 MAC
# 3 个通道
out_h = H - 2  # 6
out_w = W - 2  # 6
mac_per_pixel = 9  # 3x3 卷积核
total_mac = out_h * out_w * mac_per_pixel * 3  # ×3 通道

print(f"输入图像: {H}x{W}x3")
print(f"卷积核: 3x3")
print(f"输出特征图: {out_h}x{out_w}x3")
print(f"总 MAC 运算次数: {total_mac}")
print(f"（这个数字就是衡量 NPU 算力的关键指标）")

# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 50)
print("✅ 最小闭环完成！")
print("=" * 50)
print("""
你刚刚模拟了 NPU 最核心的运算流程：

  RGB 图像 ──▶ 滑动窗口 ──▶ MAC 运算 ──▶ ReLU ──▶ 输出特征图
                    ↑              ↑
              （数据加载）    （乘累加，NPU的核心）

关键概念对应关系（软件 → 硬件）:
  Python                        硬件
  ─────────                     ─────────
  双重 for 循环 (i, j)   →     脉动阵列 (Systolic Array)
  取 3x3 窗口 (window)   →     行缓冲器 (Line Buffer)
  pixel * weight         →     乘法器 (Multiplier)
  mac_result 累加         →     累加器 (Accumulator)
  ReLU 函数               →     激活单元 (Activation Unit)

这个 Python 脚本就是你的 "Golden Model"（参考模型）！
后续做 RTL 时，拿它的结果作为标准答案来比对验证。
""")
