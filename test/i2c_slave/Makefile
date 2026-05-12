SIM =  icarus

TOPLEVEL_LANG = verilog

VERILOG_SOURCES = ../../src/i2c_slave.sv

COCOTB_TOPLEVEL = i2c_slave

COCOTB_TEST_MODULES = i2c_slave_test

WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim

view_waves:
	gtkwave sim_build/i2c_top.fst
