import random
import cocotb
from cocotb.triggers import Timer, RisingEdge, ClockCycles
from cocotb.clock import Clock



# Parameters

CLOCKPERIOD = 10
MAX_CLOCKS = 60
master_sates = {0:"IDLE", 1:"START", 2:"ADDR", 3:"R_DATA", 
                4: "W_DATA", 5: "RECV_ACK", 6:"SEND_ACK", 7: "STOP"}

# Clock

async def clk_(dut):
    clock = Clock(dut.clk_i, CLOCKPERIOD, "ns")
    clock.start()
    await ClockCycles(dut.clk_i, MAX_CLOCKS)

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
    dut.rw_i.value = 0

# Print states

async def print_states(dut, master=True):
    if master:
        while True:
            await RisingEdge(dut.clk_i)
            cocotb.log.info(f"Master state: {master_sates[int(dut.current_state.value)]}")

#  Single-write

@cocotb.test()
async def single_write(dut):
    clk = cocotb.start_soon(clk_(dut))
    
    await init_inputs(dut)
    await Reset(dut.rst_i, 4)
    await Timer(CLOCKPERIOD, "ns")

    if (dut.busy_o.value == 0):
        dut.data_valid_i.value = 1
        dut.data_i.value = 888
        dut.addr_i.value = random.getrandbits(7)
        dut.rw_i.value = 0
        await Timer(CLOCKPERIOD, "ns")
        try: 
            assert (dut.busy_o.value == 1) 
        except: 
            raise  AssertionError("busy_o is not asserted \n" \
            f"current_state : {dut.current_state.value}")
        
        dut.data_valid_i.value = 0
        
        # cocotb.start_soon(print_states(dut))
    
        await clk
    else: raise AssertionError("busy_o is not de-asserted")