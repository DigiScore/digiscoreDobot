from time import sleep, time
from threading import Thread
from random import random, randrange, getrandbits
import pyaudio
import numpy as np
import logging

from digibot import Digibot
from nebula.nebula import Nebula

class DrawBot:
    """
    The main script to start the robot arm drawing digital score work.
    Digibot calls the local interpretor for project specific functions.
    This communicates directly to the pydobot library.
    Nebula kick starts the AI Factory for generating NNet data and affect flows.
    This script also controls the live mic audio analyser.
    Args:
        duration_of_piece: the duration in seconds of the drawing
        continuous_line: Bool: True = will not jump between points
    """
    def __init__(self, duration_of_piece: int = 120,
                 continuous_line: bool = True):
        # start dobot communications
        self.digibot = Digibot(verbose=False)
        self.digibot.draw_stave()
        self.digibot.go_position_ready()

        # reset speed
        self.digibot.speed(velocity=100, acceleration=100)
        self.dobot_commands_queue = []

        # start Nebula AI Factory
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
        self.continuous_line = continuous_line
        self.running = True
        self.logging = False
        self.old_value = 0
        self.start_time = time()
        self.end_time = self.start_time + duration_of_piece

        # start the bot listening and drawing threads
        listener_thread = Thread(target=self.director)
        dobot_thread = Thread(target=self.dobot_control)

        listener_thread.start()
        dobot_thread.start()

    def director(self):
        """Loop thread that listens to live sound and analyses amplitude.
        Normalises then stores this into the nebula dataclass for shared use."""

        print("Starting mic listening stream & thread")
        while self.running:
            # get amplitude from mic input
            data = np.frombuffer(self.stream.read(self.CHUNK,
                                             exception_on_overflow=False),
                                 dtype=np.int16)
            peak = np.average(np.abs(data)) * 2

            if peak > 2000:
                bars = "#" * int(50 * peak / 2 ** 16)
                if self.logging:
                    print("MIC LISTENER: %05d %s" % (peak, bars))

            # normalise it for range 0.0 - 1.0
            normalised_peak = ((peak - 0) / (20000 - 0)) * (1 - 0) + 0
            if normalised_peak > 1.0:
                normalised_peak = 1.0

            # put normalised amplitude into Nebula's dictionary for use
            self.nebula.user_input(normalised_peak)

    def terminate(self):
        """Smart collapse of all threads and comms"""

        print('TERMINATING')
        self.digibot.go_position_end()
        self.running = False
        self.digibot.close()

    def rnd(self, power_of_command: int) -> int:
        """Returns a randomly generated + or - integer,
        influenced by the incoming power factor"""
        pos = 1
        if getrandbits(1):
            pos = -1
        result = (randrange(1, 5) + power_of_command) * pos
        if self.logging:
            print(f'Rnd result = {result}')
        return result

    def move_y(self):
        """When called moves the pen across the y-axis
        aligned to the delta change in time across the duration of the piece"""
        # How far into the piece
        elapsed = time() - self.start_time

        # get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.digibot.pose()
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        newy = (((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175
        if self.logging:
            print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250

        # which mode
        if self.continuous_line:
            self.digibot.move_to(x, newy, 0, r, True)
        else:
            self.digibot.jump_to(x, newy, 0, r, True)

    def move_y_random(self):
        """Moves x and y pen position to nearly the true Y point."""
        # How far into the piece
        elapsed = time() - self.start_time

        # get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.digibot.pose()
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        newy = (((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175
        if self.logging:
            print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250
        self.digibot.move_to(x, newy + self.rnd(10), 0, r, True)

    def dobot_control(self):
        """Loop thread that controls the robot arm
        responses to the data generated by Nebula."""

        print("Started dobot control thread")

        while self.running:
            # check end of duration
            if time() > self.end_time:
                self.terminate()

            # get current nebula emission value
            live_emission_data = self.nebula.user_live_emission_data()

            # if the value has changed then ...
            if live_emission_data != self.old_value:
                if self.logging:
                    print(f"MAIN: emission value = {live_emission_data}")
                self.old_value = live_emission_data

                # multiply by 10 for local logic (power value)
                incoming_command = int(live_emission_data * 10) + 1

                # 1. clear the alarms
                self.digibot.clear_alarms()

                # 2. move Y
                self.move_y()

                # 3. get speed based on power of incoming value
                self.digibot.speed(velocity=incoming_command * 10,
                                   acceleration=incoming_command * 10)

                (x, y, z, r, j1, j2, j3, j4) = self.digibot.pose()
                if self.logging:
                    print(f'Current position: x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

                # low power response from AI Factory
                if incoming_command < 3:

                    # does this or that
                    if getrandbits(1):
                        self.move_y_random()
                    else:
                        squiggle_list = (self.rnd(incoming_command),
                                         self.rnd(incoming_command),
                                         self.rnd(incoming_command)
                                         )
                        self.digibot.squiggle([squiggle_list])

                # high power response from AI Factory
                elif incoming_command >= 7:
                    randchoice = randrange(3)
                    if self.logging:
                        print(f'randchoice == {randchoice}')

                    # line to somewhere
                    if randchoice == 0:
                        self.digibot.move_to(x + self.rnd(incoming_command),
                                             y + self.rnd(incoming_command),
                                             0, 0,
                                             True)

                    # big messy squiggles
                    if randchoice == 1:
                        squiggle_list = []
                        for n in range(randrange(2, 4)):
                            squiggle_list.append((randrange(-10, 10),
                                                  randrange(-10, 10),
                                                  randrange(-10, 10))
                                                 )
                        self.digibot.squiggle(squiggle_list)

                    # arc/ circle
                    elif randchoice == 2:
                        self.digibot.arc(x + self.rnd(incoming_command),
                                         y + self.rnd(incoming_command),
                                         0, 0,
                                         x + self.rnd(incoming_command),
                                         y + self.rnd(incoming_command),
                                         0, 0,
                                         True)

                else:
                    # small squiggles
                    squiggle_list = []
                    for n in range(randrange(2, 4)):
                        squiggle_list.append((randrange(-5, 5),
                                              randrange(-5, 5),
                                              randrange(-5, 5))
                                             )
                    self.digibot.squiggle(squiggle_list)

                # take a breath
                sleep(0.4)

            # wait a bit
            else:
                sleep(0.4)


if __name__ == "__main__":
    drawbot = DrawBot(duration_of_piece=240, continuous_line=True)

