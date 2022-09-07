from nebula.new_nebula import Nebula
from time import sleep
from random import random


test = Nebula(speed=1)

test.director()
if len(test.emission_list) > 0:
    emission_val = test.emission_list.pop()
    # print(emission_val)
else:
    sleep(1)
    test.user_input(random())





#
# dict = NebulaDataEngine()
#
# dict.random_dict_fill()
#


# from digiDobot import Digidobot
#
# digibot = Digidobot()
#
# digibot.stave()

# digibot.letters("m")



# a = digibot.interface.get_alarms_state()
# print(a)
#
# # digibot.bot.print_alarms(a)
# digibot.interface.clear_alarms_state()
# a = digibot.interface.get_alarms_state()
#
# print(a)



# digibot.circle(50)
#
# digibot.reset_errors()

# digibot.home()

# digibot.squiggle([(10, 50, -50),
#                   (20, 20, 20),
#                   (-25, -10, 40)
#                   ])

# digibot.home()
#
# digibot.centre()

# digibot.move_to((10, -20))

# digibot.circle_arc(1, [(10, 50, -50)])
# digibot.dot()

# digibot.circle_line(2, (-20, 45))
# digibot.line((-20, 45))

# digibot.circle(10)



# # from serial.tools import list_ports
# # import random
# # import pydobot
# #
# # available_ports = list_ports.comports()
# # print(f'available ports: {[x.device for x in available_ports]}')
# # port = available_ports[-1].device
# #
# # device = pydobot.Dobot(port=port, verbose=False)
# #
# # # device._set_queued_cmd_clear()
# # # state home position
# # (x, y, z, r, j1, j2, j3, j4) = device.pose()
# #
# # straight line forward (2cms)
# # device.move_to(x+50, y-50, z, r, wait=True)
# #
# # # straight line diagonal
# # device.slide_to(x+50, y+100, z, r, wait=True)
# #
# #
#
#
# # pen up to start
# # old_z = z + 5
# # device.move_to(x, y, old_z, r, wait=True)
# # drawing loop
# # while True:
# for t in range(100):
#     # print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')
#
#     draw_ratio = random.random() * 10
#
#     # make a random decision about x, y, & r
#     if random.getrandbits(1):
#         new_x = int(x - ((random.random() * 10) * draw_ratio))
#     else:
#         new_x = int(x + ((random.random() * 10) * draw_ratio))
#
#     if random.getrandbits(1):
#         new_y = int(y - ((random.random() * 10) * draw_ratio))
#     else:
#         new_y = int(y + ((random.random() * 10) * draw_ratio))
#
#     if random.getrandbits(1):
#         new_r = int(r - ((random.random() * 10) * draw_ratio))
#     else:
#         new_r = int(r + ((random.random() * 10) * draw_ratio))
#
#     # move according to new coords
#     # device.move_to(new_x, new_y, old_z, new_r, wait=True)
#
#     # pen up or down
#     if random.random() > 0.75:
#         new_z = z+5
#     else:
#         new_z = z
#
#     if random.getrandbits(1):
#         device.move_to(new_x, new_y, new_z, new_r)
#     else:
#         device.slide_to(new_x, new_y, new_z, new_r)
#
#     old_z = new_z
#
#     device.wait(int((random.random() * 10000) / 10))
#
# device.slide_to(x, y, z, r, wait=True)
# device.pose()
#
# digibot.close()
