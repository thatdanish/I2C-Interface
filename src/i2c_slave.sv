`default_nettype none

module i2c_slave(
    input clk_i,
    input rst_i,
    // From/To Master
    input scl_i,
    input sda_i,
    output logic sda_o,
    // External
    output logic rw_o,
    output logic data_valid_o,
    output logic [6:0] addr_o,
    output logic [31:0] data_o
);

typedef enum bit[3:0] { IDLE, START, ADDR, R_DATA, W_DATA, RECV_ACK, SEND_ACK, STOP} state_t;
state_t current_state, next_state;
bit [2:0] bit_counter;
bit [2:0] byte_counter;
bit [31:0] send_data;
bit [31:0] recv_data;
bit [6:0] addr;
bit trigger, byte_complete, data_complete, rw;

assign byte_complete = (bit_counter == 'd7);
assign data_complete = (byte_counter == 'd5);

always_ff @( posedge clk_i ) begin
    if (!rst_i) begin
        trigger <= 1'b0;
    end else begin
        trigger <= 1'b1;
        if (sda_i == 1'b0 && scl_i  == 1'b1 && (current_state == ADDR ||  current_state == W_DATA || current_state == RECV_ACK || current_state == STOP)) trigger <= 1'b1;
        else trigger <= 1'b0;
    end

end

// Slave FSM

always_ff @( posedge scl_i or posedge trigger) begin 
    if (current_state ==  IDLE) begin
        bit_counter <= 'd0;
        byte_counter <= 'd0;
    end
    if (current_state == W_DATA || current_state == ADDR || current_state == R_DATA) begin
        bit_counter <= (bit_counter == 'd7) ? 'd0 : bit_counter + 'd1;
        byte_counter <= (byte_complete == 1'b1) ? ((byte_counter == 'd5 ) ? 'd0 : byte_counter + 'd1) : byte_counter;
    end
end

always_ff @( posedge scl_i or posedge trigger) begin 
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
            if (sda_i == 1'b0 && scl_i  == 1'b1 ) next_state = START;
        end
        START: begin
            next_state = ADDR;
        end
        ADDR: begin
            if (byte_complete == 1'b1) next_state = SEND_ACK;
            else next_state = ADDR;
        end
        R_DATA: begin
            next_state = IDLE; // temporary
        end
        W_DATA: begin
            if (byte_complete == 1'b1) next_state = SEND_ACK;
            else next_state =  W_DATA;
        end
        RECV_ACK: begin
            next_state = IDLE; // temporary
        end
        SEND_ACK: begin
            if (data_complete == 1'b1) next_state = STOP;
            else next_state = W_DATA;
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
            rw_o =  1'b0;
            addr_o = 'd0;
            data_valid_o = 1'b0;
            data_o = 'd0;
        end
        START: begin
            sda_o = 1'b1;
            rw_o =  1'b0;
            addr_o = 'd0;
            data_valid_o = 1'b0;
            data_o = 'd0;
        end
        ADDR: begin
            sda_o = 1'b1;
            rw_o =  (byte_complete == 1'b1) ? rw : 1'b0;
            addr_o = (byte_complete == 1'b1) ? addr :'d0;
            data_valid_o = (byte_complete == 1'b1) ? 1'b1 : 1'b0;
            data_o = 'd0;
        end
        R_DATA: begin
            sda_o = 1'b1;
            rw_o =  1'b1;
            addr_o = addr;
            data_valid_o = 1'b0;
            data_o = 'd0;
        end
        W_DATA: begin
            sda_o = 1'b1;
            rw_o =  1'b0;
            addr_o = addr;
            data_valid_o = (data_complete == 1'b1) ? 1'b1 : 1'b0;
            data_o = (data_complete == 1'b1) ? recv_data : 'd0;
        end
        RECV_ACK: begin
            sda_o = 1'b0;
            rw_o =  rw;
            addr_o = addr;
            data_valid_o = 1'b0;
            data_o = recv_data;
        end
        SEND_ACK: begin
            sda_o = (data_complete == 1'b1) ? 1'b1 : 1'b0;
            rw_o =  1'b0;
            addr_o = 'd0;
            data_valid_o = 1'b0;
            data_o = 'd0;  
        end
        STOP: begin
            sda_o = 1'b1;
            rw_o =  1'b0;
            addr_o = 'd0;
            data_valid_o = 1'b0;
            data_o = 'd0;  
        end
        default: begin
            sda_o = 1'd1;
             rw_o =  1'b0;
            addr_o = 'd0;
            data_valid_o = 1'b0;
            data_o = 'd0;  
        end
    endcase
end

endmodule