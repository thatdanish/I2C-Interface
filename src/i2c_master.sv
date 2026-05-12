`default_nettype none

module i2c_master (
    input clk_i,
    input rst_i,
    // From/To Slave
    input sda_i,
    output logic sda_o,
    output logic scl_o,
    // External
    input rw_i,
    input data_valid_i, 
    input logic [6:0] addr_i,
    input logic [31:0] data_i,
    output logic [31:0] data_o,
    output logic data_valid_o,
    output logic busy_o
);

typedef enum bit[3:0] { IDLE, START, BUFF, ADDR, R_DATA, W_DATA, RECV_ACK, SEND_ACK, STOP} state_t;
state_t current_state, next_state;
bit [2:0] bit_counter;
bit [2:0] byte_counter;
bit [2:0] addr_counter;
bit [31:0] send_data;
bit [31:0] recv_data;
bit [6:0] addr;
bit rw, byte_complete, data_complete;

assign busy_o = ~(current_state == IDLE);
assign byte_complete = (bit_counter == 'd7);
assign data_complete = (byte_counter == 'd5);

always_ff @( posedge clk_i ) begin
    if (!rst_i) begin
        send_data <= 'd0;
        recv_data <= 'd0;
        addr <= 'd0;
        bit_counter <= 'd0;
        byte_counter <= 'd0;
        addr_counter <= 'd0;
    end else begin
        if (data_valid_i == 1'b1) begin
            send_data <= data_i;
            addr <= addr_i;
            rw <= rw_i;
        end
    end
end

always_ff @(posedge scl_o) begin
    if (current_state == IDLE) begin
        bit_counter <= 'd0;
        byte_counter <= 'd0;
    end
    if (current_state == W_DATA || current_state == ADDR || current_state == R_DATA) begin
        bit_counter <= (bit_counter == 'd7) ? 'd0 : bit_counter + 'd1;
        byte_counter <= (byte_complete == 1'b1) ? ((byte_counter == 'd5 ) ? 'd0 : byte_counter + 'd1) : byte_counter;
    end
    if (current_state == R_DATA) begin
        recv_data[((byte_counter-1)*8)+bit_counter] <= sda_i;
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
            next_state =  BUFF;
        end 
        BUFF: begin
            next_state =  ADDR;
        end 
        ADDR: begin
            if (byte_complete == 1'b1) next_state = RECV_ACK;
            else next_state = ADDR;
        end
        R_DATA: begin
            if (byte_complete == 1'b1) next_state = SEND_ACK;
            else next_state =  R_DATA;
        end
        W_DATA: begin
            if (byte_complete == 1'b1) next_state = RECV_ACK;
            else next_state =  W_DATA;
        end 
        RECV_ACK: begin
            if (sda_i == 1'b0) begin
                if (data_complete == 1'b1) next_state = STOP;
                else next_state = (rw == 1'b0) ? W_DATA : R_DATA;
            end else begin
                if (data_complete == 1'b1) next_state = IDLE;
                else next_state = START;
            end 
        end
        SEND_ACK: begin
            if (data_complete == 1'b1) next_state = STOP;
            else next_state = R_DATA;
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
            data_o = 'd0;
            data_valid_o = 1'b0;
        end 
        START: begin
            sda_o = 1'b0;
            scl_o = 1'b1;            
            data_o = 'd0;
            data_valid_o = 1'b0;
        end 
        BUFF: begin
            sda_o = 1'b0;
            scl_o = clk_i;            
            data_o = 'd0;
            data_valid_o = 1'b0;
        end 
        ADDR: begin
            sda_o = (byte_complete == 1'b1) ? rw :  addr[bit_counter];
            scl_o = clk_i;
            data_o = 'd0;
            data_valid_o = 1'b0;
        end
        R_DATA: begin
            sda_o = 1'b0;
            scl_o = clk_i;
            data_o = 'd0;
            data_valid_o = 1'b0;
        end
        W_DATA: begin
            sda_o = send_data[((byte_counter-1)*8)+bit_counter];
            scl_o = clk_i;            
            data_o = 'd0;
            data_valid_o = 1'b0;
        end 
        RECV_ACK: begin
            sda_o = 1'b0;
            scl_o = clk_i;
            data_o = 'd0;
            data_valid_o = 1'b0;
        end 
        SEND_ACK: begin
            sda_o =  (data_complete == 1'b1) ? 1'b1 : 1'b0;
            scl_o =  clk_i;
            data_o = (data_complete == 1'b1) ? recv_data : 'd0;
            data_valid_o = (data_complete == 1'b1) ? 1'b1 : 1'b0;
        end
        STOP: begin
            sda_o = 1'b1;
            scl_o = 1'b1;;
            data_o = 'd0;
            data_valid_o = 1'b0;
        end 
        default: begin
            sda_o = 1'b1;
            scl_o = 1'b1;
            data_o = 'd0;
            data_valid_o = 1'b0;
        end
    endcase
end
endmodule