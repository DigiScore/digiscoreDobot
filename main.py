from nebula.nebula import Nebula
from time import sleep
from random import random, randrange, getrandbits
import pyaudio
import numpy as np

from digiDobot import Digidobot

digibot = Digidobot()

test = Nebula(speed=1)

test.director()
# if len(test.emission_list) > 0:
#     emission_val = test.emission_list.pop()
    # print(emission_val)
# else:
#     sleep(1)
#     test.user_input(random())

# set up mic listening funcs
CHUNK = 2 ** 11
RATE = 44100
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)


def rnd():
    if getrandbits(1):
        pn = 10
    else:
        pn = -10
    return random() * pn

def dobot_control(incoming_value):
    value_int = int(incoming_value * 10)
    if getrandbits(1):
        draw = True
    else:
        draw = False

    print(f'DOBOT input val = {value_int}, drawing? {draw}')

    if value_int == 1:
        digibot.circle(rnd(), draw)
    elif value_int == 2:
        squiggle_list = []
        for n in range(randrange(2, 10)):
            squiggle_list.append((rnd(), rnd(), rnd()))
        digibot.squiggle(squiggle_list, draw)
    elif value_int == 3:
        digibot.move_to((rnd(), rnd()))
    elif value_int == 4:
        digibot.circle_arc(rnd(), [(rnd(), rnd(), rnd())], draw)
    elif value_int == 5:
        digibot.dot()
    elif value_int == 6:
        digibot.circle_line(rnd(), (rnd(), rnd()), draw)
    elif value_int == 7:
        digibot.line((rnd(), rnd()), draw)
    elif value_int == 8:
        digibot.circle(rnd())
    else:
        digibot.move_to((rnd(), rnd()))



while True:
    data = np.frombuffer(stream.read(CHUNK,
                                     exception_on_overflow=False),
                         dtype=np.int16)
    peak = np.average(np.abs(data)) * 2
    # print('peak ============ ', peak)

    # do stuff with this data
    # if peak > 2000:
    #     bars = "#" * int(50 * peak / 2 ** 16)
    #     print("%05d %s" % (peak, bars))

    # share the data
    # new_value = ( (old_value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min
    normalised_peak = ((peak - 0) / (20000 - 0)) * (1 - 0) + 0
    if normalised_peak > 1.0:
        normalised_peak = 1.0

    # print('normalised peak === ', normalised_peak)
    test.user_input(normalised_peak)

    if len(test.emission_list) > 0:
        emission_val = test.emission_list.pop()
        dobot_control(emission_val)
        # print(emission_val)

#
# dict = NebulaDataEngine()
#
# dict.random_dict_fill()
#



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
