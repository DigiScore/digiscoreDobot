from nebula.nebula import Nebula
from time import sleep, time
from threading import Thread
from random import random, randrange, getrandbits
import pyaudio
import numpy as np
import logging

from digibot import Digibot

class DrawBot:
    def __init__(self, duration_of_piece: int = 120):
        # start dobot
        self.digibot = Digibot(verbose=True)
        self.digibot.draw_stave()
        # reset speed
        self.digibot.speed(velocity=100, acceleration=100)
        self.dobot_commands_queue = []

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
        self.duration_of_piece = duration_of_piece
        self.running = True
        self.old_value = 0
        self.start_time = time()
        self.end_time = self.start_time + duration_of_piece

        # get y-creep sub-division e.g. 420 points across
        # the y-stave, divided by time in seconds
        # self.duration = duration_of_piece
        # self.sub_division_of_duration = duration_of_piece / 420
        # print('sub division = ', self.sub_division_of_duration)

        # start the bot listening and drawing
        # while time() < end_time:
        listener_thread = Thread(target=self.director)
        dobot_thread = Thread(target=self.dobot_control)
        draw_thread = Thread(target=self.dobot_commands)

        listener_thread.start()
        dobot_thread.start()
        draw_thread.start()
        # listener_thread.join()

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
        pos = 1
        if getrandbits(1):
            pos = -1
        result = (randrange(1, 5) + power_of_command) * pos
        print(f'Rnd result = {result}')
        return result

        # # movement + or - (random)
        # if getrandbits(1):
        #     posneg = 1
        # else:
        #     posneg = -1
        #
        # # multiplication factor
        # if getrandbits(1):
        #     multiplication_factor = randrange(1, power_of_command)
        # else:
        #     multiplication_factor = 1
        # return (random() + multiplication_factor) * posneg

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
                if len(self.dobot_commands_queue):
                    self.dobot_commands_queue.append(value_int)

            else:
                # print("MAIN: sleep")
                sleep(0.1)

            # # move y along a bit
            # elapsed = int(time() - self.start_time)
            # current_y_delta = elapsed * self.sub_division_of_duration
            # position_list = self.digibot.current_position()
            # self.digibot.print_position(position_list)
            # nowx, nowy, nowz, nowr = position_list[:4]
            # print('elapsed time = ', elapsed)
            # print(f'old y = {nowy}, move to = {nowy + current_y_delta}')
            # self.digibot.slide_to((nowx, nowy + current_y_delta, nowz, nowr))

            # check end of duration
            if time() > self.end_time:

                self.digibot.close()
                self.running = False

    def move_y(self):
        # move y along a bit
        elapsed = time() - self.start_time

        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        newy = (((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175

        # current_y_delta = elapsed * sub_division_of_duration
        (x, y, z, r, j1, j2, j3, j4) = self.digibot.pose()
        print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # lift up pen
        # digibot.move_to_relative(0, 0, 5, 0)
        print('elapsed time = ', elapsed)
        print(f'old y = {y}, move to = {newy}')
        if x <= 200 or x >= 300:
            x = 250
        # if mode == 1:
        self.digibot.jump_to(x, newy, 0, r, True)

        # digibot.move_to_relative(0, 0, -5, 0)
        # return (x, y, z)

    def dobot_commands(self):
        """Controls the symbolic interpretation of Master Output from AI Factory
        with Dobot commands. Basic schema:
            < 2: slide to relative
            2-8: squiggle (draw or not)
            >=8: random
            """
        # command_list = ["circle",
        #                 "squiggle",
        #                 "circle arc",
        #                 "move to relative",
        #                 "dot",
        #                 "circle line",
        #                 "line",
        #                 "circle",
        #                 "slide to relative",
        #                 "slide to relative"]

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

        if len(self.dobot_commands_queue):
            incoming_command = self.dobot_commands_queue.pop()

            # 1. clear the alarms
            self.digibot.clear_alarms()

            # get speed
            self.digibot.speed(velocity=incoming_command * 10,
                               acceleration=incoming_command * 10)

            (x, y, z, r, j1, j2, j3, j4) = self.digibot.pose()
            print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

            # low power response from AI Factory
            if incoming_command < 3:
                # self.digibot.pen_ready(False)
                # self.digibot.slide_to_rel((self.rnd(2), self.rnd(2)))
                # # print result
                # print(f'DOBOT: {incoming_command}: draw command = "move to relative", wait=False')
                self.move_y()

            # high power response from AI Factory
            elif incoming_command >= 8:
                randchoice = randrange(4)
                print(f'randchoice == {randchoice}')

                # move y
                if randchoice == 0:
                    print('move y')
                    self.move_y()

                # messy squiggle
                if randchoice <= 1:
                    squiggle_list = []
                    for n in range(randrange(2, 4)):
                        squiggle_list.append((randrange(-5, 5),
                                              randrange(-5, 5),
                                              randrange(-5, 5))
                                             )
                    self.digibot.squiggle(squiggle_list)

                    # digibot.squiggle([(randrange(1, 5), randrange(1, 5), randrange(1, 5))])

                # line to somewhere
                elif randchoice == 2:
                    self.digibot.move_to(x + self.rnd(incoming_command),
                                         y + self.rnd(incoming_command),
                                         0, 0,
                                         True)

                # arc/ circle
                elif randchoice == 3:
                    self.digibot.arc(x + self.rnd(incoming_command),
                                     y + self.rnd(incoming_command),
                                     0, 0,
                                     x + self.rnd(incoming_command),
                                     y + self.rnd(incoming_command),
                                     0, 0,
                                     True)


            #   self.digibot.pen_ready(True)
                # if incoming_command == 1:
                #     self.digibot.circle(self.rnd(incoming_command))
                # elif incoming_command == 2:
                #     squiggle_list = []
                #     for n in range(randrange(2, 4)):
                #         squiggle_list.append((self.rnd(incoming_command),
                #                               self.rnd(incoming_command),
                #                               self.rnd(incoming_command)))
                #     self.digibot.squiggle(squiggle_list)
                # elif incoming_command == 3:
                #     self.digibot.slide_to_rel((self.rnd(incoming_command),
                #                               self.rnd(incoming_command)))
                # elif incoming_command == 4:
                #     self.digibot.circle_arc(self.rnd(incoming_command),
                #                             [(self.rnd(incoming_command),
                #                               self.rnd(incoming_command),
                #                               self.rnd(incoming_command))
                #                              ])
                # elif incoming_command == 5:
                #     self.digibot.dot()
                # elif incoming_command == 6:
                #     self.digibot.circle_line(self.rnd(incoming_command),
                #                              (self.rnd(incoming_command), self.rnd(incoming_command)
                #                               ))
                # elif incoming_command == 7:
                #     self.digibot.line((self.rnd(incoming_command),
                #                        self.rnd(incoming_command)
                #                        ))
                # elif incoming_command == 8:
                #     self.digibot.circle(self.rnd(incoming_command))
                #
                # else:
                #     self.digibot.slide_to_rel((self.rnd(incoming_command),
                #                                self.rnd(incoming_command)
                #                                ))
                # print(f'DOBOT: {incoming_command}: draw command = {command_list[incoming_command]}, drawing=True, wait=True')

            else:
                # self.digibot.pen_ready(True)
                squiggle_list = (self.rnd(incoming_command),
                                 self.rnd(incoming_command),
                                 self.rnd(incoming_command)
                                 )
                self.digibot.squiggle([squiggle_list])
                # print(f'DOBOT: {incoming_command}: draw command = "Squiggle", drawing=True, wait=True')

        else:
            sleep(0.2)

if __name__ == "__main__":
    drawbot = DrawBot()


