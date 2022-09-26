from threading import Thread
from time import sleep
from random import getrandbits, randrange


from digibot import Digibot

digibot = Digibot(verbose=False)
digibot.draw_stave()

(x, y, z, r, j1, j2, j3, j4) = digibot.pose()
print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

def rnd(power):
    pos = 1
    if getrandbits(1):
        pos = -1
    return (randrange(1, 5) + power) * pos

def process_list():
    if len(digibot.draw_list):
        draw_dict = digibot.draw_list.pop()[0]
        if draw_dict['type'] == "squiggle":
            pass
        elif draw_dict['type'] == 'move':
            pass
        elif draw_dict['type'] == 'line':
            pass
        elif draw_dict['type'] == 'swing':
            pass

    else:
        sleep(0.1)

draw_thread = Thread(target=process_list)
draw_thread.start()
