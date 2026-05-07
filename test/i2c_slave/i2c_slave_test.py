import cocotb
from cocotb.triggers import Timer, RisingEdge,ClockCycles
from cocotb.clock import Clock

# Parameters

PRINT_STATES = True
SMOKE_TEST =  True
CLOCKPERIOD = 10
MAX_CLOCKS = 150
slave_sates = ["IDLE","START","ADDR","R_DATA", 
                "W_DATA","RECV_ACK","SEND_ACK","STOP"]

# Clock

async def clk_(dut, N_CLKS):
    clock = Clock(dut.clk_i, CLOCKPERIOD, "ns")
    clock.start()
    await ClockCycles(dut.clk_i, int(N_CLKS))

# Reset

async def Reset(rst_i, n):
    rst_i.value = 0
    await Timer(CLOCKPERIOD*n, "ns")
    rst_i.value = 1

# Initialize Inputs

async def init_inputs(dut):
    dut.scl_i.value = 1
    dut.sda_i.value = 1

# Print-states

async def print_states(dut):
    if PRINT_STATES:
        while True:
            await RisingEdge(dut.clk_i)
            cocotb.log.info(f"Slave state: {slave_sates[int(dut.current_state.value)]}")

# Smoke-test

if SMOKE_TEST:
    @cocotb.test()
    async def smoke_test(dut):
        clk = cocotb.start_soon(clk_(dut, MAX_CLOCKS/2))

        await Reset(dut.rst_i, 4)
        await Timer(CLOCKPERIOD, 'ns')
        await init_inputs(dut)
        cocotb.start_soon(print_states(dut))
        await clk

# Single-write

@cocotb.test()
async def single_write(dut):
    pass