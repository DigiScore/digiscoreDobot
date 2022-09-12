from nebula.nebula import Nebula
from time import sleep
from threading import Thread
from random import random, randrange, getrandbits
import pyaudio
import numpy as np

from digiDobot import Digidobot

class DrawBot:
    def __init__(self):
        # start Nebula
        self.nebula = Nebula(speed=1)
        self.nebula.director()

        # start dobot
        self.digibot = Digidobot()

        # set up mic listening funcs
        self.CHUNK = 2 ** 11
        self.RATE = 44100
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)

        # start the bot listening and drawing
        self.running = True
        self.old_value = 0

        listener_thread = Thread(target=self.director)
        dobot_thread = Thread(target=self.dobot_control)
        listener_thread.start()
        dobot_thread.start()
        listener_thread.join()


    def director(self):
        print("Starting mic listening stream & thread")
        while self.running:
            # get amplitude from mic input
            data = np.frombuffer(self.stream.read(self.CHUNK,
                                             exception_on_overflow=False),
                                 dtype=np.int16)
            peak = np.average(np.abs(data)) * 2

            # normalise it for range 0.0 - 1.0
            normalised_peak = ((peak - 0) / (20000 - 0)) * (1 - 0) + 0
            if normalised_peak > 1.0:
                normalised_peak = 1.0

            # put normalised amplitude into Nebula's dictionary for use
            self.nebula.user_input(normalised_peak)

            # # get live emission from Nebula (not list)
            # self.nebula_emission_val = self.nebula.live_emission_data

    def terminate(self):
        self.running = False

    def rnd(self):
        # movement + or - (random)
        if getrandbits(1):
            posneg = 10
        else:
            posneg = -10
        return random() * posneg


    def dobot_control(self):
        print("Started dobot control thread")

        while self.running:
            # get current nebula emission value
            live_emission_data = self.nebula.user_live_emission_data()
            print(f"emission value = {live_emission_data}")
            if live_emission_data != self.old_value:
                # multiply by 10 for local logic
                value_int = int(live_emission_data * 10)
                self.dobot_commands(value_int)

            else:
                sleep(1)

    def dobot_commands(self, incoming_command):
        command_list = ["circle",
                             "squiggle",
                             "move to relative",
                             "circle arc",
                             "dot",
                             "circle line",
                             "line",
                             "circle",
                             "slide to relative",
                             "slide to relative"]

        # randomly draw or move
        if getrandbits(1):
            draw = True
        else:
            draw = False

        # randomly wait or not
        if getrandbits(1):
            wait = True
        else:
            wait = False

        print(f'{incoming_command}: DOBOT draw command = {command_list[incoming_command]}, drawing={draw}, wait={wait}')

        if incoming_command == 1:
            self.digibot.circle(self.rnd(), draw, wait)
        elif incoming_command == 2:
            squiggle_list = []
            for n in range(randrange(2, 10)):
                squiggle_list.append((self.rnd(), self.rnd(), self.rnd()))
            self.digibot.squiggle(squiggle_list, draw, wait)
        elif incoming_command == 3:
            self.digibot.move_to((self.rnd(), self.rnd()))
        elif incoming_command == 4:
            self.digibot.circle_arc(self.rnd(), [(self.rnd(), self.rnd(), self.rnd())], draw, wait)
        elif incoming_command == 5:
            self.digibot.dot()
        elif incoming_command == 6:
            self.digibot.circle_line(self.rnd(), (self.rnd(), self.rnd()), draw, wait)
        elif incoming_command == 7:
            self.digibot.line((self.rnd(), self.rnd()), draw, wait)
        elif incoming_command == 8:
            self.digibot.circle(self.rnd(), wait)
        else:
            self.digibot.slide_to((self.rnd(), self.rnd()), wait)


if __name__ == "__main__":
    drawbot = DrawBot()

