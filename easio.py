import smbus
import threading
import time
import copy

    
def setBit(bit, value):
    return value | (1<<bit)

def clearBit(bit, value):
    return value & ~(1<<bit)

class i2c:
    # Command for setting IO direction on bank A
    IODIRA = 0x00
    # Command for setting IO direction on bank B
    IODIRB = 0x01
    # Command for setting output values on bank A
    OLATA = 0x14
    # Command for setting output values on bank B
    OLATB = 0x15
    # Command for reading data from bank A
    GPIOA = 0x12
    # Command for reading data from bank B
    GPIOB = 0x13
    # Delay for IO check loop
    IODELAY = 20.0 / 1000.0
    
    def __init__(self, i2cInterface, i2cAddress):
        self.i2cInterface = i2cInterface
        self.i2cAddress = i2cAddress
        self.bus = smbus.SMBus(self.i2cInterface)
        self.bankDir = [0b00000000, 0b00000000]
        self.bankOutputValues = [0b00000000, 0b00000000]
        self.inputChangeListeners = [[[] for _ in range(8)] for _ in range(2)]
        self.lastInputValues = [[0 for _ in range(8)]for _ in range(2)]
        self.newInputValues = [[0 for _ in range(8)]for _ in range(2)]
        self.inputsChanged = False
        # By default, set all pins on bank A and B to output
        self.bus.write_byte_data(self.i2cAddress, i2c.IODIRA, self.bankDir[0])
        self.bus.write_byte_data(self.i2cAddress, i2c.IODIRB, self.bankDir[1])
        # Create callback thread condition
        self.cond = threading.Condition(threading.Lock())
        
        # Startup input read thread
        t = threading.Thread(target=i2c.doInputCheckLoop, args=(self,))
        t.setDaemon(True)
        t.start()

        # Startup event dispatch thread
        edt = threading.Thread(target=i2c.doNotifyListeners, args=(self,))
        edt.setDaemon(True)
        edt.start()


    def setPinMode(self, bank, pin, mode):
        if(mode):
            self.bankDir[bank] = setBit(pin, self.bankDir[bank])
        else:
            self.bankDir[bank] = clearBit(pin, self.bankDir[bank])
        if bank == 0:
            self.bus.write_byte_data(self.i2cAddress, i2c.IODIRA, self.bankDir[0])
        else:
            self.bus.write_byte_data(self.i2cAddress, i2c.IODIRB, self.bankDir[1])

    def setPinValue(self, bank, pin, mode):
        if(mode):
            self.bankOutputValues[bank] = setBit(pin, self.bankOutputValues[bank])
        else:
            self.bankOutputValues[bank] = clearBit(pin, self.bankOutputValues[bank])
        i2c.setAllPins(self, bank, self.bankOutputValues[bank])

    def setAllPins(self, bank, bankValues):
        self.bankOutputValues[bank] = bankValues
        if bank == 0:
            self.bus.write_byte_data(self.i2cAddress, i2c.OLATA, bankValues)
        else:
            self.bus.write_byte_data(self.i2cAddress, i2c.OLATB, bankValues)

    def readAllPins(self, bank):
        if bank == 0:
            values = self.bus.read_byte_data(self.i2cAddress, i2c.GPIOA)
        else:
            values = self.bus.read_byte_data(self.i2cAddress, i2c.GPIOB)
        return values

    def readPinValue(self, bank, pin):
        return i2c.readAllPins(self, bank) & (1<<pin)

    def addPinInputChangeListener(self, bank, pin, listener):
        self.inputChangeListeners[bank][pin].append(listener)

    def removePinInputChangeListener(self, bank, pin, listener):
        self.inputChangeListeners[bank][pin].remove(listener)

    def doInputCheckLoop(self):
        while True:
            self.cond.acquire()
            for bank in range (0, 2):
                allPinValues = i2c.readAllPins(self, bank)
                for pin in range(0, 8):
                    if self.bankDir[bank] & (1 << pin):
                        newValue = allPinValues & (1<<pin)
                        oldValue = self.lastInputValues[bank][pin]
                        self.newInputValues[bank][pin] = newValue
                        if newValue != oldValue:                            
                            self.inputsChanged = True
                            self.cond.notify()
            self.cond.release()
            time.sleep(i2c.IODELAY)

    def doNotifyListeners(self):
        while True:
            self.cond.acquire()
            while not self.inputsChanged:
                self.cond.wait()            
            self.inputsChanged = False
            newValues = copy.deepcopy(self.newInputValues)
            oldValues = copy.deepcopy(self.lastInputValues)
            self.lastInputValues = copy.deepcopy(self.newInputValues)
            self.cond.release()
            for bank in range (0, 2):
                for pin in range(0, 8):
                    if self.bankDir[bank] & (1 << pin):                        
                        if newValues[bank][pin] != oldValues[bank][pin]:
                            for listener in self.inputChangeListeners[bank][pin]:
                                listener(bank, pin, oldValues[bank][pin], newValues[bank][pin])
