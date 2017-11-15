import smbus
import threading
import time

class i2c:
    #TODO: Bank B - everything is Bank A only at the moment
    # Command for setting IO direction on bank A
    IODIRA = 0x00
    # Command for setting output values on bank A
    OLATA = 0x14
    # Command for reading data from bank A
    GPIOA = 0x12
    # Delay for IO check loop
    IODELAY = 20.0 / 1000.0
    
    def __init__(self, i2cInterface, i2cAddress):
        self.i2cInterface = i2cInterface
        self.i2cAddress = i2cAddress
        self.bus = smbus.SMBus(self.i2cInterface)
        self.bankADir = 0b00000000
        self.bankAValues = 0b00000000
        self.inputChangeListeners = [[] for _ in range(8)]
        self.lastInputValues = [0 for _ in range(8)]
        # By default, set all pins on bank A to output
        self.bus.write_byte_data(self.i2cAddress, i2c.IODIRA, self.bankADir)
        # Startup input read thread
        t = threading.Thread(target=i2c.doInputCheckLoop, args=(self,))
        t.start()
    
    def setBit(bit, value):
        return value | (1<<bit)

    def clearBit(bit, value):
        return value & ~(1<<bit)

    def setPinMode(self, pin, mode):
        if(mode):
            self.bankADir = i2c.setBit(pin, self.bankADir)
        else:
            self.bankADir = i2c.clearBit(pin, self.bankADir)
        self.bus.write_byte_data(self.i2cAddress, i2c.IODIRA, self.bankADir)

    def setPinValue(self, pin, mode):
        if(mode):
            self.bankAValues = i2c.setBit(pin, self.bankAValues)
        else:
            self.bankAValues = i2c.clearBit(pin, self.bankAValues)
        i2c.setAllPins(self, self.bankAValues)

    def setAllPins(self, bankValues):
        self.bankAValues = bankValues
        self.bus.write_byte_data(self.i2cAddress, i2c.OLATA, bankValues)

    def readAllPins(self):
        return self.bus.read_byte_data(self.i2cAddress, i2c.GPIOA)

    def readPinValue(self, pin):
        return i2c.readAllPins(self) & (1<<pin)

    def addPinInputChangeListener(self, pin, listener):
        self.inputChangeListeners[pin].append(listener)

    def removePinInputChangeListener(self, pin, listener):
        self.inputChangeListeners[pin].remove(listener)

    def doInputCheckLoop(self):
        while True:
            allPinValues = i2c.readAllPins(self)
            for pin in range(0, 8):
                newValue = allPinValues & (1<<pin)
                oldValue = self.lastInputValues[pin]
                if newValue != oldValue:
                    self.lastInputValues[pin] = newValue
                    for listener in self.inputChangeListeners[pin]:
                        listener(pin, oldValue, newValue)
            time.sleep(i2c.IODELAY)
