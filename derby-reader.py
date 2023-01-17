import asyncio
import json
import logging
import sys

import serial

"""
Serial<id=0x7fe270656e30, open=True>(port='/dev/ttyUSB0', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)

Serial Port Configuration:
    PORT: "/dev/ttyUSB0"
    BAUD: 9600
    ByteSize: 8
    Parity: 'N'
    StopBits: 1
    Timeout: None
    Xon/Xoff: False
    RTS/CTS: False
    DSR/DTR: False

Track Equipment operates using the following values:

- ASCII 64 - at symbol (@)      reset
- ASCII 32 - space              break between values
- ASCII 61 - equal symbol (=)   break between name and value
- ASCII 13,10 - \r\n            line break

Data goes like follows:
- A=0.000! B=0.000" C=0.000# D=0.000 F=0.000

"""

LOG = logging.getLogger()

class DerbyTrackReader(object):

    def __init__(self, serialPort, handler):
        self.serialPort = serialPort
        self.handler = handler

    async def read(self):
        while True:
            data = self.serialPort.readline().decode('utf-8')
            LOG.debug(f"SERIAL PORT: '{data}'")
            results = self.decode(data)
            if not self.handler is None:
                self.handler(results)

    def decodeTime(self, value):
        laneName, laneTime = None, None
        splitEquals = value.split("=")
        laneName = splitEquals[0]
        laneTime = float(splitEquals[1][:5])
        return (laneName, laneTime)

    def decode(self, data):
        scrape_reset = data[1:]
        parts = scrape_reset.split(' ')
        raceTimes = [
            self.decodeTime(x)
            for x in parts
            if '=' in x
        ]
        return(raceTimes)

def raceHandler(raceTimes):
    raceData = {
        lane: value
        for lane, value in raceTimes
    }
    LOG.debug(f'Race Data - {raceData} - JSON: {json.dumps(raceData)}')

def main():
    lh = logging.StreamHandler(sys.stdout)
    lh.setLevel(logging.DEBUG)

    lf = logging.FileHandler('.derby-track-py.log')
    lf.setLevel(logging.DEBUG)

    log = logging.getLogger()
    log.addHandler(lh)
    log.addHandler(lf)
    log.setLevel(logging.DEBUG)

    serialPort = serial.Serial(
        port="/dev/ttyUSB0",
    )
    derby = DerbyTrackReader(serialPort, raceHandler)
    asyncio.run(derby.read())
    serialPort.close()

if __name__ == "__main__":
    sys.exit(main())
