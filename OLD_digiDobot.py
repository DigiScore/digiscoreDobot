import serial
import struct
import time
import threading
import warnings
import math

from .message import Message
from .enums import PTPMode
from .enums.CommunicationProtocolIDs import CommunicationProtocolIDs
from .enums.ControlValues import ControlValues


class Dobot:

    def __init__(self, port, verbose=False):
        threading.Thread.__init__(self)

        self._on = True
        self.verbose = verbose
        self.ready = True  # flag to stop over-Qing

        self.lock = threading.Lock()
        self.ser = serial.Serial(port,
                                 baudrate=115200,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS)
        is_open = self.ser.isOpen()
        if self.verbose:
            print('pydobot: %s open' % self.ser.name if is_open else 'failed to open serial port')

        self._set_queued_cmd_start_exec()
        self._set_queued_cmd_clear()
        self._set_ptp_joint_params(200, 200, 200, 200, 200, 200, 200, 200)
        self._set_ptp_coordinate_params(velocity=200, acceleration=200)
        self._set_ptp_jump_params(10, 200)
        self._set_ptp_common_params(velocity=100, acceleration=100)
        self._get_pose()

    """
        Gets the current command index
    """

    def _get_queued_cmd_current_index(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.GET_QUEUED_CMD_CURRENT_INDEX
        response = self._send_command(msg)
        idx = struct.unpack_from('L', response.params, 0)[0]
        return idx

    """
        Gets the real-time pose of the Dobot
    """

    def _get_pose(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.GET_POSE
        response = self._send_command(msg)
        self.x = struct.unpack_from('f', response.params, 0)[0]
        self.y = struct.unpack_from('f', response.params, 4)[0]
        self.z = struct.unpack_from('f', response.params, 8)[0]
        self.r = struct.unpack_from('f', response.params, 12)[0]
        self.j1 = struct.unpack_from('f', response.params, 16)[0]
        self.j2 = struct.unpack_from('f', response.params, 20)[0]
        self.j3 = struct.unpack_from('f', response.params, 24)[0]
        self.j4 = struct.unpack_from('f', response.params, 28)[0]

        if self.verbose:
            print("pydobot: x:%03.1f \
                            y:%03.1f \
                            z:%03.1f \
                            r:%03.1f \
                            j1:%03.1f \
                            j2:%03.1f \
                            j3:%03.1f \
                            j4:%03.1f" %
                  (self.x, self.y, self.z, self.r, self.j1, self.j2, self.j3, self.j4))
        return response

    def _read_message(self, retries=5):
        for x in range(retries):
            time.sleep(0.1)
            b = self.ser.read_all()
            if len(b) > 0:
                msg = Message(b)
                if self.verbose:
                    print('pydobot: <<', msg)
                return msg
        return
        # time.sleep(0.1)
        # b = self.ser.read_all()
        # if len(b) > 0:
        #     msg = Message(b)
        #     if self.verbose:
        #         print('pydobot: <<', msg)
        #     return msg
        # return

    def _send_command(self, msg, wait=False):
        self.ready = False
        self.lock.acquire()
        self._send_message(msg)
        response = self._read_message()
        self.lock.release()

        if not wait:
            return response

        expected_idx = struct.unpack_from('L', response.params, 0)[0]
        if self.verbose:
            print('pydobot: waiting for command', expected_idx)

        while True:
            current_idx = self._get_queued_cmd_current_index()

            if current_idx != expected_idx:
                time.sleep(0.1)
                continue

            if self.verbose:
                print('pydobot: command %d executed' % current_idx)
            self.ready = True
            break

        return response

    def _send_message(self, msg):
        time.sleep(0.1)
        if self.verbose:
            print('pydobot: >>', msg)
        self.ser.write(msg.bytes())

    """
        Executes the CP Command
    """

    def _set_cp_cmd(self, x, y, z):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_CP_CMD
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray(bytes([0x01]))
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.append(0x00)
        return self._send_command(msg)

    """
        Sets the status of the gripper
    """

    def _set_end_effector_gripper(self, enable=False):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_END_EFFECTOR_GRIPPER
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray([0x01]))
        if enable is True:
            msg.params.extend(bytearray([0x01]))
        else:
            msg.params.extend(bytearray([0x00]))
        return self._send_command(msg)

    """
        Sets the status of the suction cup
    """

    def _set_end_effector_suction_cup(self, enable=False):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_END_EFFECTOR_SUCTION_CUP
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray([0x01]))
        if enable is True:
            msg.params.extend(bytearray([0x01]))
        else:
            msg.params.extend(bytearray([0x00]))
        return self._send_command(msg)

    """
        Sets the velocity ratio and the acceleration ratio in PTP mode
    """

    def _set_ptp_joint_params(self, v_x, v_y, v_z, v_r, a_x, a_y, a_z, a_r):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_PTP_JOINT_PARAMS
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', v_x)))
        msg.params.extend(bytearray(struct.pack('f', v_y)))
        msg.params.extend(bytearray(struct.pack('f', v_z)))
        msg.params.extend(bytearray(struct.pack('f', v_r)))
        msg.params.extend(bytearray(struct.pack('f', a_x)))
        msg.params.extend(bytearray(struct.pack('f', a_y)))
        msg.params.extend(bytearray(struct.pack('f', a_z)))
        msg.params.extend(bytearray(struct.pack('f', a_r)))
        return self._send_command(msg)

    """
        Sets the velocity and acceleration of the Cartesian coordinate axes in PTP mode
    """

    def _set_ptp_coordinate_params(self, velocity, acceleration):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_PTP_COORDINATE_PARAMS
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', velocity)))
        msg.params.extend(bytearray(struct.pack('f', velocity)))
        msg.params.extend(bytearray(struct.pack('f', acceleration)))
        msg.params.extend(bytearray(struct.pack('f', acceleration)))
        return self._send_command(msg)

    """
       Sets the lifting height and the maximum lifting height in JUMP mode
    """

    def _set_ptp_jump_params(self, jump, limit):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_PTP_JUMP_PARAMS
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', jump)))
        msg.params.extend(bytearray(struct.pack('f', limit)))
        return self._send_command(msg)

    """
        Sets the velocity ratio, acceleration ratio in PTP mode
    """

    def _set_ptp_common_params(self, velocity, acceleration):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_PTP_COMMON_PARAMS
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', velocity)))
        msg.params.extend(bytearray(struct.pack('f', acceleration)))
        return self._send_command(msg)

    """
        Executes PTP command
    """

    def _set_ptp_cmd(self, x, y, z, r, mode, wait):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_PTP_CMD
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray([mode.value]))
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.extend(bytearray(struct.pack('f', r)))
        return self._send_command(msg, wait)

    # """
    #     Home command
    # """
    # def _set_home_cmd(self):
    #     msg = Message()
    #     msg.id = CommunicationProtocolIDs.SET_HOME_CMD
    #     msg.ctrl = ControlValues.THREE
    #     return self._send_command(msg, wait=True)

    """
        Clears command queue
    """

    def _set_queued_cmd_clear(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_QUEUED_CMD_CLEAR
        msg.ctrl = ControlValues.ONE
        return self._send_command(msg)

    """
        Start command
    """

    def _set_queued_cmd_start_exec(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_QUEUED_CMD_START_EXEC
        msg.ctrl = ControlValues.ONE
        return self._send_command(msg)

    """
        Wait command
    """

    def _set_wait_cmd(self, ms):
        msg = Message()
        msg.id = 110
        msg.ctrl = 0x03
        msg.params = bytearray(struct.pack('I', ms))
        return self._send_command(msg)

    """
        Stop command
    """

    def _set_queued_cmd_stop_exec(self):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_QUEUED_CMD_STOP_EXEC
        msg.ctrl = ControlValues.ONE
        return self._send_command(msg)

    def _get_eio_level(self, address):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_EIO
        msg.ctrl = ControlValues.ZERO
        msg.params = bytearray([])
        msg.params.extend(bytearray([address]))
        return self._send_command(msg)

    def _set_eio_level(self, address, level):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_GET_EIO
        msg.ctrl = ControlValues.ONE
        msg.params = bytearray([])
        msg.params.extend(bytearray([address]))
        msg.params.extend(bytearray([level]))
        return self._send_command(msg)

    """
          Sets arc command
      """

    def _set_arc_command(self, x, y, z, r, x1, y1, z1, r1, wait=False):
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_ARC_COMMAND
        msg.ctrl = ControlValues.THREE
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.extend(bytearray(struct.pack('f', r)))
        msg.params.extend(bytearray(struct.pack('f', x1)))
        msg.params.extend(bytearray(struct.pack('f', y1)))
        msg.params.extend(bytearray(struct.pack('f', z1)))
        msg.params.extend(bytearray(struct.pack('f', r1)))
        return self._send_command(msg, wait)

    # def _set_arc_cmd(self, x, y, z, r, cir_x, cir_y, cir_z, cir_r):
    #     msg = Message()
    #     msg.id = 101
    #     msg.ctrl = 0x03
    #     msg.params = bytearray([])
    #     msg.params.extend(bytearray(struct.pack('f', cir_x)))
    #     msg.params.extend(bytearray(struct.pack('f', cir_y)))
    #     msg.params.extend(bytearray(struct.pack('f', cir_z)))
    #     msg.params.extend(bytearray(struct.pack('f', cir_r)))
    #     msg.params.extend(bytearray(struct.pack('f', x)))
    #     msg.params.extend(bytearray(struct.pack('f', y)))
    #     msg.params.extend(bytearray(struct.pack('f', z)))
    #     msg.params.extend(bytearray(struct.pack('f', r)))
    #     return self._send_command(msg)

    # def _follow_path(self, path):
    #     for point in path:
    #         queue_index = self.move_to(point[0], point[1], point[2], 50)

    @staticmethod
    def _extract_cmd_index(response):
        return struct.unpack_from('I', response.params, 0)[0]

    def wait_for_cmd(self, cmd_id):
        current_cmd_id = self._get_queued_cmd_current_index()
        while cmd_id > current_cmd_id:
            self.logger.debug("Current-ID", current_cmd_id)
            self.logger.debug("Waiting for", cmd_id)

    # def clear_alarms(self) -> None:
    #     msg = Message()
    #     msg.id = 20
    #     msg.ctrl = 0x01
    #     self._send_command(msg)  # empty response

    def get_eio(self, addr):
        return self._get_eio_level(addr)

    def set_eio(self, addr, val):
        return self._set_eio_level(addr, val)

    def close(self):
        self._on = False
        self.lock.acquire()
        self.ser.close()
        if self.verbose:
            print('pydobot: %s closed' % self.ser.name)
        self.lock.release()

    def go(self, x, y, z, r=0.):
        warnings.warn('go() is deprecated, use move_to() instead')
        self.move_to(x, y, z, r)

    def move_to(self, x, y, z, r, wait=False):
        self._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVL_XYZ, wait=wait)

    # def joint_move_to(self, j1, j2, j3, j4, wait=False):
    #     self._set_ptp_cmd(j1, j2, j3, j4, mode=PTPMode.JUMP_ANGLE, wait=wait)

    # def jump_to(self, x, y, z, r, wait=False):
    #     self._set_ptp_cmd(x, y, z, r, mode=PTPMode.JUMP_XYZ, wait=wait)

    def suck(self, enable):
        self._set_end_effector_suction_cup(enable)

    def grip(self, enable):
        self._set_end_effector_gripper(enable)

    def speed(self, velocity=100., acceleration=100.):
        self._set_ptp_common_params(velocity, acceleration)
        self._set_ptp_coordinate_params(velocity, acceleration)

    def wait(self, ms):
        self._set_wait_cmd(ms)

    #
    # def go_arc(self, x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait=False):
    #     # return self._extract_cmd_index(self._set_arc_cmd(x, y, z, r, cir_x, cir_y, cir_z, cir_r))
    #     return self._set_arc_command(x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait)

    def pose(self):
        response = self._get_pose()
        x = struct.unpack_from('f', response.params, 0)[0]
        y = struct.unpack_from('f', response.params, 4)[0]
        z = struct.unpack_from('f', response.params, 8)[0]
        r = struct.unpack_from('f', response.params, 12)[0]
        j1 = struct.unpack_from('f', response.params, 16)[0]
        j2 = struct.unpack_from('f', response.params, 20)[0]
        j3 = struct.unpack_from('f', response.params, 24)[0]
        j4 = struct.unpack_from('f', response.params, 28)[0]
        return x, y, z, r, j1, j2, j3, j4

    # def home(self):
    #     self._set_home_cmd()
    #
    # def move_to_relative(self, x, y, z, r, wait=False):
    #     self._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ_INC, wait=wait)
    #
    # def dot(self):
    #     self.circle(0.1)
    #
    # def circle(self, size: float = 5):
    #     """draws a circle at the current position.
    #     Default is 5 pixels diameter.
    #     Args:
    #         size: radius in pixels
    #         drawing: True = pen on paper
    #         wait: True = wait till sequence finished"""
    #     center = self.pose()
    #     # print('Center:', center)
    #     # self.bot.interface.set_continous_trajectory_params(200, 200, 200)
    #
    #     # Draw circle
    #     path = []
    #     steps = 24
    #     scale = size
    #     for i in range(steps + 2):
    #         x = math.cos(((math.pi * 2) / steps) * i)
    #         y = math.sin(((math.pi * 2) / steps) * i)
    #         # if i == 0 and drawing:
    #         path.append([center[0] + x * scale, center[1] + y * scale, center[2], center[3]])
    #         # else:
    #             # path.append([center[0] + x * scale, center[1] + y * scale, center[2] - 5])
    #
    #     self._follow_path(path)

    # def speed(self, velocity=100., acceleration=100.):
    #     self.wait_for_cmd(self._extract_cmd_index(self._set_ptp_common_params(velocity, acceleration)))
    #     self.wait_for_cmd(self._extract_cmd_index(self._set_ptp_coordinate_params(velocity, acceleration)))





"""Top level class for digi score commands.
Uses gustafsson's code as low-level interface
Oroginal code https://github.com/AlexGustafsson/dobot-python"""

import sys
import os
import math
from random import randrange, random, getrandbits
from time import time, sleep

from serial.tools import list_ports
from dobot_python.lib.dobot import Dobot

alarm_dict = {
            0x00: 'reset occurred',
            0x01: 'undefined instruction',
            0x02: 'file system error',
            0x03: 'communications error between MCU and FPGA',
            0x04: 'angle sensor error',

            0x10: 'plan: pose is abnormal',
            0x11: 'plan: pose is out of workspace',
            0x12: 'plan: joint limit',
            0x13: 'plan: repetitive points',
            0x14: 'plan: arc input parameter',
            0x15: 'plan: jump parameter',

            0x20: 'motion: kinematic singularity',
            0x21: 'motion: out of workspace',
            0x22: 'motion: inverse limit',

            0x30: 'axis 1 overspeed',
            0x31: 'axis 2 overspeed',
            0x32: 'axis 3 overspeed',
            0x33: 'axis 4 overspeed',

            0x40: 'axis 1 positive limit',
            0x41: 'axis 1 negative limit',
            0x42: 'axis 2 positive limit',
            0x43: 'axis 2 negative limit',
            0x44: 'axis 3 positive limit',
            0x45: 'axis 3 negative limit',
            0x46: 'axis 4 positive limit',
            0x47: 'axis 4 negative limit',

            0x50: 'axis 1 lost steps',
            0x51: 'axis 2 lost steps',
            0x52: 'axis 3 lost steps',
            0x53: 'axis 4 lost steps',


            0x60: 'OTHER_AXIS1_DRV_ALARM',
            0x61: 'OTHER_AXIS1_OVERFLOW',
            0x62: 'OTHER_AXIS1_FOLLOW',
            0x63: 'OTHER_AXIS2_DRV_ALARM',
            0x64: 'OTHER_AXIS2_OVERFLOW',
            0x65: 'OTHER_AXIS2_FOLLOW',
            0x66: 'OTHER_AXIS3_DRV_ALARM',
            0x67: 'OTHER_AXIS3_OVERFLOW',
            0x68: 'OTHER_AXIS3_FOLLOW',
            0x69: 'OTHER_AXIS4_DRV_ALARM',
            0x6A: 'OTHER_AXIS4_OVERFLOW',
            0x6B: 'OTHER_AXIS4_FOLLOW',

            0x70: 'MOTOR_REAR_ENCODER',
            0x71: 'MOTOR_REAR_TEMPERATURE_HIGH',
            0x72: 'MOTOR_REAR_TEMPERATURE_LOW',
            0x73: 'MOTOR_REAR_LOCK_CURRENT',
            0x74: 'MOTOR_REAR_BUSV_HIGH',
            0x75: 'MOTOR_REAR_BUSV_LOW',
            0x76: 'MOTOR_REAR_OVERHEAT',
            0x77: 'MOTOR_REAR_RUNAWAY',
            0x78: 'MOTOR_REAR_BATTERY_LOW',
            0x79: 'MOTOR_REAR_PHASE_SHORT',
            0x7A: 'MOTOR_REAR_PHASE_WRONG',
            0x7B: 'MOTOR_REAR_LOST_SPEED',
            0x7C: 'MOTOR_REAR_NOT_STANDARDIZE',
            0x7D: 'ENCODER_REAR_NOT_STANDARDIZE',
            0x7E: 'MOTOR_REAR_CAN_BROKE',

            0x80: 'MOTOR_FRONT_ENCODER',
            0x81: 'MOTOR_FRONT_TEMPERATURE_HIGH',
            0x82: 'MOTOR_FRONT_TEMPERATURE_LOW',
            0x83: 'MOTOR_FRONT_LOCK_CURRENT',
            0x84: 'MOTOR_FRONT_BUSV_HIGH',
            0x85: 'MOTOR_FRONT_BUSV_LOW',
            0x86: 'MOTOR_FRONT_OVERHEAT',
            0x87: 'MOTOR_FRONT_RUNAWAY',
            0x88: 'MOTOR_FRONT_BATTERY_LOW',
            0x89: 'MOTOR_FRONT_PHASE_SHORT',
            0x8A: 'MOTOR_FRONT_PHASE_WRONG',
            0x8B: 'MOTOR_FRONT_LOST_SPEED',
            0x8C: 'MOTOR_FRONT_NOT_STANDARDIZE',
            0x8D: 'ENCODER_FRONT_NOT_STANDARDIZE',
            0x8E: 'MOTOR_FRONT_CAN_BROKE',

            0x90: 'MOTOR_Z_ENCODER',
            0x91: 'MOTOR_Z_TEMPERATURE_HIGH',
            0x92: 'MOTOR_Z_TEMPERATURE_LOW',
            0x93: 'MOTOR_Z_LOCK_CURRENT',
            0x94: 'MOTOR_Z_BUSV_HIGH',
            0x95: 'MOTOR_Z_BUSV_LOW',
            0x96: 'MOTOR_Z_OVERHEAT',
            0x97: 'MOTOR_Z_RUNAWAY',
            0x98: 'MOTOR_Z_BATTERY_LOW',
            0x99: 'MOTOR_Z_PHASE_SHORT',
            0x9A: 'MOTOR_Z_PHASE_WRONG',
            0x9B: 'MOTOR_Z_LOST_SPEED',
            0x9C: 'MOTOR_Z_NOT_STANDARDIZE',
            0x9D: 'ENCODER_Z_NOT_STANDARDIZE',
            0x9E: 'MOTOR_Z_CAN_BROKE',

            0xA0: 'MOTOR_R_ENCODER',
            0xA1: 'MOTOR_R_TEMPERATURE_HIGH',
            0xA2: 'MOTOR_R_TEMPERATURE_LOW',
            0xA3: 'MOTOR_R_LOCK_CURRENT',
            0xA4: 'MOTOR_R_BUSV_HIGH',
            0xA5: 'MOTOR_R_BUSV_LOW',
            0xA6: 'MOTOR_R_OVERHEAT',
            0xA7: 'MOTOR_R_RUNAWAY',
            0xA8: 'MOTOR_R_BATTERY_LOW',
            0xA9: 'MOTOR_R_PHASE_SHORT',
            0xAA: 'MOTOR_R_PHASE_WRONG',
            0xAB: 'MOTOR_R_LOST_SPEED',
            0xAC: 'MOTOR_R_NOT_STANDARDIZE',
            0xAD: 'ENCODER_R_NOT_STANDARDIZE',
            0xAE: 'MOTOR_R_CAN_BROKE',

            0xB0: 'MOTOR_ENDIO_IO',
            0xB1: 'MOTOR_ENDIO_RS485_WRONG',
            0xB2: 'MOTOR_ENDIO_CAN_BROKE'
        }

class Digidobot:
    """Controls movement and shapes drawn by Dobot"""
    def __init__(self, verbose: bool = False):
        # set global path
        sys.path.insert(0, os.path.abspath('.'))

        # find available ports and locate Dobot (-1)
        available_ports = list_ports.comports()
        print(f'available ports: {[x.device for x in available_ports]}')
        port = available_ports[-1].device

        # initiate dobot and connect
        self.bot = Dobot(port, verbose)
        self.interface = self.bot.interface
        print('Bot status:', 'connected' if self.bot.connected() else 'not connected')

        # setup a client incoming command list
        self.incoming_command_list = []

        # drawing or notdrawing y offset
        self.drawing = False
        self.not_drawing_offset = -5

        # safe place
        self.safe_place = (300, 0, 10, 0)

        print('locating home')
        # self.ready_position = \
        self.bot.home()
        self.reset_errors()

        print('remove pen')
        self.draw_stave()

        # print('Unlock the arm and place it on the middle of the paper')
        # input("Press enter to continue...")
        #
        # # Remember starting position for pen lift
        # self.centre_pos = self.interface.get_pose()
        # self.print_position(self.centre_pos)
        # self.pen_ready(False)

    def print_position(self, position):
        print(f'Centre position (x, y, z, r): {position[0:4]}')

    def move_to_rel_xyz(self, new_relative_pos: tuple, wait: bool = True):
        """move the pen head to a relative position x, y, z
        from current position"""
        self.bot.move_to_relative(new_relative_pos[0],
                                  new_relative_pos[1],
                                  new_relative_pos[2],
                                  0,
                                  wait=wait)

    def slide_to_rel_xyz(self, new_relative_pos: tuple, wait: bool = True):
        """Slide to a relative coordinate x, y, z
        shortest possible path"""
        self.bot.slide_to_relative(new_relative_pos[0],
                                   new_relative_pos[1],
                                   new_relative_pos[2],
                                   0,
                                   wait=wait)

    def move_to_xyzr(self, new_pos: tuple, wait: bool = True):
        """move the pen head to a cartesian position x, y, z, r
                from current position"""
        x, y, z, r = new_pos[0], \
                     new_pos[1], \
                     new_pos[2], \
                     new_pos[3]
        self.bot.move_to(x, y, z, r)

    def slide_to_xyzr(self, new_pos: tuple, wait: bool = True):
        """move the pen head to a cartesian position x, y, z, r
                from current position quickly. Used for rapid movement"""
        x, y, z, r = new_pos[0], \
                     new_pos[1], \
                     new_pos[2], \
                     new_pos[3]
        self.bot.slide_to(x, y, z, r)

    # todo - all these functions can be with or without pen draw
    # def pen_ready(self, ready_to_draw: bool):
    #     """moves the drawing pen onto page ready to draw"""
    #     current_position = self.interface.get_pose()
    #     # print(f'current position = {current_position}')
    #     x, y, z, r = current_position[:4]
    #     if ready_to_draw:
    #         print(f"Ready to draw x:{x}, y:{y}, z:0")
    #         # self.bot.move_to_relative(0, 0, -5, 0)
    #         self.move_to((x, y, 0, r))
    #     else:
    #         print(f"Ready to move x:{x}, y:{y}, z:+10")
    #         # self.bot.move_to_relative(0, 0, 5, 0)
    #         self.move_to((x, y, 10, r))

        # self.reset_errors()

    def squiggle(self, arc_list: list,
                 drawing: bool = True,
                 queue: bool = True):
        """accepts a list of tuples that define a sequence of
        x, y deltas to create a sequence of arcs that define a squiggle.
        list (circumference point, end point x, end point y):
            circumference point: size of arc in pixels across x axis
            end point x, end point y: distance from last/ previous position
             """
        # if drawing:
        #     self.pen_ready(True)
        [x, y, z, r] = self.interface.get_pose()[0:4]
        for arc in arc_list:
            # print(arc)
            circumference, dx, dy = arc[0], arc[1], arc[2]
            self.interface.set_arc_command([x + circumference, y, z, r], [x + dx, y + dy, z, r], queue=queue)
            x += dx
            y += dy
        # if drawing:
        #     self.pen_ready(False)

    def line(self, new_position_relative: tuple,
             drawing: bool = True,
             wait: bool = True):
        """Draws a straight line to coordinates relative to current position.
        """
        # if drawing:
        #     self.pen_ready(True)
        x = new_position_relative[0]
        y = new_position_relative[1]
        self.bot.move_to_relative(x, y, 0, 0, wait=wait)
        # if drawing:
        #     self.pen_ready(False)

    def circle_line(self, circle_size: float,
                    line_end_point_relative: tuple,
                    drawing: bool = True,
                    wait: bool = True):
        """draws a circle and a line combination.
        Circle size is diameter.
        Line direction is relative to start position of circle"""
        self.circle(circle_size, drawing, wait)
        self.line(line_end_point_relative, drawing, wait)

    def circle_arc(self, circle_size: float,
                   arc_list: list,
                   drawing: bool = True,
                   wait: bool = True):
        """draws a circle and an arc combination.
        Circle size is radius.
        Line direction is relative to start position of circle"""
        self.circle(circle_size, drawing, wait)
        self.squiggle(arc_list, drawing, wait)

    def home(self):
        """ go to default home position"""
        self.bot.home()

    # def centre(self):
    #     """ go to initial middle of paper position"""
    #     self.drawing = False
    #     x, y, z, r = self.centre_pos[4], \
    #                  self.centre_pos[5], \
    #                  self.centre_pos[6], \
    #                  self.centre_pos[7]
    #     print(x, y, z, r)
    #     self.bot.slide_to(x, y, z, r)

    def dot(self, wait: bool = True):
        self.circle(0.1, wait=wait)

    def circle(self, size: float = 5,
               drawing: bool = True,
               wait: bool = False):
        """draws a circle at the current position.
        Default is 3 pixels diameter.
        Args:
            size: radius in pixels
            drawing: True = pen on paper
            wait: True = wait till sequence finished"""
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
            # if i == 0 and drawing:
            path.append([center[0] + x * scale, center[1] + y * scale, center[2]])
            # else:
                # path.append([center[0] + x * scale, center[1] + y * scale, center[2] - 5])

        self.bot.follow_path(path, wait=wait)

        # if drawing:
        #     self.pen_ready(False)

    def reset_errors(self):
        alarms = self.interface.get_alarms_state()
        # print(alarms)
        self.alarms(alarms)

    # todo - multiple staff lines [LOW]
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
        self.slide_to_xyzr((x1, y1, z1, r1))

        # draw a line/ stave
        input('Insert pen, then press enter')
        self.move_to_xyzr((x2, y2, z2, r2))

        # goto standby position
        self.move_to_xyzr((250, -210, 20, 0))

    def alarms(self, alarm_response):
        alarms = []
        for i, x in enumerate(alarm_response):
            for j in range(8):
                if x & (1 << j) > 0:
                    alarms.append(8 * i + j)
        if len(alarms) > 0:
            # self.move_to(self.safe_place[:4])
            for alarm in alarms:
                try:
                    print('ALARM:', alarm_dict[alarm])
                except:
                    print('ALARM: not in list')
        self.interface.clear_alarms_state()
        # self.bot.home()

    def current_position(self):
        """returns current position x, y, z, r as list"""
        position_list = self.interface.get_pose()[0:4]
        return position_list

    def close(self):
        self.interface.close()

if __name__ == "__main__":
    digibot = Digidobot(verbose=False)
    digibot.reset_errors()

    # start operating vars
    duration_of_piece = 60 # seconds
    running = True
    old_value = 0
    start_time = time()
    end_time = start_time + duration_of_piece
    sub_division_of_duration = 420 / duration_of_piece

    def move_y():
        # move y along a bit
        elapsed = int(time() - start_time) + 1
        current_y_delta = elapsed * sub_division_of_duration
        position_list = digibot.current_position()
        digibot.print_position(position_list)
        nowx, nowy, nowz, nowr = position_list[:4]
        print('elapsed time = ', elapsed)
        print(f'old y = {nowy}, move to = {nowy + current_y_delta}')
        if 200 <= nowx <= 300:
            nowx = 250
        digibot.slide_to_xyzr((nowx, nowy + current_y_delta, 0, nowr))

    def rnd(power_of_command):
        # movement + or - (random)
        if getrandbits(1):
            posneg = 1
        else:
            posneg = -1

        # multiplication factor
        if getrandbits(1):
            multiplication_factor = randrange(3, 6) + power_of_command
        else:
            multiplication_factor = 5

        # return (random() + multiplication_factor) * posneg

        result = multiplication_factor * posneg
        print(f'                Random number = {result}')
        return result

    command_list = ["circle",
                        "squiggle",
                        "circle arc",
                        "slide to relative",
                        "dot",
                        "circle line",
                        "line",
                        "circle",
                        "slide to relative",
                        "slide to relative"]

    while time() < end_time:
        move_y()

        incoming_command = randrange(10)
        # # randomly draw or move
        # if getrandbits(1):
        #     draw = True
        # else:
        #     draw = False
        #
        # # randomly wait or not
        # if getrandbits(1):
        #     wait = True
        # else:
        #     wait = True


        print("random command = ", incoming_command)

        # low power response from AI Factory
        if incoming_command < 3:
            # self.digibot.pen_ready(False)
            print(f'DOBOT: {incoming_command}: draw command = "slide to relative", ')

            digibot.move_to_rel((rnd(2), rnd(2)))
            # print result
            # print(f'DOBOT: {incoming_command}: draw command = "slide to relative", ')

        # Mid power response from AI Factory
        elif 3 <= incoming_command < 8:
            # self.digibot.pen_ready(True)
            incoming_command = randrange(10)
            print('random choice = ', incoming_command)
            print(f'DOBOT: {incoming_command}: draw command = {command_list[incoming_command]}, drawing=True, wait=True')


            if incoming_command == 0:
                scale = randrange(5, 20)
                print('circle radius = ', scale)
                digibot.circle(scale)

            elif incoming_command == 1:
                squiggle_list = (rnd(incoming_command),
                                 rnd(incoming_command),
                                 rnd(incoming_command)
                                 )
                digibot.squiggle([squiggle_list])

            elif incoming_command == 2:
                # digibot.circle_arc(rnd(incoming_command),
                #                         [(rnd(incoming_command),
                #                           rnd(incoming_command),
                #                           rnd(incoming_command))
                #                          ])
                pass

            elif incoming_command == 3:
                digibot.move_to_rel((rnd(incoming_command),
                                      rnd(incoming_command)))

            elif incoming_command == 4:
                digibot.dot()

            elif incoming_command == 5:
                pass
                # digibot.circle_line(rnd(incoming_command),
                #                     (rnd(incoming_command), rnd(incoming_command)
                #                           ))
            elif incoming_command == 6:
                digibot.line((rnd(incoming_command),
                                   rnd(incoming_command)
                                   ))

            elif incoming_command == 7:
                # digibot.circle(rnd(incoming_command))
                pass

            else:
                digibot.move_to_rel((rnd(incoming_command),
                                           rnd(incoming_command)
                                           ))
            # print(f'DOBOT: {incoming_commandming_command}: draw command = {command_list[incoming_command]}, drawing=True, wait=True')

        # High power emission
        elif incoming_command >= 8:
            # self.digibot.pen_ready(True)
            print(f'DOBOT: {incoming_command}: draw command = "Squiggle", drawing=True, wait=True')
            squiggle_list = []
            for n in range(randrange(2, 4)):
                squiggle_list.append((rnd(incoming_command),
                                      rnd(incoming_command),
                                      rnd(incoming_command)))
            digibot.squiggle(squiggle_list)

            # print(f'DOBOT: {incoming_command}: draw command = "Squiggle", drawing=True, wait=True')


        sleep(1)

            # # move y along a bit
            # elapsed = int(time() - start_time) + 1
            # current_y_delta = elapsed * sub_division_of_duration
            # position_list = digibot.current_position()
            # digibot.print_position(position_list)
            # nowx, nowy, nowz, nowr = position_list[:4]
            # print('elapsed time = ', elapsed)
            # print(f'old y = {nowy}, move to = {nowy + current_y_delta}')
            # digibot.slide_to((nowx, nowy + current_y_delta, nowz, nowr))



