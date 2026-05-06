import cocotb
from cocotb.triggers import Timer, RisingEdge



# Parameters

CLOCKPERIOD = 10
SIMTIME = 100

# Clock

async def Clock(dut):

    for _ in range(SIMTIME):
        dut.clk_i.value = 1
        await Timer(CLOCKPERIOD/2, "ns")
        dut.clk_i.value = 0
        await Timer(CLOCKPERIOD/2, "ns")

# Reset

async def Reset(rst_i, n):
    rst_i.value = 0
    await Timer(CLOCKPERIOD*n, "ns")
    rst_i.value = 1

# Initialize Inputs

async def init_inputs(dut):
    dut.data_valid_i.value = 0
    dut.sda_i.value = 0
    dut.addr_i.value = 0
    dut.data_i.value = 0

# Sanity test

@cocotb.test()
async def sanity_test(dut):
    clock_running  = cocotb.start_soon(Clock(dut))
    
    await init_inputs(dut)
    await Reset(dut.rst_i, 4)
    await Timer(CLOCKPERIOD, "ns")

    if (dut.busy_o.value == 0):
        dut.data_valid_i.value = 1
        dut.data_i.value = 888

        await Timer(CLOCKPERIOD, "ns")
        try: 
            assert (dut.busy_o.value == 1) 
       
        except: 
            raise  AssertionError("busy_o is not asserted \n" \
            f"current_state : {dut.current_state.value}")
        
        dut.data_valid_i.value = 0
        await clock_running
        
    else: raise AssertionError("busy_o is not de-asserted")

