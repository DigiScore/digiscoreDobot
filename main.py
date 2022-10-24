from time import sleep, time
from threading import Thread
from random import random, randrange, getrandbits
import pyaudio
import numpy as np
import logging
from serial.tools import list_ports
import sys

from digibot import Digibot
from nebula.nebula import Nebula
from queue import Queue

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
        speed: int the dynamic tempo of the all processes. 1 = slow, 5 = fast
    """
    def __init__(self, duration_of_piece: int = 120,
                 continuous_line: bool = True,
                 speed: int = 1,
                 staves: int = 1):

        # config logging for all modules
        logging.basicConfig(level=logging.INFO)

        # start dobot communications
        # find available ports and locate Dobot (-1)
        available_ports = list_ports.comports()
        print(f'available ports: {[x.device for x in available_ports]}')
        port = available_ports[-1].device

        self.digibot = Digibot(port=port, verbose=False)
        self.digibot.draw_stave(staves=staves)
        self.digibot.go_position_ready()

        # reset speed
        # self.digibot.speed(velocity=100, acceleration=100)
        self.global_speed = speed
        self.dobot_commands_queue = Queue(maxsize=1)

        # start Nebula AI Factory
        self.nebula = Nebula(self.dobot_commands_queue, speed=speed)
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
        self.old_value = 0
        self.start_time = time()
        self.end_time = self.start_time + duration_of_piece

        # start the bot listening and drawing threads
        listener_thread = Thread(target=self.director)
        dobot_thread = Thread(target=self.dobot_control)

        listener_thread.start()
        dobot_thread.start()

        # sys.exit()

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
                logging.debug("MIC LISTENER: %05d %s" % (peak, bars))

            # normalise it for range 0.0 - 1.0
            normalised_peak = ((peak - 0) / (20000 - 0)) * (1 - 0) + 0
            if normalised_peak > 1.0:
                normalised_peak = 1.0

            # put normalised amplitude into Nebula's dictionary for use
            self.nebula.user_input(normalised_peak)
        logging.info('quitting listener thread')

    def terminate(self):
        """Smart collapse of all threads and comms"""
        print('TERMINATING')
        self.digibot.home()
        self.digibot.close()
        self.running = False

    def rnd(self, power_of_command: int) -> int:
        """Returns a randomly generated + or - integer,
        influenced by the incoming power factor"""
        pos = 1
        if getrandbits(1):
            pos = -1
        result = (randrange(1, 5) + randrange(power_of_command)) * pos
        logging.debug(f'Rnd result = {result}')
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
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250

        # move z (pen head) a little
        if getrandbits(1):
            z = 0
        else:
            z = randrange(-2, 2)

        # which mode
        if self.continuous_line:
            self.digibot.move_to(x, newy, z, r, True)
        else:
            self.digibot.jump_to(x, newy, z, r, True)

        logging.info(f'Move Y to x:{round(x)} y:{round(newy)} z:{round(z)}')

    def move_y_random(self):
        """Moves x and y pen position to nearly the true Y point."""
        # How far into the piece
        elapsed = time() - self.start_time

        # get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.digibot.pose()
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        newy = (((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250
        self.digibot.jump_to(x + self.rnd(10), newy + self.rnd(10), 0, r, True)

    # todo - this should be absorbed into affect
    def dobot_control(self):
        """Loop thread that controls the robot arm
        responses to the data generated by Nebula."""

        print("Started dobot control thread")

        while self.running:
            while not self.dobot_commands_queue.empty():
                print('================')
                # check end of duration
                if time() > self.end_time:
                    self.terminate()
                    self.running = False
                    break

                # get current nebula emission value
                # live_emission_data = self.nebula.user_live_emission_data()
                live_emission_data = self.dobot_commands_queue.get()

                # if the value has changed then ...
                if live_emission_data != self.old_value:
                    self.old_value = live_emission_data

                    # multiply by 10 for local logic (power value)
                    incoming_command = int(live_emission_data * 10) + 1
                    logging.info(f"MAIN: emission value = {live_emission_data} == {incoming_command}")

                    # 1. clear the alarms
                    self.digibot.clear_alarms()

                    # 2. move Y
                    # self.move_y()

                    # 3. get speed based on power of incoming value * global speed setting * 2
                    if getrandbits(1):
                        self.digibot.speed(velocity=((incoming_command * 10) * self.global_speed) * 2,
                                           acceleration=((incoming_command * 10) * self.global_speed) * 2
                                           )
                    else:
                        self.digibot.speed(velocity=randrange(30, 200),
                                           acceleration=randrange(30, 200)
                                           )

                    (x, y, z, r, j1, j2, j3, j4) = self.digibot.pose()
                    logging.debug(f'Current position: x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

                    #
                    # LOW power response from AI Factory
                    #
                    if incoming_command < 3:
                        # self.move_y()
                        # self.digibot.dot()

                        logging.info('Emission < 3: PASS')

                        #
                        # # does this or that
                        # if getrandbits(1):
                        #     self.move_y_random()
                        #     logging.info('Emission < 3: move Y random')
                        # else:
                        #     squiggle_list = (self.rnd(incoming_command),
                        #                      self.rnd(incoming_command),
                        #                      self.rnd(incoming_command)
                        #                      )
                        #     self.digibot.squiggle([squiggle_list])
                        #     logging.info('Emission < 3: squiggle')

                    #
                    # HIGH power response from AI Factory
                    #
                    elif incoming_command >= 7:
                        self.move_y()

                        randchoice = randrange(3)
                        logging.debug(f'randchoice == {randchoice}')

                        # line to somewhere
                        if randchoice == 0:
                            self.digibot.move_to(x + self.rnd(incoming_command),
                                                 y + self.rnd(incoming_command),
                                                 z, 0,
                                                 False)
                            logging.info('Emission >=7: draw line')

                        # big messy squiggles
                        if randchoice == 1:
                            squiggle_list = []
                            for n in range(randrange(2, 4)):
                                squiggle_list.append((randrange(-10, 10),
                                                      randrange(-10, 10),
                                                      randrange(-10, 10))
                                                     )
                            self.digibot.squiggle(squiggle_list)
                            logging.info('Emission >=7: messy squiggle')


                        # arc/ circle
                        elif randchoice == 2:
                            self.digibot.arc(x + self.rnd(incoming_command),
                                             y + self.rnd(incoming_command),
                                             z, 0,
                                             x + self.rnd(incoming_command),
                                             y + self.rnd(incoming_command),
                                             z, 0,
                                             False)
                            logging.info('Emission >=7: draw arc/ circle')

                    #
                    # MID power response
                    #
                    else:
                        # small squiggles
                        squiggle_list = []
                        for n in range(randrange(2, 4)):
                            squiggle_list.append((randrange(-5, 5) / 10,
                                                  randrange(-5, 5) / 10,
                                                  randrange(-5, 5) / 10)
                                                 )
                        self.digibot.squiggle(squiggle_list)
                        logging.info('3 < Emission < 7: small squiggle')

                    # take a breath
                    sleep(0.4 / self.global_speed)

                # wait a bit until the new emission is different from current
                # else:
                # print("!!!!!")
                sleep(0.1)

        logging.info('quitting dobot director thread')


if __name__ == "__main__":
    DrawBot(duration_of_piece=80, continuous_line=True, speed=3, staves=0)

