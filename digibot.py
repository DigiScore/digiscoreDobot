import sys
import os
import math
import struct
from random import randrange, random, getrandbits
from time import time, sleep
from serial.tools import list_ports
from time import time
from pydobot import Dobot
from pydobot.enums import PTPMode
from pydobot.message import Message
from pydobot.enums.ControlValues import ControlValues
from pydobot.enums.CommunicationProtocolIDs import CommunicationProtocolIDs


class Digibot(Dobot):
    """Controls movement and shapes drawn by Dobot"""

    def __init__(self, port, verbose: bool = False):
        super().__init__(port, verbose)

        # set global path
        sys.path.insert(0, os.path.abspath('.'))

        # # find available ports and locate Dobot (-1)
        # available_ports = list_ports.comports()
        # print(f'available ports: {[x.device for x in available_ports]}')
        # port = available_ports[-1].device

        # initiate dobot and connect        self.bot = pydobot.Dobot(port=port, verbose=verbose)


        # make a shared list/ dict
        self.draw_list = []
        self.ready_position = [250, -175, 20, 0]
        self.end_position = (250, 175, 20, 0)

        print('locating home')
        self.home()
        input('remove pen, then press enter')

    def draw_stave(self, staves: int = 1):
        """Draws a  line across the middle of an A3 paper, symbolising a stave.
        Has optional function to draw multiple staves.
        Args:
            staves: number of lines to draw. Default = 1"""
        stave_start_pos = (250, 175, 0, 0)
        stave_end_pos = (250, -175, 0, 0)

        # goto start position for line draw, without pen
        x1, y1, z1, r1 = stave_start_pos[:4]
        x2, y2, z2, r2 = stave_end_pos[:4]
        self.move_to(x1, y1, z1, r1)

        # draw a line/ stave
        input('Insert pen, then press enter')
        self.move_to(x2, y2, z2, r2)

        # # goto standby position
        # self.bot.move_to_relative(0, 0, 10, 0)
        # input('waiting')

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
            self.arc(x + circumference, y, z, r, x + dx, y + dy, z, r)
            x += dx
            y += dy
            sleep(0.2)

    def arc(self, x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait=False):
        # return self._extract_cmd_index(self._set_arc_cmd(x, y, z, r, cir_x, cir_y, cir_z, cir_r))
    #     return self._set_arc_command(x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait)
    #
    # def arc(self, x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait):
    #     self.go_arc(x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait)
    #
    # def _set_arc_command(self, x, y, z, r, x1, y1, z1, r1, wait=False):
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

    # def circle(self, size:int = 5):
    #     self.circle(size)

    # def speed(self, velocity=200, acceleration=200):
    #     self.bot._set_ptp_coordinate_params(velocity=velocity,
    #                                         acceleration=acceleration)

    def _follow_path(self, path):
        for point in path:
            queue_index = self.move_to(point[0], point[1], point[2], 50)

    def go_position_ready(self):
        x, y, z, r = self.ready_position[:4]
        self.move_to(x, y, z, r, wait=True)

    def go_position_end(self):
        x, y, z, r = self.end_position[:4]
        self.move_to(x, y, z, r, wait=True)

    # @staticmethod
    # def _extract_cmd_index(response):
    #     return struct.unpack_from('I', response.params, 0)[0]

    # def wait_for_cmd(self, cmd_id):
    #     current_cmd_id = self._get_queued_cmd_current_index()
    #     while cmd_id > current_cmd_id:
    #         self.logger.debug("Current-ID", current_cmd_id)
    #         self.logger.debug("Waiting for", cmd_id)

    # def pose(self):
    #     return self.bot.pose()

    # def move_to(self, x, y, z, r, wait=True):
    #     self.move_to(x, y, z, r, wait)

    def jump_to(self, x, y, z, r, wait=True):
        self._set_ptp_cmd(x, y, z, r, mode=PTPMode.JUMP_XYZ, wait=wait)

    def move_to_relative(self, x, y, z, r, wait=True):
        self._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ_INC, wait=wait)

    def joint_move_to(self, j1, j2, j3, j4, wait=True):
        self.joint_move_to(j1, j2, j3, j4, wait)

    def home(self):
        # self._set_home_cmd()
        # """
        #         Home command
        #     """
        #
        # def _set_home_cmd(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_HOME_CMD
        msg.ctrl = ControlValues.THREE
        return self._send_command(msg, wait=True)

    # def close(self):
    #     self.close()

    def clear_alarms(self) -> None:
        msg = Message()
        msg.id = 20
        msg.ctrl = 0x01
        self._send_command(msg)  # empty response

    # def home(self):
    #     self._set_home_cmd()

    # def move_to_relative(self, x, y, z, r, wait=False):
    #     self._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ_INC, wait=wait)

    def dot(self):
        self.circle(0.1)

    def circle(self, size: float = 5):
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
        steps = 24
        scale = size
        for i in range(steps + 2):
            x = math.cos(((math.pi * 2) / steps) * i)
            y = math.sin(((math.pi * 2) / steps) * i)
            # if i == 0 and drawing:
            path.append([center[0] + x * scale, center[1] + y * scale, center[2], center[3]])
            # else:
                # path.append([center[0] + x * scale, center[1] + y * scale, center[2] - 5])

        self._follow_path(path)

if __name__ == "__main__":
    # # find available ports and locate Dobot (-1)
    available_ports = list_ports.comports()
    print(f'available ports: {[x.device for x in available_ports]}')
    port = available_ports[-1].device
    digibot = Digibot(port=port, verbose=True)

    # print('drawing stave')
    # digibot.draw_stave()

    (x, y, z, r, j1, j2, j3, j4) = digibot.pose()
    print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

    digibot.squiggle([(5, 5, 5)])

    digibot.circle(20)

    digibot.close()
