module i2c_master (
    input clk_i,
    input rst_i
    input sda_o,
    output sda_o,
    output scl_o,
    input logic [6:0] addr_i,
    input logic [31:0] data_i,

);

typedef enum bit[2:0] { IDLE, START, DATA, ACK, STOP} state_t;
state_t current_state, next_state;


always_ff @( posedge clk_i ) begin
    if (!rst_i) begin
        
    end else begin
        
    end
    
end


// Controller FSM

always_ff @( posedge clk_i ) begin
    if (!rst_i) begin
        current_state <= IDLE;
    end else begin
        current_state <= next_state;
    end
    
end
endmodule