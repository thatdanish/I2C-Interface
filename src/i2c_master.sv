`default_nettype none

module i2c_master (
    input clk_i,
    input rst_i,
    input data_valid_i, 
    input sda_i,
    output logic busy_o,
    output logic sda_o,
    output logic scl_o,
    input logic [6:0] addr_i,
    input logic [31:0] data_i
);

typedef enum bit[2:0] { IDLE, START, DATA, ACK, STOP} state_t;
state_t current_state, next_state;
bit [2:0] bit_counter;
bit [1:0] byte_counter;
bit [31:0] data;
bit byte_complete, data_complete;

assign busy_o = ~(current_state == IDLE);
assign byte_complete = (bit_counter == 'd7);
assign data_complete = (byte_counter == 'd3);

always_ff @( posedge clk_i ) begin
    if (!rst_i) begin
        data <= 'd0;
        bit_counter <= 'd0;
        byte_counter <= 'd0;
    end else begin
        data <= (data_valid_i == 1'b1) ? data_i : data;
        if (current_state == DATA) begin
            bit_counter <= (bit_counter == 'd7) ? 'd0 : bit_counter + 'd1;
            byte_counter <= (byte_complete == 1'b1) ? ((byte_counter == 'd4 ) ? 'd0 : byte_counter + 'd1) : byte_counter;
        end
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

always_comb begin 
    next_state = IDLE;
    case (current_state)
        IDLE: begin
            if (data_valid_i == 1'b1) next_state = START;
        end 
        START: begin
            next_state =  DATA;
        end 
        DATA: begin
            if (byte_complete == 1'b1) next_state = ACK;
            else next_state =  DATA;
        end 
        ACK: begin
            if (sda_i == 1'b0) begin
                if (data_complete == 1'b1) next_state = STOP;
                else next_state =  DATA;
            end else next_state = START;
        end 
        STOP: begin
            next_state = IDLE;
        end 
        default: begin
            next_state = IDLE;
        end
    endcase
end

always_comb begin 
    case (current_state)
        IDLE: begin
            sda_o = 1'b1;
            scl_o = 1'b1;
        end 
        START: begin
            sda_o = 1'b0;
            scl_o = 1'b1;            
        end 
        DATA: begin
            sda_o = data[byte_counter*8+bit_counter];
            scl_o = clk_i;            
        end 
        ACK: begin
            sda_o = 1'b0;
            scl_o = clk_i;
        end 
        STOP: begin
            sda_o = 1'b1;
            scl_o = 1'b1;;
        end 
        default: begin
            sda_o = 1'b1;
            scl_o = 1'b1;
        end
    endcase
end

endmodule