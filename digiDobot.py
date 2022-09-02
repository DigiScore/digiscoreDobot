"""Top level class for digi score commands.
Uses gustafsson's code as low-level interface"""

import sys
import os
import math

from serial.tools import list_ports
from gustafsson.lib.interface import Interface
from gustafsson.lib.dobot import Dobot


class Digidobot:

    def __init__(self):
        # set global path
        sys.path.insert(0, os.path.abspath('.'))

        # find available ports and locate Dobot (-1)
        available_ports = list_ports.comports()
        print(f'available ports: {[x.device for x in available_ports]}')
        port = available_ports[-1].device

        # initiate dobot and connect
        self.bot = Dobot(port)
        self.interface = Interface(port)
        print('Bot status:', 'connected' if self.bot.connected() else 'not connected')

        print('locating home')
        self.ready_position = self.bot.home()

        print('Unlock the arm and place it on the middle of the paper')
        input("Press enter to continue...")

        center = self.bot.get_pose()
        print('Center:', center)

    def move_to(self):
        pass

    def slide_to(self):
        pass

    def squiggle(self):
        pass

    def line(self):
        pass

    def home(self):
        self.bot.home()

    def circle(self, size: int = 3):
        """draws a circle at the current position.
        Default is 3 pixels diameter.
        Args:
            size: diameter in pixels"""
        center = self.interface.get_pose()
        # print('Center:', center)
        self.bot.interface.set_continous_trajectory_params(200, 200, 200)

        # Draw circle
        path = []
        steps = 24
        scale = size
        for i in range(steps + 2):
            x = math.cos(((math.pi * 2) / steps) * i)
            y = math.sin(((math.pi * 2) / steps) * i)

            path.append([center[0] + x * scale, center[1] + y * scale, center[2]])
        self.bot.follow_path(path)