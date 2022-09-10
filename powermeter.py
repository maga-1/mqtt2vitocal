#!/usr/bin/env python
"""
Pymodbus Server With Updating Thread
--------------------------------------------------------------------------

This is an example of having a background thread updating the
context while the server is operating. This can also be done with
a python thread::

    from threading import Thread

    thread = Thread(target=updating_writer, args=(context,))
    thread.start()
"""
# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from lib2to3.pgen2.token import RBRACE
from multiprocessing import context
from pymodbus.version import version
from pymodbus.server.asynchronous import StartTcpServer, StartSerialServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

from pymodbus.payload import BinaryPayloadBuilder, Endian

import paho.mqtt.client as mqtt
from thread_safe_datastore import *

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#----------------------------------------------------------------------------
# Settings
#----------------------------------------------------------------------------

topic = "strom/wp/restpower"
mqtt_server = "server.ganzinger.de"
mqtt_port = 1883

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #

def run_updating_server():
    # ----------------------------------------------------------------------- # 
    # initialize your data store
    # ----------------------------------------------------------------------- # 
    
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ThreadSafeDataBlock(ModbusSequentialDataBlock(0, [0]*100)),
        ir=ModbusSequentialDataBlock(0, [0]*100))

    global context
    context = ModbusServerContext(slaves=store, single=True)
    
    # ----------------------------------------------------------------------- # 
    # initialize the server information
    # ----------------------------------------------------------------------- # 
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = version.short()
    
    # ----------------------------------------------------------------------- # 
    # run the server you want
    # ----------------------------------------------------------------------- # 
    #StartTcpServer(context, identity=identity, address=("localhost", 5020))
    StartSerialServer(context, identity=identity, port='/dev/ttyUSB1', parity='E', baudrate='19200', stopbits=1, bytesize=8, framer = ModbusRtuFramer)

######
# mqtt message handler
######
def on_message(mqttc, obj, msg):
    log.debug("Message received. T: "+ msg.topic + " QOS: " + str(msg.qos) + " PL: " + str(msg.payload))
    builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
    builder.reset() # Reset Old entries
    try:
       rp = round(int(msg.payload) / 30) 
    except ValueError:
        rp = 0
        log.error("Message received not an int: "+ str(msg.payload))
    builder.add_16bit_int(rp)
    payload = builder.to_registers()   # Convert to int values
    log.debug("new value: "+ str(rp))
    register = 3
    slave_id = 60
    addresses = [37, 42, 47]
    for address in addresses:
        context[slave_id].setValues(register, address, payload)

if __name__ == "__main__":
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.connect_async(mqtt_server, mqtt_port, 60)
    mqttc.subscribe(topic, 0)
    mqttc.loop_start()
    run_updating_server()


