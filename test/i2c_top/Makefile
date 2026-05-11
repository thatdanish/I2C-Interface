SIM =  icarus

TOPLEVEL_LANG = verilog

VERILOG_SOURCES = ../../src/i2c_top.sv

COCOTB_TOPLEVEL = i2c_top

COCOTB_TEST_MODULES = i2c_top_test

WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim

view_waves:
	gtkwave sim_build/i2c_slave.fst
