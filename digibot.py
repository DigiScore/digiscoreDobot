import sys
import os
import math
import struct
from time import time, sleep
from serial.tools import list_ports
from pydobot import Dobot
from pydobot.enums import PTPMode
from pydobot.message import Message
from pydobot.enums.ControlValues import ControlValues
from pydobot.enums.CommunicationProtocolIDs import CommunicationProtocolIDs


class Digibot(Dobot):
    """Controls movement and shapes drawn by Dobot.
    Inherets all the functions of Pydobot, and chances a few"""

    def __init__(self, port, verbose: bool = False):
        super().__init__(port, verbose)

        # set global path
        sys.path.insert(0, os.path.abspath('.'))

        # make a shared list/ dict
        self.ready_position = [250, -175, 20, 0]
        self.draw_position = [250, -175, 0, 0]
        self.end_position = (250, 175, 20, 0)

        print('locating home')
        self.home()
        input('remove pen, then press enter')

    def draw_stave(self, staves: int = 1):
        """Draws a  line across the middle of an A3 paper, symbolising a stave.
        Has optional function to draw multiple staves.
        Starts at right hand edge centre, and moves directly left.
        Args:
            staves: number of lines to draw. Default = 1"""

        stave_gap = 2
        x = 250 - ((staves * stave_gap) / 2)
        y_start = 175
        y_end = -175
        z = 0
        r = 0

        # goto start position for line draw, without pen
        self.move_to(x, y_start, z, r)
        input('insert pen, then press enter')

        if staves >= 1:
            # draw a line/ stave
            for stave in range(staves):
                print(f'drawing stave {stave + 1} out of {staves}')
                self.move_to(x, y_end, z, r)

                if staves > 1:
                    # reset to RH and draw the rest
                    x += stave_gap

                    if (stave + 1) < staves:
                        self.jump_to(x, y_start, z, r)
        else:
            self.jump_to(x, y_end, z, r)

    def squiggle(self, arc_list: list):
        """accepts a list of tuples that define a sequence of
        x, y deltas to create a sequence of arcs that define a squiggle.
        list (circumference point, end point x, end point y):
            circumference point: size of arc in pixels across x axis
            end point x, end point y: distance from last/ previous position
             """
        [x, y, z, r] = self.pose()[0:4]
        for arc in arc_list:
            circumference, dx, dy = arc[0], arc[1], arc[2]
            self.arc(x + circumference, y, z, r, x + dx, y + dy, z, r)
            x += dx
            y += dy
            sleep(0.2)

    def arc(self, x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait=False):
        """Draws an arc defined by a) circumference of arc (x, y, z, r),
        with b) a finishing coordinates (cirx, ciry, cirz, cirr.
        """
        msg = Message()
        msg.id = 101
        msg.ctrl = 0x03
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.extend(bytearray(struct.pack('f', r)))
        msg.params.extend(bytearray(struct.pack('f', cir_x)))
        msg.params.extend(bytearray(struct.pack('f', cir_y)))
        msg.params.extend(bytearray(struct.pack('f', cir_z)))
        msg.params.extend(bytearray(struct.pack('f', cir_r)))
        return self._send_command(msg, wait)

    def follow_path(self, path):
        for point in path:
            queue_index = self.move_to(point[0], point[1], point[2], 0)

    def continuous_trajectory(self, x, y, z, velocity = 50, wait = True):
        msg = Message()
        msg.id = 91
        msg.ctrl = 0x03
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.extend(bytearray(struct.pack('f', velocity)))

        return self._send_command(msg, wait)

    # todo - continuous trajectory - test circle
    def go_position_ready(self):
        """moves directly to pre-defined position 'Ready Position'"""
        x, y, z, r = self.ready_position[:4]
        self.move_to(x, y, z, r, wait=True)

    def go_position_draw(self):
        """moves directly to pre-defined position 'Ready Position'"""
        x, y, z, r = self.draw_position[:4]
        self.move_to(x, y, z, r, wait=True)

    def go_position_end(self):
        """moves directly to pre-defined position 'end position'"""
        x, y, z, r = self.end_position[:4]
        self.move_to(x, y, z, r, wait=True)

    def jump_to(self, x, y, z, r, wait=True):
        """Lifts pen up, and moves directly to defined coordinates (x, y, z, r)"""
        self._set_ptp_cmd(x, y, z, r, mode=PTPMode.JUMP_XYZ, wait=wait)

    def move_to_relative(self, x, y, z, r, wait=True):
        """moves to new position defined in relatives coordinates to current position.
        Delta/ relative movement is x, y, z, r from current position"""
        self._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ_INC, wait=wait)

    def joint_move_to(self, j1, j2, j3, j4, wait=True):
        """moves specific joints direct to new angles."""
        self.joint_move_to(j1, j2, j3, j4, wait)

    def home(self):
        """Go directly to the home position 0, 0, 0, 0"""
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_HOME_CMD
        msg.ctrl = ControlValues.THREE
        return self._send_command(msg, wait=True)

    def clear_alarms(self) -> None:
        """clear the alarms log and LED"""
        msg = Message()
        msg.id = 20 # this should be 21, but that doesnt work!!
        msg.ctrl = 0x01
        self._send_command(msg)  # empty response

    def dot(self):
        """draws a small dot at current position"""
        self.note_head(0.1)

    def note_head(self, size: float = 5, steps: int = 4):
        """draws a circle at the current position.
        Default is 5 pixels diameter.
        Args:
            size: radius in pixels
            drawing: True = pen on paper
            wait: True = wait till sequence finished"""
        center = self.pose()
        # print('Center:', center)
        # self.bot.interface.set_continous_trajectory_params(200, 200, 200)

        # Draw circle
        path = []
        steps = steps
        scale = size
        for i in range(steps + 1):
            x = math.cos(((math.pi * 2) / steps) * i)
            y = math.sin(((math.pi * 2) / steps) * i)
            path.append([center[0] + x * scale, center[1] + y * scale, center[2]])
        self.follow_path(path)
        self.move_to(center[0], center[1], center[2], center[3])


if __name__ == "__main__":
    # # find available ports and locate Dobot (-1)
    available_ports = list_ports.comports()
    print(f'available ports: {[x.device for x in available_ports]}')
    port = available_ports[-1].device
    digibot = Digibot(port=port, verbose=False)

    # print('drawing stave')
    # digibot.draw_stave()

    (x, y, z, r, j1, j2, j3, j4) = digibot.pose()
    print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')


    # digibot.arc(x + 50, y, z, r, x + 50, y + 50, z, r)

    # digibot.squiggle([(5, 5, 5)])
    #
    digibot.dot()
    #
    # digibot.close()
