# mqtt2vitocal

Software for emulating Viessmann energy meters to optimize photovoltaic power consumption with heat pumps. It was tested with a Vitocal 200-S heat pump, others should work as well. Make sure to check with the Viessman manual whether the values for surplus energy must be positive or negative, also double check in the diagnosis menu of your device.
The program was inspired by this thread: https://openwb.de/forum/viewtopic.php?f=9&t=1568
The software makes use of the pymodbus https://pymodbus.readthedocs.io/en/latest/ library and is mostly following the examples from there. For mqtt connection, the paho library https://www.eclipse.org/paho/index.php?page=clients/python/index.php has to be installed. Warning: Only use python 3, for python 2 the automatic reconnect to the mqtt broker does not work reliably.

In 
