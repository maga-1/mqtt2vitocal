# mqtt2vitocal

Software for emulating Viessmann energy meters to optimize photovoltaic power consumption with heat pumps. It was tested with a Vitocal 200-S heat pump, others should work as well. Make sure to check with the Viessman manual whether the values for surplus energy must be positive or negative, also double check in the diagnosis menu of your device.
The program was inspired by this thread: https://openwb.de/forum/viewtopic.php?f=9&t=1568
The software makes use of the [pymodbus](https://pymodbus.readthedocs.io/en/latest/) library and is mostly following the examples from there. 

For mqtt, the [paho library](https://www.eclipse.org/paho/index.php?page=clients/python/index.php) has to be installed. Warning: Only use python 3, for python 2 the automatic reconnect to the mqtt broker after connection loss does not work reliably.

## Configuration

At the beginning of `powermeter.py` you can find a configuration section for the mqtt connection:

```
#----------------------------------------------------------------------------
# Settings
#----------------------------------------------------------------------------

topic = "electricity/hp/restpower"
mqtt_server = "localhost"
mqtt_port = 1883
```
`mqtt_server` and `mqtt_port` cover the mqtt connection parameters. `topic` denotes the topic to subscribe for the remaining power. This script expects the remaining power in Watt as an integer value according to the specification of Viessmann (see below).

## Calculation of remaining power

The placement of the original power meter is a bit peculiar. It is assumed that the heat pump is the *very first* device *after the power meter* of the grid company. The Viessman power meter comes next, right after the heat pump, but before any other consumers. This means, the value of interest is the power delivered to the grid *plus* the power consumed by the heat pump.

### Example for Vitocal 200-S

The 200-S expects positive values if power is delivered to the grid. I use the power meter of my grid company to retrieve the current power `gridPower`. The value is *negative* when power is delivered *to* the grid. In addition, I use a separate power meter to measure the current power consumption of the heat pump `hpPower` (always positive). Consquently, I calcuate the remaining power `restPower` with the following formula (I do this in [Node-RED](https://nodered.org/)):

$$
restPower = hpPower - gridPower
$$

`restPower` should be published on mqtt as an integer value in Watt for use by this script. Please note, we do not have to consider individual phases, although the original power meter does deliver these values. The balance of all phases is sufficient. This script will simulate an even distribution for the heat pump. You can verify this in the photovoltaic diagnosis screen of the heat pump: You should see 1/3 of the remaining power per phase. The total value shows the balanced average power of the last ten minutes.
