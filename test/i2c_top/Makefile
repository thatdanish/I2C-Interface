SIM =  icarus

TOPLEVEL_LANG = verilog

VERILOG_SOURCES = ../../src/I2CTop.sv ../../src/i2c_slave.sv ../../src/i2c_master.sv 

COCOTB_TOPLEVEL = I2CTop

COCOTB_TEST_MODULES = i2c_top_test

WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim

view_waves:
	gtkwave sim_build/I2CTop.fst