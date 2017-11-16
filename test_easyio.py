import easio
import time

buttonPresses = 0

def onButtonPress(bank, pin, oldValue, newValue):
    global buttonPresses
    #print("Pin", pin, "changed from", oldValue, "to", newValue)
    if oldValue and not newValue:
        buttonPresses = buttonPresses +1
        test_i2c.setAllPins(0, 0)
        test_i2c.setPinValue(0, buttonPresses%3, 1)
        # Deliberately delay the EDT
        time.sleep(3)

def testInputListeners(test_i2c):
    test_i2c.addPinInputChangeListener(0, 7, onButtonPress)
    print("Ready to go!")
    while True:
        time.sleep(1)

test_i2c = easio.i2c(0, 0x20)
test_i2c.setPinMode(0, 7, 1)
test_i2c.setAllPins(0, 0b00000001)
testInputListeners(test_i2c)



###################################
# Other tests
###################################



# Create a lambda for getting current time
current_time_ms = lambda: int(round(time.time() * 1000))



def testOutput(test_i2c):
    print("Testing putput")
    test_i2c.setAllPins(0b00000010)
    time.sleep(1)
    test_i2c.setPinValue(1, 0)
    test_i2c.setPinValue(0, 1)
    test_i2c.setPinValue(2, 1)

def testInput(test_i2c):
    # Don't have the loop chewing all CPU
    delay = 20
    lastState = False
    print("Starting loop")
    startTime = 0;
    
    while True:
        currentState = test_i2c.readPinValue(7)
        if (not lastState) and currentState:
            lastState = True
            startTime = current_time_ms()
        elif lastState and (not currentState):
            print("Pressed for", current_time_ms() - startTime, "ms.")
            lastState = False
        time.sleep(delay/1000)



#testOutput(test_i2c)
#testInput(test_i2c)
