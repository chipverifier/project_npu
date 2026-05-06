// ============================================================
// mac_unit.sv — 乘累加单元 (Multiply-Accumulate Unit)
// ============================================================
// 这是 NPU 中最基本、最核心的计算单元。
// 它做一件事：out = a * b + c
//
// 对应 Python 代码中的这一行：
//   mac_result += pixel * weight
//
// 硬件实现：
//   a = pixel (像素值)
//   b = weight (权重值)
//   c = 之前的累加结果
//   out = 新的累加结果
//
// 数据位宽：8-bit (简化版本，便于理解)
// ============================================================

module mac_unit (
    input  logic        clk,        // 时钟
    input  logic        rst_n,      // 复位（低有效）
    input  logic        valid_in,   // 输入有效标志
    input  logic [7:0]  a,          // 操作数 a (如像素)
    input  logic [7:0]  b,          // 操作数 b (如权重)
    input  logic [15:0] c,          // 累加输入 (来自上一个 MAC)
    output logic [15:0] result,     // 乘加结果
    output logic        valid_out   // 输出有效标志
);

    // ----------------------------------------
    // 乘法结果（a × b 需要 16-bit 来存）
    // ----------------------------------------
    logic [15:0] product;

    // ----------------------------------------
    // 组合逻辑：做乘法
    // ----------------------------------------
    always_comb begin
        product = a * b;  // 8-bit × 8-bit = 16-bit
    end

    // ----------------------------------------
    // 时序逻辑：在时钟上升沿做累加
    // ----------------------------------------
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result    <= 16'd0;
            valid_out <= 1'b0;
        end else if (valid_in) begin
            result    <= product + c;  // ← 这就是 MAC 操作！
            valid_out <= 1'b1;
        end else begin
            valid_out <= 1'b0;
        end
    end

endmodule
