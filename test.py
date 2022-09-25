import sys
import os
import math
from random import randrange, random, getrandbits
from time import time, sleep

from serial.tools import list_ports
from digibot import Digibot

digibot = Digibot(verbose=False)
digibot.draw_stave()

(x, y, z, r, j1, j2, j3, j4) = digibot.pose()
print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

# print('test wiggle')
# digibot.move_to(x + 20, y, z, r, wait=True)
# # device.wait(1000)
# digibot.move_to(x, y, z, r, wait=True)

# start operating vars
duration_of_piece = 480  # seconds
running = True
old_value = 0
start_time = time()
end_time = start_time + duration_of_piece


def move_y():
    # move y along a bit
    elapsed = time() - start_time

    # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    newy = (((elapsed - 0) * (210 - -210)) / (duration_of_piece - 0)) + -210

    # current_y_delta = elapsed * sub_division_of_duration
    (x, y, z, r, j1, j2, j3, j4) = digibot.pose()
    print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

    # lift up pen
    digibot.move_to_relative(0, 0, 5, 0)
    print('elapsed time = ', elapsed)
    print(f'old y = {y}, move to = {newy}')
    if x <= 200 or x >= 300:
        x = 250
    digibot.move_to(x, newy, 0, r, False)
    # digibot.move_to_relative(0, 0, -5, 0)

def rnd(power):
    pos = 1
    if getrandbits(1):
        pos = -1
    return (randrange(1, 5) + power) * pos

# todo - move to an emmission system like Fabrizio's score
while time() < end_time:
    # move_y()
    digibot.clear_alarms()

    if getrandbits(1):
        power = randrange(1, 10)
        if getrandbits(1):
            digibot.squiggle([(rnd(power), rnd(power), rnd(power))])
        else:
            digibot.move_to_relative(rnd(power), rnd(power), 0, 0, True)
    else:
        print('move y')
        move_y()

    sleep(0.2)

digibot.close()





# from serial.tools import list_ports
# from time import time
# import pydobot
#
# available_ports = list_ports.comports()
# print(f'available ports: {[x.device for x in available_ports]}')
# port = available_ports[-1].device
#
# digibot = pydobot.Dobot(port=port, verbose=True)
#
# (x, y, z, r, j1, j2, j3, j4) = digibot.pose()
# print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')
#
# for i in range(1):
#     digibot.move_to(x + 20, y, z, r, wait=True)
#     # device.wait(1000)
#     digibot.move_to(x, y, z, r, wait=True)
#     # device.wait(1000)
#
# # digibot.close()
#
#
#
#
# #
# #
# #
# #
# # from main import DrawBot
# # from digiDobot import Digidobot
# # from time import time, sleep
# # from random import randrange
# #
# #
# #
# # digibot = Digidobot(verbose=False)
# # digibot.reset_errors()
#
# # start operating vars
# duration_of_piece = 60  # seconds
# running = True
# old_value = 0
# start_time = time()
# end_time = start_time + duration_of_piece
# # sub_division_of_duration = 420 / duration_of_piece #/ 420
# # print('sub division = ', sub_division_of_duration)
# #
# #
# def move_y():
#     # move y along a bit
#     elapsed = time() - start_time
#
#     # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
#     newy = (((elapsed - 0) * (210 - -210)) / (60 - 0)) + -210
#
#     # current_y_delta = elapsed * sub_division_of_duration
#     position_list = digibot.pose()
#     print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')
#
#     nowx, nowy, nowz, nowr = position_list[:4]
#     print('elapsed time = ', elapsed)
#     print(f'old y = {nowy}, move to = {newy}')
#     if 200 <= nowx <= 300:
#         nowx = 250
#     digibot.move_to(nowx, newy, 0, nowr)
# #
# # def random_move():
# #     incoming_command = randrange(10)
# #     print("random command = ", incoming_command)
# #
# #     # low power response from AI Factory
# #     if incoming_command < 3:
# #         # lift pen up for movement
# #         digibot.slide_to_rel_xyz((0, 0, 5))
# #         print(f'DOBOT: {incoming_command}: draw command = "move to relative", ')
# #         digibot.slide_to_rel_xyz((5, 5, 0))
# #         # pen auto drops because of move_y()
# #
# #     elif incoming_command >= 7:
# #         print(f'DOBOT: {incoming_command}: draw command = "draw to relative", ')
# #         digibot.slide_to_rel_xyz((5, 5, 0))
# #
# #     else:
# #         squiggle_list = (5,
# #                          5,
# #                          5)
# #         digibot.squiggle([squiggle_list])
# #         print(f'DOBOT: {incoming_command}: draw command = "squiggle", ')
# #
# while time() < end_time:
#     print('move y')
#     move_y()
# #
# #     random_move()
# #
# #     print('choose random')
# #     q = digibot.interface.get_current_queue_index()
# #     print('qqqqqqqqqqqqqqqqqqqqqqqq                     ', q)
# #
# #     # while q == digibot.interface.get_current_queue_index():
# #     sleep(1)
# #     q = digibot.interface.get_current_queue_index()
# #     print('qqqqqqqqqqqqqqqqqqqqqqqq                     ', q)
#
#
# digibot.close()
