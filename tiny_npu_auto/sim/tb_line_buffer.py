"""
tb_line_buffer.py — Line Buffer 行为模拟 + 面试题
==================================================
模拟 8×8 图像经过 Line Buffer + 3×3 窗口读取的过程
"""

def line_buffer_sim(img, img_width=8, kernel_size=3):
    """
    模拟 Line Buffer 的行为
    img: 8×8 图像（list of lists）
    返回：所有 3×3 窗口
    """
    print("=" * 60)
    print("Line Buffer 模拟 — 8×8 图像")
    print("=" * 60)
    
    print("\n输入图像:")
    for row in img:
        print(f"  {row}")
    
    # ---- Phase 1: DMA 写入 ----
    print(f"\n{'─'*60}")
    print("Phase 1: DMA 逐行写入 Line Buffer")
    print(f"{'─'*60}")
    
    buffer = [[0]*img_width for _ in range(kernel_size)]
    
    for r in range(8):
        row = r % 3  # 循环写入 0,1,2 行
        for c in range(img_width):
            buffer[row][c] = img[r][c]
        print(f"  写入第 {r} 行 → buffer 行 {row}: {img[r]}")
        if r >= 2:  # 3行凑齐后
            print(f"    [Buffer 状态] 行0={buffer[0]} 行1={buffer[1]} 行2={buffer[2]}")
    
    print(f"\n  ✅ Line Buffer 已填满 3 行数据")
    
    # ---- Phase 2: 滑动窗口读取 ----
    print(f"\n{'─'*60}")
    print("Phase 2: 滑动窗口读取 → 喂给 Systolic Array")
    print(f"{'─'*60}")
    
    windows = []
    for start_col in range(img_width - kernel_size + 1):
        window = [
            [buffer[0][start_col + j] for j in range(kernel_size)],
            [buffer[1][start_col + j] for j in range(kernel_size)],
            [buffer[2][start_col + j] for j in range(kernel_size)]
        ]
        windows.append(window)
        print(f"  窗口 {start_col}: {window}")
    
    print(f"\n  共生成 {len(windows)} 个 3×3 窗口")
    return windows


def main():
    # 8×8 测试图像
    image = [
        [1,  2,  3,  4,  5,  6,  7,  8],
        [9,  10, 11, 12, 13, 14, 15, 16],
        [17, 18, 19, 20, 21, 22, 23, 24],
        [25, 26, 27, 28, 29, 30, 31, 32],
        [33, 34, 35, 36, 37, 38, 39, 40],
        [41, 42, 43, 44, 45, 46, 47, 48],
        [49, 50, 51, 52, 53, 54, 55, 56],
        [57, 58, 59, 60, 61, 62, 63, 64]
    ]
    
    windows = line_buffer_sim(image)
    
    # 面试题
    print("\n" + "=" * 60)
    print("📖 面试题：Line Buffer 深度")
    print("=" * 60)
    print("""
Q: 做 3×3 卷积，Line Buffer 需要存几行？
A: 3 行。因为一次要同时提供 3 行像素才能构成 3×3 窗口。

Q: 如果图像宽度是 1280，Line Buffer 要多大？
A: 3 × 1280 × 8bit = 30720 bit ≈ 3.75 KB

Q: 如果不用 Line Buffer，会怎样？
A: 每次卷积都要从 DDR 读 9 个 pixel，读 9 次 DDR
   Line Buffer 让 9 次读 DDR → 1 次读 DDR + 8 次读 SRAM
   速度差：DDR (~50ns) vs SRAM (~1ns) → 快 50 倍
""")


if __name__ == "__main__":
    main()
