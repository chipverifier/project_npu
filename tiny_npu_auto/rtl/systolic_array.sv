// ============================================================
// systolic_array.sv — 3×3 脉动阵列 (Systolic Array)
// ============================================================
// 什么是脉动阵列？
//
// 想象一下学校做广播体操的方阵：
//   每一排的人同时做一个动作，然后传给旁边的人
//   → 所有人同时工作，数据像波浪一样在阵列中流动
//
// NPU 的脉动阵列就是这个道理：
//   pixels（像素）从上往下流
//   weights（权重）从左往右流
//   每个 MAC 单元在数据经过时做一次乘加
//
// 为什么用阵列？
//   如果只有一个 MAC，你要串行算 9 次
//   如果有 9 个 MAC 组成阵列，一次并行就算完了
//   → 这就是 NPU 比 CPU 快的根本原因
//
// 布局：
//         w00 →  w01 →  w02
//          ↓     ↓      ↓
//   p0 →  MAC00  MAC01  MAC02
//          ↓     ↓      ↓
//   p1 →  MAC10  MAC11  MAC12
//          ↓     ↓      ↓
//   p2 →  MAC20  MAC21  MAC22
//
//   pixels 从上往下流 (vertical)
//   weights 从左往右流 (horizontal)
//   部分和从左往右累加 (horizontal)
// ============================================================

module systolic_array #(
    parameter ARRAY_SIZE = 3  // 3×3 阵列
) (
    input  logic                    clk,
    input  logic                    rst_n,
    input  logic                    valid_in,     // 输入有效
    input  logic [7:0]  pixels  [ARRAY_SIZE-1:0], // 一列像素（同时输入）
    input  logic [7:0]  weights [ARRAY_SIZE-1:0], // 一行权重（同时输入）
    output logic [15:0] results [ARRAY_SIZE-1:0],  // 一列结果（同时输出）
    output logic                    valid_out
);

    // 内部连线声明
    logic [7:0]  pixel_in  [ARRAY_SIZE-1:0][ARRAY_SIZE-1:0];
    logic [7:0]  weight_in [ARRAY_SIZE-1:0][ARRAY_SIZE-1:0];
    logic [15:0] psum_in   [ARRAY_SIZE-1:0][ARRAY_SIZE-1:0];
    logic [15:0] psum_out  [ARRAY_SIZE-1:0][ARRAY_SIZE-1:0];
    logic        valid_mid [ARRAY_SIZE-1:0][ARRAY_SIZE-1:0];

    // 生成 3×3 MAC 阵列
    genvar i, j;
    generate
        for (i = 0; i < ARRAY_SIZE; i++) begin : row
            for (j = 0; j < ARRAY_SIZE; j++) begin : col
                // pixel 传递
                if (i == 0)
                    assign pixel_in[i][j] = pixels[j];
                else
                    assign pixel_in[i][j] = pixel_in[i-1][j];
                // weight 传递
                if (j == 0)
                    assign weight_in[i][j] = weights[i];
                else
                    assign weight_in[i][j] = weight_in[i][j-1];
                // partial sum 传递
                if (j == 0)
                    assign psum_in[i][j] = 16'd0;
                else
                    assign psum_in[i][j] = psum_out[i][j-1];
                // valid 传播
                if (i == 0 && j == 0)
                    assign valid_mid[i][j] = valid_in;
                else if (i == 0)
                    assign valid_mid[i][j] = valid_mid[i][j-1];
                else
                    assign valid_mid[i][j] = valid_mid[i-1][j];

                // MAC 单元
                mac_unit u_mac (
                    .clk      (clk),
                    .rst_n    (rst_n),
                    .valid_in (valid_mid[i][j]),
                    .a        (pixel_in[i][j]),
                    .b        (weight_in[i][j]),
                    .c        (psum_in[i][j]),
                    .result   (psum_out[i][j]),
                    .valid_out()
                );
            end
        end
    endgenerate

    // 输出：取最后一列的结果
    always_comb begin
        for (int i = 0; i < ARRAY_SIZE; i++) begin
            results[i] = psum_out[i][ARRAY_SIZE-1];
        end
    end

    assign valid_out = valid_mid[ARRAY_SIZE-1][ARRAY_SIZE-1];

endmodule
