// ============================================================
// line_buffer.sv — 行缓冲器 (Line Buffer)
// ============================================================
// Line Buffer 是 NPU 的"数据快递中转站"。
//
// 它的作用：
//   从 DMA 收来的数据是一整行图像 → 存到 Line Buffer
//   等 Line Buffer 凑够 3 行 → 按 3×3 窗口喂给 Systolic Array
//
// 为什么要它？
//   没有 Line Buffer：
//     DMA 读 1 个 pixel → MAC 算一次 → 等下一个 pixel ...
//     MAC 一直在等数据，利用率极低
//
//   有 Line Buffer：
//     DMA 可以一次读一整行（效率高）
//     Line Buffer 存 3 行，每次给 MAC 喂 9 个 pixel
//     MAC 不停地在算，利用率高
// ============================================================

module line_buffer #(
    parameter IMG_WIDTH  = 8,
    parameter KERNEL_SIZE = 3
) (
    input  logic        clk,
    input  logic        rst_n,
    // 写端口（DMA 把数据写进来）
    input  logic        wr_en,
    input  logic [7:0]  wr_data,
    // 读端口（给 Systolic Array 喂数据）
    input  logic        rd_en,
    output logic [7:0]  rd_window [KERNEL_SIZE-1:0][KERNEL_SIZE-1:0]
);

    // 存储体：3 行，每行 IMG_WIDTH 个 pixel
    logic [7:0] buffer [KERNEL_SIZE-1:0][IMG_WIDTH-1:0];

    // 写指针
    logic [7:0]  wr_col_cnt;
    logic [1:0]  wr_row_cnt;

    // 读指针
    logic [7:0]  rd_col_cnt;

    // DMA 写入逻辑
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_col_cnt <= 0;
            wr_row_cnt <= 0;
        end else if (wr_en) begin
            buffer[wr_row_cnt][wr_col_cnt] <= wr_data;
            if (wr_col_cnt == IMG_WIDTH - 1) begin
                wr_col_cnt <= 0;
                if (wr_row_cnt == KERNEL_SIZE - 1)
                    wr_row_cnt <= 0;
                else
                    wr_row_cnt <= wr_row_cnt + 1;
            end else begin
                wr_col_cnt <= wr_col_cnt + 1;
            end
        end
    end

    // 读取逻辑：滑动窗口
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_col_cnt <= 0;
        end else if (rd_en) begin
            for (int i = 0; i < KERNEL_SIZE; i++) begin
                for (int j = 0; j < KERNEL_SIZE; j++) begin
                    rd_window[i][j] <= buffer[i][rd_col_cnt + j];
                end
            end
            if (rd_col_cnt >= IMG_WIDTH - KERNEL_SIZE)
                rd_col_cnt <= 0;
            else
                rd_col_cnt <= rd_col_cnt + 1;
        end
    end

endmodule
