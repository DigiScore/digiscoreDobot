from nebula.nebula import Nebula
from time import sleep, time
from threading import Thread
from random import random, randrange, getrandbits
import pyaudio
import numpy as np
import logging

from digiDobot import Digidobot

class DrawBot:
    def __init__(self, duration_of_piece: int = 120):
        # start dobot
        self.digibot = Digidobot(verbose=True)

        # start Nebula
        self.nebula = Nebula(speed=1)
        self.nebula.director()

        # set up mic listening funcs
        self.CHUNK = 2 ** 11
        self.RATE = 44100
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)

        # start operating vars
        self.running = True
        self.old_value = 0
        self.start_time = time()
        self.end_time = self.start_time + duration_of_piece

        # get y-creep sub-division e.g. 420 points across
        # the y-stave, divided by time in seconds
        # self.duration = duration_of_piece
        self.sub_division_of_duration = duration_of_piece / 420
        print('sub division = ', self.sub_division_of_duration)

        # start the bot listening and drawing
        # while time() < end_time:
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

            if peak > 2000:
                bars = "#" * int(50 * peak / 2 ** 16)
                print("MIC LISTENER: %05d %s" % (peak, bars))

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

    def rnd(self, power_of_command):
        # movement + or - (random)
        if getrandbits(1):
            posneg = 1
        else:
            posneg = -1

        # multiplication factor
        if getrandbits(1):
            multiplication_factor = randrange(1, power_of_command)
        else:
            multiplication_factor = 1
        return (random() + multiplication_factor) * posneg

    def dobot_control(self):
        print("Started dobot control thread")

        # todo - constant movement across page y from 210 -> -210
        # todo - healthchecker here inc position check and righting
        while self.running:
            # get current nebula emission value
            # print(f'DOBOT: Connected {self.digibot.bot.connected()}')
            live_emission_data = self.nebula.user_live_emission_data()
            print(f"MAIN: emission value = {live_emission_data}")
            if live_emission_data != self.old_value:
                # multiply by 10 for local logic
                value_int = int(live_emission_data * 10)
                self.dobot_commands(value_int)

            else:
                # print("MAIN: sleep")
                sleep(0.1)

            # move y along a bit
            elapsed = int(time() - self.start_time)
            current_y_delta = elapsed * self.sub_division_of_duration
            position_list = self.digibot.current_position()
            self.digibot.print_position(position_list)
            nowx, nowy, nowz, nowr = position_list[:4]
            print('elapsed time = ', elapsed)
            print(f'old y = {nowy}, move to = {nowy + current_y_delta}')
            self.digibot.slide_to((nowx, nowy + current_y_delta, nowz, nowr))

            # check end of duration
            if time() > self.end_time:

                self.digibot.close()
                self.running = False

    def dobot_commands(self, incoming_command):
        """Controls the symbolic interpretation of Master Output from AI Factory
        with Dobot commands. Basic schema:
            < 2: slide to relative
            2-8: squiggle (draw or not)
            >=8: random
            """
        command_list = ["circle",
                        "squiggle",
                        "circle arc",
                        "move to relative",
                        "dot",
                        "circle line",
                        "line",
                        "circle",
                        "slide to relative",
                        "slide to relative"]

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

        # low power response from AI Factory
        if incoming_command < 3:
            # self.digibot.pen_ready(False)
            self.digibot.slide_to_rel((self.rnd(2), self.rnd(2)))
            # print result
            print(f'DOBOT: {incoming_command}: draw command = "move to relative", wait=False')

        # high power response from AI Factory
        elif incoming_command >= 8:
            # self.digibot.pen_ready(True)
            if incoming_command == 1:
                self.digibot.circle(self.rnd(incoming_command))
            elif incoming_command == 2:
                squiggle_list = []
                for n in range(randrange(2, 4)):
                    squiggle_list.append((self.rnd(incoming_command),
                                          self.rnd(incoming_command),
                                          self.rnd(incoming_command)))
                self.digibot.squiggle(squiggle_list)
            elif incoming_command == 3:
                self.digibot.slide_to_rel((self.rnd(incoming_command),
                                          self.rnd(incoming_command)))
            elif incoming_command == 4:
                self.digibot.circle_arc(self.rnd(incoming_command),
                                        [(self.rnd(incoming_command),
                                          self.rnd(incoming_command),
                                          self.rnd(incoming_command))
                                         ])
            elif incoming_command == 5:
                self.digibot.dot()
            elif incoming_command == 6:
                self.digibot.circle_line(self.rnd(incoming_command),
                                         (self.rnd(incoming_command), self.rnd(incoming_command)
                                          ))
            elif incoming_command == 7:
                self.digibot.line((self.rnd(incoming_command),
                                   self.rnd(incoming_command)
                                   ))
            elif incoming_command == 8:
                self.digibot.circle(self.rnd(incoming_command))

            else:
                self.digibot.slide_to_rel((self.rnd(incoming_command),
                                           self.rnd(incoming_command)
                                           ))
            print(f'DOBOT: {incoming_command}: draw command = {command_list[incoming_command]}, drawing=True, wait=True')

        else:
            # self.digibot.pen_ready(True)
            squiggle_list = (self.rnd(incoming_command),
                             self.rnd(incoming_command),
                             self.rnd(incoming_command)
                             )
            self.digibot.squiggle([squiggle_list])
            print(f'DOBOT: {incoming_command}: draw command = "Squiggle", drawing=True, wait=True')


if __name__ == "__main__":
    drawbot = DrawBot()


