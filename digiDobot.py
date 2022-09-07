"""Top level class for digi score commands.
Uses gustafsson's code as low-level interface
Oroginal code https://github.com/AlexGustafsson/dobot-python"""

import sys
import os
import math

from serial.tools import list_ports
from dobot_python.lib.dobot import Dobot


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
        self.interface = self.bot.interface
        print('Bot status:', 'connected' if self.bot.connected() else 'not connected')

        # reset any lingering errors
        # todo - this doesnt
        self.reset_errors()

        # drawing or notdrawing y offset
        self.drawing = False
        self.not_drawing_offset = -5

        print('locating home')
        self.ready_position = self.bot.home()

        print('Unlock the arm and place it on the middle of the paper')
        input("Press enter to continue...")

        self.centre_pos = self.interface.get_pose()
        print('Center:', self.centre_pos)
        self.pen_ready(False)

    def move_to(self, new_relative_pos: tuple):
        """move the pen head to a relative position
        from current position"""
        self.bot.move_to_relative(new_relative_pos[0],
                                  new_relative_pos[1],
                                  0,0)

    def slide_to(self):
        pass

    def pen_ready(self, ready_to_draw: bool):
        """moves the drawing pen onto page ready to draw"""
        if ready_to_draw:
            self.bot.move_to_relative(0, 0, -5, 0)
        else:
            self.bot.move_to_relative(0, 0, 5, 0)
            self.reset_errors()

    def squiggle(self, arc_list: list):
        """accepts a list of tuples that define a sequence of
        x, y deltas to create a sequence of arcs that define a squiggle.
        list (circumference point, end point x, end point y):
            circumference point: size of arc in pixels across x axis
            end point x, end point y: distance from last/ previous position
             """
        self.pen_ready(True)
        [x, y, z, r] = self.interface.get_pose()[0:4]
        for arc in arc_list:
            print(arc)
            circumference, dx, dy = arc[0], arc[1], arc[2]
            self.interface.set_arc_command([x + circumference, y, z, r], [x + dx, y + dy, z, r])
            x += dx
            y += dy
        self.pen_ready(False)

    def line(self, new_position_relative: tuple):
        """Draws a straight line to coordinates relative to current position.
        """
        self.pen_ready(True)
        x = new_position_relative[0]
        y = new_position_relative[1]
        self.bot.move_to_relative(x, y, 0, 0)
        self.pen_ready(False)

    def circle_line(self, circle_size: float, line_end_point_relative: tuple):
        """draws a circle and a line combination.
        Circle size is diameter.
        Line direction is relative to start position of circle"""
        self.circle(circle_size)
        self.line(line_end_point_relative)

    def circle_arc(self, circle_size: float, arc_list: list):
        """draws a circle and an arc combination.
        Circle size is radius.
        Line direction is relative to start position of circle"""
        self.circle(circle_size)
        self.squiggle(arc_list)

    def home(self):
        """ go to default home position"""
        self.bot.home()

    def centre(self):
        """ go to initial middle of paper position"""
        self.drawing = False
        x, y, z, r = self.centre_pos[4], \
                     self.centre_pos[5], \
                     self.centre_pos[6], \
                     self.centre_pos[7]
        print(x, y, z, r)
        self.bot.slide_to(x, y, z, r)

    def dot(self):
        self.circle(0.1)

    def circle(self, size: float = 2):
        """draws a circle at the current position.
        Default is 3 pixels diameter.
        Args:
            size: radius in pixels"""
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
            if i == 0:
                path.append([center[0] + x * scale, center[1] + y * scale, center[2]])
            else:
                path.append([center[0] + x * scale, center[1] + y * scale, center[2] - 5])
        self.bot.follow_path(path)
        self.pen_ready(False)

    # todo - this doesnt work LOW
    def stave(self):
        centre = self.bot.get_pose()
        [x, y, z, r] = centre[0:4]
        for line in range(5):
            self.pen_ready(True)
            self.bot.move_to_relative(-10, 0, 0, 0)
            self.pen_ready(False)
            y += 2
            self.bot.move_to(x, y, z, r)

    # todo - this is tricky. Needed?
    def letters(self, letter: str):
        """draws a musical letter such as m, p, f.
        anchor point is far left"""
        self.pen_ready(True)
        [x, y, z, r] = self.bot.get_pose()[0:4]
        if letter == "m":
            self.bot.move_to_relative(-2, 0, 0, 0)
            self.interface.set_arc_command([x + 1, y, z, r], [x + 1, y + 1, z, r])
            self.bot.move_to_relative(2, 0, 0, 0)
            self.bot.move_to_relative(-2, 0, 0, 0)
            [x, y, z, r] = self.bot.get_pose()[0:4]
            self.interface.set_arc_command([x + 1, y, z, r], [x + 1, y + 1, z, r])
        elif letter == "p":
            pass
        elif letter == "f":
            pass
        self.pen_ready(False)

    def reset_errors(self):
        # self.interface.get_alarms_state()
        self.interface.clear_alarms_state()

    def close(self):
        self.interface.close()
