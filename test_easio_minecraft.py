from mcpi.minecraft import Minecraft
import easio
import mchouse

#########################
# Set up the I2C GPIO extender using easio
#########################
i2c = easio.i2c(0, 0x20)
i2c.setPinMode(0, 7, 1)
i2c.setAllPins(0, 0)

#########################
# Set up the LED pin positions
#########################
GREEN = 0b00000001
AMBER = 0b00000010
RED   = 0b00000100

#########################
# Connect to Minecraft
#########################
mc = Minecraft.create()
mc.postToChat("Connected")

#########################
# Create a callback for when the physical button's state changes
# We'll make it build a house when the button is released
#########################
def onButtonStateChange(bank, pin, oldValue, newValue):
    if(oldValue and not newValue):
        mchouse.build_a_house(mc)

#########################
# Add the callback as a listener for the button on pin 7
# This will now listen on a seperate thread to the
# main thread, allowing us to do other stuff
#########################
i2c.addPinInputChangeListener(0, 7, onButtonStateChange)

#########################
# Set up a detection loop to detect what the player is standing
# on and setting LEDs accordingly
#########################
while True:
    pos = mc.player.getPos()
    block_beneath = mc.getBlock(pos.x, pos.y-1, pos.z)
    #print(block_beneath)
    if block_beneath == 2:
        i2c.setAllPins(0, GREEN)
    elif block_beneath == 12:
        i2c.setAllPins(0, AMBER)
    elif block_beneath == 1:
        i2c.setAllPins(0, GREEN | RED)
    elif block_beneath == 35:
        i2c.setAllPins(0, GREEN | AMBER| RED)
    elif block_beneath == 18:
        i2c.setAllPins(0, GREEN)
    elif block_beneath == 41:
        i2c.setAllPins(0, AMBER)
    elif block_beneath == 9:
        i2c.setAllPins(0, GREEN)
    elif block_beneath == 3:
        i2c.setAllPins(0, GREEN | AMBER| RED)
    elif block_beneath == 79:
        i2c.setAllPins(0, RED)
    elif block_beneath == 5:
        i2c.setAllPins(0, GREEN | AMBER)
    else:
        i2c.setAllPins(0, 0)
