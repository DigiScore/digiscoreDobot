from time import sleep
import sys
import os
import math

from serial.tools import list_ports

from dobot_python.lib.interface import Interface


class Dobot:
    def __init__(self, port, verbose: bool = False):
        self.interface = Interface(port, verbose=verbose)

        self.interface.stop_queue(True)
        self.interface.clear_queue()
        self.interface.start_queue()

        self.interface.set_point_to_point_jump_params(10, 10)
        self.interface.set_point_to_point_joint_params([50, 50, 50, 50], [50, 50, 50, 50])
        self.interface.set_point_to_point_coordinate_params(50, 50, 50, 50)
        self.interface.set_point_to_point_common_params(50, 50)
        self.interface.set_point_to_point_jump2_params(5, 5, 5)

        self.interface.set_jog_joint_params([50, 50, 50, 50], [50, 50, 50, 50])
        self.interface.set_jog_coordinate_params([50, 50, 50, 50], [50, 50, 50, 50])
        self.interface.set_jog_common_params(50, 50)

        self.interface.set_continous_trajectory_params(50, 50, 50)

    def connected(self):
        return self.interface.connected()

    def get_pose(self):
        return self.interface.get_pose()

    def home(self, wait=True):
        self.interface.set_homing_command(0)
        if wait:
            self.wait()

    # 2. MOVL_XYZ,
    #         Linear movement,
    #         (x,y,z,r)
    #         is the target point in Cartesian coordinate system
    #         Move to the absolute coordinate, one axis at a time
    def move_to(self, x, y, z, r, wait=True):
        self.interface.set_point_to_point_command(2, x, y, z, r)
        if wait:
            self.wait()

    # 1. MOVJ_XYZ,
    #         Joint movement,
    #         (x,y,z,r)
    #         is the target point in Cartesian coordinate system
    #         Slide to the absolute coordinate, shortest possible path
    def slide_to(self, j1, j2, j3, j4, wait=True):
        self.interface.set_point_to_point_command(1, j1, j2, j3, j4)
        if wait:
            self.wait()

    # 7. MOVL_INC,Linear movement increment mode, (x,y,z,r)
    # is the Cartesian coordinate increment in Cartesian coordinate system
    def move_to_relative(self, x, y, z, r, wait=True):
        self.interface.set_point_to_point_command(7, x, y, z, r)
        if wait:
            self.wait()

    # 6. MOVJ_INC,
    #         Joint movement increment mode,
    #         (x,y,z,r)
    #         is the angle increment in Joint coordinate system
    #         Slide joints to the relative coordinate, one axis at a time
    def slide_to_relative(self, j1, j2, j3, j4, wait=True):
        self.interface.set_point_to_point_command(6, j1, j2, j3, j4)
        if wait:
            self.wait()

    # Wait until the instruction finishes
    def wait(self, queue_index=None):
        # If there are no more instructions in the queue, it will end up
        # always returning the last instruction - even if it has finished.
        # Use a zero wait as a non-operation to bypass this limitation
        self.interface.wait(0)

        if queue_index is None:
            queue_index = self.interface.get_current_queue_index()
        while True:
            if self.interface.get_current_queue_index() > queue_index:
                break

            # sleep(0.5)

    # Move according to the given path
    def follow_path(self, path, wait=True):
        self.interface.stop_queue()
        queue_index = None
        for point in path:
            queue_index = self.interface.set_continous_trajectory_command(1, point[0], point[1], point[2], 50)
        self.interface.start_queue()
        if wait:
            self.wait(queue_index)

    # Move according to the given path
    def follow_path_relative(self, path, wait=True):
        self.interface.stop_queue()
        queue_index = None
        for point in path:
            queue_index = self.interface.set_continous_trajectory_command(0,  point[0], point[1], point[2], 50)
        self.interface.start_queue()
        if wait:
            self.wait(queue_index)

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath('.'))

    # find available ports and locate Dobot (-1)
    available_ports = list_ports.comports()
    print(f'available ports: {[x.device for x in available_ports]}')
    port = available_ports[-1].device
    testbot = Dobot(port)

    def print_position():
        pos = testbot.interface.get_pose()
        print(f'Centre position (x, y, z, r): {pos[0:4]}, angles = {pos[4:]}')


    print('locating home')
    testbot.home()

    print('Unlock the arm and place it on the middle of the paper')
    input("Press enter to continue...")
    center = testbot.interface.get_pose()

    print_position()

    testbot.move_to_relative(0, 0, 10, 0)
    print('Ready to draw')

    testbot.move_to_relative(0, 0, -10, 0)

    testbot.interface.set_continous_trajectory_params(200, 200, 200)

    # Draw circle
    path = []
    steps = 24
    scale = 50
    for i in range(steps + 2):
        x = math.cos(((math.pi * 2) / steps) * i)
        y = math.sin(((math.pi * 2) / steps) * i)

        path.append([center[0] + x * scale, center[1] + y * scale, center[2]])
    testbot.follow_path(path)

    # Move up and then back to the start
    testbot.move_to_relative(0, 0, 10, 0)
    testbot.slide_to(center[4], center[5], center[6], center[7])
    # print("moving to relative position x + 10")
    # testbot.move_to_relative(10, 0, 0, 0)
    # print_position()
    #
    # print("slide joints to relative position j1 + 10")
    # testbot.slide_to_relative(10, 0, 0, 0)
    # print_position()
    #
    # print('move to an absolute cartesian position - original centre')
    # x, y, z, r = centre_pos[0], centre_pos[1], centre_pos[2], centre_pos[3]
    # testbot.move_to(x, y, z, r)
    #
    # print('move to an absolute cartesian position - original centre pen up')
    # x, y, z, r = centre_pos[0], centre_pos[1], centre_pos[2], centre_pos[3]
    # testbot.move_to(x, y, z + 5, r)

