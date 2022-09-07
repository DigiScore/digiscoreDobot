import sys
import os
from time import sleep

sys.path.insert(0, os.path.abspath('.'))

from serial.tools import list_ports


available_ports = list_ports.comports()
print(f'available ports: {[x.device for x in available_ports]}')
port = available_ports[0].device

#
# from gustafsson.lib.dobot import Dobot
#
# # interface = Interface('/dev/tty.usbmodem1442301')
#
# bot = Dobot('/dev/tty.usbmodem1442301')


from gustafsson.lib.interface import Interface

bot = Interface('/dev/tty.usbmodem1442301')



# Defaults
bot.set_jog_joint_params([20, 20, 20, 30], [100, 100, 100, 100])
bot.set_jog_coordinate_params([20, 20, 20, 30], [100, 100, 100, 100])
bot.set_jog_common_params(150, 150)

print('Bot status:', 'connected' if bot.connected() else 'not connected')

joint_params = bot.get_jog_joint_params()
print('Joint params:', joint_params)

coordinate_params = bot.get_jog_coordinate_params()
print('Coordinate params:', coordinate_params)

common_params = bot.get_jog_common_params()
print('Common params:', common_params)

print('Rotating left')
bot.set_jog_command(1, 1)
sleep(1)

print('Rotating right')
bot.set_jog_command(1, 2)
sleep(1)

print('Stopping')
bot.set_jog_command(1, 0)
sleep(1)

print('Increasing joint speed')
bot.set_jog_joint_params([50, 50, 50, 30], [500, 500, 500, 500])

print('Moving forward')
bot.set_jog_command(1, 3)
sleep(1)

print('Moving backward')
bot.set_jog_command(1, 4)
sleep(1)

print('Stopping')
bot.set_jog_command(1, 0)
sleep(1)

print('Decreasing joint speed')
bot.set_jog_joint_params([10, 10, 10, 30], [100, 100, 100, 100])
print('Increasing coordinate speed')
bot.set_jog_coordinate_params([50, 50, 50, 30], [500, 500, 500, 500])

print('Moving down')
bot.set_jog_command(1, 5)
sleep(1)

print('Decreasing coordinate speed')
bot.set_jog_coordinate_params([10, 10, 10, 30], [100, 100, 100, 100])
print('Increasing general speed')
bot.set_jog_common_params(50, 50)

print('Moving up')
bot.set_jog_command(1, 6)
sleep(1)

print('Stopping')
bot.set_jog_command(1, 0)
sleep(1)



# if bot.connected():
#     print('Connected')
# else:
#     print('Not connected')
#
# bot.move_to(50, 50, 50, 0.5)
# bot.slide_to(-50, 10, 20, 0.5)
#
# from time import sleep
#
# from gustafsson.lib.interface import Interface
#
# bot = Interface('/dev/tty.usbmodem1442301')
#
# print('Bot status:', 'connected' if bot.connected() else 'not connected')
#
# joint_params = bot.get_point_to_point_joint_params()
# print('Joint params:', joint_params)
#
# jump_params = bot.get_point_to_point_jump_params()
# print('Jump params:', jump_params)
#
# # jump2_params = bot.get_point_to_point_jump2_params()
# # print('Jump2 params:', jump2_params)
#
# common_params = bot.get_point_to_point_common_params()
# print('Common params:', common_params)
#
# coordinate_params = bot.get_point_to_point_coordinate_params()
# print('Coordinate params:', coordinate_params)
#
# # Does nothing?
# bot.set_point_to_point_command(0, 10, 10, 10, 10)
# sleep(1)
#
# # Does nothing?
# bot.set_point_to_point_command(1, 30, 30, 30, 30)
# sleep(1)
#
# # One axis at a time
# bot.set_point_to_point_command(3, 10, 10, 10, 10)
# sleep(1)
#
# # One axis at a time
# bot.set_point_to_point_command(3, 30, 30, 30, 30)
# sleep(1)
#
# # Shortest path
# bot.set_point_to_point_command(4, 10, 10, 10, 10)
# sleep(1)
#
# # Shortest path
# bot.set_point_to_point_command(5, 30, 30, 30, 30)
# sleep(1)
#
# # Shortest path
# bot.set_point_to_point_command(6, 10, 10, 10, 10)
# sleep(1)
#
# # Shortest path
# bot.set_point_to_point_command(7, 30, 30, 30, 30)
# sleep(1)
#
# bot.set_point_to_point_command(8, 10, 10, 10, 10)
# sleep(1)
#
# # Does nothing?
# bot.set_point_to_point_po_command(0, 30, 30, 30, 30)