`default_nettype none

module I2CTop (
    input clk_i,
    input rst_i,
    // From/to master's side
    input rw_i,
    input master_data_valid_i,
    input logic [6:0] addr_i,
    input logic [31:0] master_data_i,
    output logic busy_o,
    // From/to slave's side
    input slave_data_valid_i,
    input logic [31:0] slave_data_i,
    output logic rw_o,
    output logic data_valid_o,
    output logic [6:0] addr_o,
    output logic [31:0] data_o
);

logic sda_m2s, sda_s2m, shared_clk;

i2c_master i2c_master_i (
    .clk_i,
    .rst_i,
    .sda_i(sda_s2m),
    .sda_o(sda_m2s),
    .scl_o(shared_clk),
    .rw_i,
    .data_valid_i(master_data_valid_i),
    .addr_i,
    .data_i(master_data_i),
    .busy_o
);


i2c_slave i2c_slave_i (
    .clk_i,
    .rst_i,
    .scl_i(shared_clk),
    .sda_i(sda_m2s),
    .sda_o(sda_s2m),
    .data_valid_i(slave_data_valid_i),
    .data_i(slave_data_i),
    .rw_o,
    .data_valid_o,
    .addr_o,
    .data_o
);

endmodule