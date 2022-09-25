import sys
import os
import math
from random import randrange, random, getrandbits
from time import time, sleep
from serial.tools import list_ports
from time import time
import pydobot

class Digibot:
    """Controls movement and shapes drawn by Dobot"""

    def __init__(self, verbose: bool = False):
        # set global path
        sys.path.insert(0, os.path.abspath('.'))

        # find available ports and locate Dobot (-1)
        available_ports = list_ports.comports()
        print(f'available ports: {[x.device for x in available_ports]}')
        port = available_ports[-1].device

        # initiate dobot and connect
        self.bot = pydobot.Dobot(port=port, verbose=verbose)

        # make a shared list/ dict
        self.draw_list = []

        print('locating home')
        self.home()
        input('remove pen, then press enter')

    def draw_stave(self, staves: int = 1):
        """Draws a  line across the middle of an A3 paper, symbolising a stave.
        Has optional function to draw multiple staves.
        Args:
            staves: number of lines to draw. Default = 1"""
        stave_start_pos = (250, 210, 0, 0)
        stave_end_pos = (250, -210, 0, 0)

        # goto start position for line draw, without pen
        x1, y1, z1, r1 = stave_start_pos[:4]
        x2, y2, z2, r2 = stave_end_pos[:4]
        self.bot.move_to(x1, y1, z1, r1)

        # draw a line/ stave
        input('Insert pen, then press enter')
        self.bot.move_to(x2, y2, z2, r2)

        # goto standby position
        input('waiting')
        self.bot.move_to_relative(0, 0, 10, 0)

    def squiggle(self, arc_list: list):
        """accepts a list of tuples that define a sequence of
        x, y deltas to create a sequence of arcs that define a squiggle.
        list (circumference point, end point x, end point y):
            circumference point: size of arc in pixels across x axis
            end point x, end point y: distance from last/ previous position
             """
        # if drawing:
        #     self.pen_ready(True)
        [x, y, z, r] = self.pose()[0:4]
        for arc in arc_list:
            # print(arc)
            circumference, dx, dy = arc[0], arc[1], arc[2]
            self.bot.go_arc(x + circumference, y, z, r, x + dx, y + dy, z, r)
            x += dx
            y += dy

    def circle(self, size:int = 5):
        self.bot.circle(size)

    def pose(self):
        return self.bot.pose()

    def move_to(self, x, y, z, r, wait=True):
        self.bot.move_to(x, y, z, r, wait)

    def move_to_relative(self, x, y, z, r, wait=True):
        self.bot.move_to_relative( x, y, z, r, wait)

    def home(self):
        self.bot.home()

    def close(self):
        self.bot.close()

    def clear_alarms(self):
        self.bot.clear_alarms()

if __name__ == "__main__":
    digibot = Digibot(verbose=False)

    # print('drawing stave')
    # digibot.draw_stave()

    (x, y, z, r, j1, j2, j3, j4) = digibot.pose()
    print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

    digibot.squiggle([(5, 5, 5)])

    digibot.circle(20)


    #
    # print('test wiggle')
    # digibot.move_to(x + 20, y, z, r, wait=True)
    # # device.wait(1000)
    # digibot.move_to(x, y, z, r, wait=True)
    #
    # # start operating vars
    # duration_of_piece = 60  # seconds
    # running = True
    # old_value = 0
    # start_time = time()
    # end_time = start_time + duration_of_piece
    #
    #
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
    #
    #
    # while time() < end_time:
    #     print('move y')
    #     move_y()

    digibot.close()