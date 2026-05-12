import random
import cocotb
from cocotb.triggers import ClockCycles, RisingEdge, Timer
from cocotb.clock import Clock

# Parameters

CLOCKPERIOD = 10
MAX_CLOCKS = 150
SINGLE_WRITE = True
SINGLE_READ = True
PRINT_STATES = False
slave_sates = ["IDLE","ADDR","R_DATA", 
                "W_DATA","RECV_ACK","SEND_ACK"]
master_sates = ["IDLE","START", "BUFF", "ADDR","R_DATA", 
                "W_DATA","RECV_ACK","SEND_ACK","STOP"]

# Clock

async def clk_(dut, N_CLKS):
    clk = Clock(dut.clk_i, CLOCKPERIOD, 'ns')
    clk.start()
    await ClockCycles(dut.clk_i, int(N_CLKS))
    clk.stop()

# Next clock cycle

async def NextClockCycle(dut): 
    await RisingEdge(dut.clk_i)
    await Timer(1)

# Reset

async def reset(dut, N):
    dut.rst_i.value = 0
    for _ in range(N):
        await RisingEdge(dut.clk_i)
    dut.rst_i.value = 1

# Print states

async def print_states(dut, master=True, slave=True):
    if PRINT_STATES:
        while True:
            await RisingEdge(dut.clk_i)
            if master and slave:
                cocotb.log.info(f"Master state: {master_sates[int(dut.i2c_master_i.current_state.value)]}({int(dut.i2c_master_i.current_state.value)}); Slave state: {slave_sates[int(dut.i2c_slave_i.current_state.value)]}({int(dut.i2c_slave_i.current_state.value)})")
            else:
                if master:
                    cocotb.log.info(f"Master state: {master_sates[int(dut.i2c_master_i.current_state.value)]}({int(dut.i2c_master_i.current_state.value)})")
                if slave:
                    cocotb.log.info(f"Slave state: {slave_sates[int(dut.i2c_slave_i.current_state.value)]}({int(dut.i2c_slave_i.current_state.value)})")

# Initialize inputs

async def init_inputs(dut):
    # master-side
    dut.rw_i.value = 0
    dut.master_data_valid_i.value = 0
    dut.addr_i.value = 0
    dut.master_data_i.value = 0
    # slave-side
    dut.slave_data_valid_i.value = 0
    dut.slave_data_i.value = 0    

# Single-write

if SINGLE_WRITE:
    @cocotb.test()
    async def single_write(dut):

        # Setup
        clk = cocotb.start_soon(clk_(dut, MAX_CLOCKS/2))    
        cocotb.start_soon(print_states(dut))
        await init_inputs(dut)
        await reset(dut, 5)

        await RisingEdge(dut.clk_i)

        # Start transmission
        if (dut.busy_o.value == 0):
            dut.master_data_valid_i.value = 1
            data = random.getrandbits(32)
            dut.master_data_i.value = data
            dut.rw_i.value = 0
            addr = random.getrandbits(7)
            dut.addr_i.value = addr
            await RisingEdge(dut.clk_i)
            dut.master_data_valid_i.value = 0
            await NextClockCycle(dut)
            try:
                assert (dut.busy_o.value == 1)
            except:
                raise AssertionError("busy_o is de-asserted")
            
            # Catch address
            while (dut.slave_data_valid_o.value != 1):
                await RisingEdge(dut.clk_i)
            
            address_on_slave = dut.addr_o.value

            try:
                assert address_on_slave == format(addr, f'0{7}b')
            except:
                raise AssertionError(f"Transmitted address mismatch --> expected {format(addr, f'0{7}b')} ({addr}), got {address_on_slave} ({int(address_on_slave)})")
            
            await NextClockCycle(dut)
            
            # Catch data
            while (dut.slave_data_valid_o.value != 1):
                await RisingEdge(dut.clk_i)
            
            data_on_slave = dut.slave_data_o.value

            try:
                assert data_on_slave == format(data, f'0{32}b')
            except:
                raise AssertionError(f"Transmitted data mismatch --> expected {format(data, f'0{32}b')} ({data}), got {data_on_slave} ({int(data_on_slave)})")
            
            await NextClockCycle(dut)
            

            # Proper termination
            try:
                assert master_sates[int(dut.i2c_master_i.current_state.value)] == "IDLE"
            except:
                raise AssertionError(f"Master port not terminated properly, currently at {master_sates[int(dut.i2c_master_i.current_state.value)]}")
            
            try:
                assert slave_sates[int(dut.i2c_slave_i.current_state.value)] == "IDLE"
            except:
                raise AssertionError(f"Slave port not terminated properly, currently at {slave_sates[int(dut.i2c_slave_i.current_state.value)]}")
            
            # Test passed
            await ClockCycles(dut.clk_i, 10)
            cocotb.pass_test("yay!")
        else:
            raise AssertionError("busy_o is asserted at the start")
        
# Single-read

if SINGLE_READ:
    @cocotb.test()
    async def single_read(dut):
        
        # Setup
        clk = cocotb.start_soon(clk_(dut, MAX_CLOCKS/2))    
        cocotb.start_soon(print_states(dut))
        await init_inputs(dut)
        await reset(dut, 5)

        await RisingEdge(dut.clk_i)

        # Start transmission
        if (dut.busy_o.value == 0):
            dut.master_data_valid_i.value = 1
            dut.rw_i.value = 1
            addr = random.getrandbits(7)
            dut.addr_i.value = addr
            await RisingEdge(dut.clk_i)
            dut.master_data_valid_i.value = 0
            await NextClockCycle(dut)

            try:
                assert (dut.busy_o.value == 1)
            except:
                raise AssertionError("busy_o is de-asserted")
            
            # Catch address & send data
            while (dut.slave_data_valid_o.value != 1):
                await RisingEdge(dut.clk_i)
            
            address_on_slave = dut.addr_o.value

            try:
                assert address_on_slave == format(addr, f'0{7}b')
            except:
                raise AssertionError(f"Transmitted address mismatch --> expected {format(addr, f'0{7}b')} ({addr}), got {address_on_slave} ({int(address_on_slave)})")
            
            if (dut.rw_o.value == 1):
                data = random.getrandbits(32)
                dut.slave_data_i.value = data
                dut.slave_data_valid_i.value = 1
            else:
                raise AssertionError("rw_o is not 1 (HIGH - R))")
            
            await RisingEdge(dut.clk_i)
            dut.slave_data_valid_i.value = 0
            await NextClockCycle(dut)      

            # Catch data
            while (dut.master_data_valid_o.value != 1):
                await RisingEdge(dut.clk_i)
            
            data_on_master = dut.master_data_o.value

            try:
                assert data_on_master == format(data, f'0{32}b')
            except:
                raise AssertionError(f"Transmitted data mismatch --> expected {format(data, f'0{32}b')} ({data}), got {data_on_master} ({int(data_on_master)})")
            
            await NextClockCycle(dut)
            
            # Proper termination
            try:
                assert master_sates[int(dut.i2c_master_i.current_state.value)] == "IDLE"
            except:
                raise AssertionError(f"Master port not terminated properly, currently at {master_sates[int(dut.i2c_master_i.current_state.value)]}")
            
            try:
                assert slave_sates[int(dut.i2c_slave_i.current_state.value)] == "IDLE"
            except:
                raise AssertionError(f"Slave port not terminated properly, currently at {slave_sates[int(dut.i2c_slave_i.current_state.value)]}")
            
            # Test passed
            await ClockCycles(dut.clk_i, 10)
            cocotb.pass_test("yay!")
        else:
            raise AssertionError("busy_o is asserted at the start")