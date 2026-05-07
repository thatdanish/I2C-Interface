# I2C Master

i2c_master:
	cd test/i2c_master && make

wave_i2c_master:
	cd test/i2c_master && make view_waves

# I2C Slave

i2c_slave:
	cd test/i2c_slave && make

wave_i2c_slave:
	cd test/i2c_slave && make view_waves