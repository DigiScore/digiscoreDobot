import hid
import time

gamepad = hid.device()
gamepad.open(0x0079, 0x0006)
gamepad.set_nonblocking(True)

# scaling vars
old_min = 0
old_max = 255
new_min = -1
new_max = 1

while True:
    report = gamepad.read(64)
    if report:
        print(report)
        # todo - add scaler -1 ~ 1
        # new_value = ((old_value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

        left_joysick_left_right = round((((report[0] - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min), 2)
        left_joysick_up_down = round((((report[1] - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min), 2)
        right_joysick_left_right = round((((report[3] - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min), 2)
        right_joysick_up_down = round((((report[4] - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min), 2)
        num_buttons = report[5]
        all_other_buttons = report[6]
        # print(left_joysick_left_right,
        #       left_joysick_up_down,
        #       right_joysick_left_right,
        #       right_joysick_up_down,
        #       num_buttons,
        #       all_other_buttons)
