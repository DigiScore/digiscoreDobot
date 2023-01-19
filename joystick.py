import hid
from threading import Timer

class Joystick:
    def __init__(self):
        self.gamepad = hid.device()
        self.gamepad.open(0x0079, 0x0006)
        self.gamepad.set_nonblocking(True)

        joy_thread = Timer(0.1, self.joystick_listener)
        joy_thread.start()

    def joystick_listener(self):
        # scaling vars
        old_min = 0
        old_max = 255
        new_min = -1
        new_max = 1

        while True:
            report = self.gamepad.read(64)
            if report:
                print(report)
                # new_value = ((old_value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

                self.left_joysick_left_right = round((((report[0] - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min), 2)
                self.left_joysick_up_down = round((((report[1] - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min), 2)
                self.right_joysick_left_right = round((((report[3] - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min), 2)
                self.right_joysick_up_down = round((((report[4] - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min), 2)
                self.num_buttons = report[5]
                self.all_other_buttons = report[6]
                # print(left_joysick_left_right,
                #       left_joysick_up_down,
                #       right_joysick_left_right,
                #       right_joysick_up_down,
                #       num_buttons,
                #       all_other_buttons)

if __name__ == "__main__":
    Joystick()
