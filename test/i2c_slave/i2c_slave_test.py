import random
import cocotb
from cocotb.triggers import Timer, RisingEdge,ClockCycles
from cocotb.clock import Clock

# Parameters

PRINT_STATES = True
SMOKE_TEST =  False
CLOCKPERIOD = 10
MAX_CLOCKS = 150
slave_sates = ["IDLE","ADDR","R_DATA", 
                "W_DATA","RECV_ACK","SEND_ACK"]

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
            cocotb.log.info(f"Slave state: {slave_sates[int(dut.current_state.value)]}({int(dut.current_state.value)})")

# Smoke-test

if SMOKE_TEST:
    @cocotb.test()
    async def smoke_test(dut):
        clk = cocotb.start_soon(clk_(dut, MAX_CLOCKS/2))
        await init_inputs(dut)
        await Reset(dut.rst_i, 4)
        await Timer(CLOCKPERIOD, 'ns')
        cocotb.start_soon(print_states(dut))
        await clk

# Single-write

@cocotb.test()
async def single_write(dut):

    # Setup
    clk = cocotb.start_soon(clk_(dut, MAX_CLOCKS/2))
    await init_inputs(dut)
    await Reset(dut.rst_i,5)
    cocotb.start_soon(print_states(dut))
    await Timer(CLOCKPERIOD,"ns")

    # Start
    
    dut.sda_i.value = 0
    dut.scl_i.value = 1
    # await Timer(CLOCKPERIOD, "ns")
    shared_clk = Clock(dut.scl_i, CLOCKPERIOD, "ns")
    shared_clk.start()

    # ADDR
    
    addr = []
    for i in range(8):
        await RisingEdge(dut.scl_i)
        if i != 7:
            a = random.randint(0,1)
            dut.sda_i.value = a
            addr.append(a)
        else: 
            dut.sda_i.value = 0
    addr.reverse()
    await Timer(CLOCKPERIOD, "ns")
    cocotb.log.info(f"Address : {addr}")
    
    # ACK
    await Timer(CLOCKPERIOD, "ns")
    await RisingEdge(dut.scl_i)
    try:
        assert(dut.sda_o.value == 0)  
    except: 
        raise AssertionError("sda_o high after address")
    
    # Write Data
    data = []
    for i in range(35):
        await Timer(CLOCKPERIOD, "ns")
        if i not in [8, 16, 24]:
            d = random.randint(0,1)
            dut.sda_i.value = d
            data.append(d)
    
    data.reverse()
    cocotb.log.info(f"Data : {data}")

    await RisingEdge(dut.scl_i)
    try:
        assert(dut.sda_o.value == 1)  
    except: 
        raise AssertionError("sda_o low after data")
    
    # STOP
    
    await RisingEdge(dut.clk_i)
    dut.sda_i.value = 1
    shared_clk.stop()
    dut.scl_i.value = 1

    await clk