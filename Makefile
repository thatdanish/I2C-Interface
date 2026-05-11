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

# I2C Top

i2c_top:	
	cd test/i2c_top && make

wave_i2c_slave:
	cd test/i2c_top && make view_waves