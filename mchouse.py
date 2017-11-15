def build_a_house(mc):
    mc.postToChat("Building your new house. Please standby...")
    pos = mc.player.getPos()
    # Build the house around the player so offset
    pos.x = pos.x - 5
    pos.z = pos.z - 5

    # Stone walls first
    material = 1
    for y in range(0, 5):
        for x in range(0, 10):
            mc.setBlock(pos.x + x, pos.y + y, pos.z, material)
        for z in range(0, 10):
            mc.setBlock(pos.x + 9, pos.y + y, pos.z + z, material)
        for x in range(0, 10):
            mc.setBlock(pos.x + x, pos.y + y, pos.z + 9, material)
        for z in range(0, 10):
            mc.setBlock(pos.x, pos.y + y, pos.z + z, material)

    # Then wooden roof
    material = 5
    for y in range(0, 5):
        for x in range(0 + y, 10-y):
            mc.setBlock(pos.x + x, pos.y + y + 5, pos.z + y, material)
        for z in range(0 + y, 10 - y):
            mc.setBlock(pos.x + 9 - y, pos.y + y + 5, pos.z + z, material)
        for x in range(0 + y, 10 - y):
            mc.setBlock(pos.x + x, pos.y + y + 5, pos.z + 9 - y, material)
        for z in range(0 + y, 10 - y):
            mc.setBlock(pos.x + y, pos.y + y + 5, pos.z + z, material)

    # Then knock out a door
    material = 0
    mc.setBlock(pos.x + 5, pos.y, pos.z, material)
    mc.setBlock(pos.x + 5, pos.y + 1, pos.z, material)
    mc.setBlock(pos.x + 5, pos.y + 2, pos.z, material)
    mc.setBlock(pos.x + 6, pos.y, pos.z, material)
    mc.setBlock(pos.x + 6, pos.y + 1, pos.z, material)
    mc.setBlock(pos.x + 6, pos.y + 2, pos.z, material)

