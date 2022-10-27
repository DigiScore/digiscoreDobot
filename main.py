from time import sleep, time
from threading import Thread
from random import random, randrange, getrandbits
import pyaudio
import numpy as np
import logging
from serial.tools import list_ports
from queue import Queue

from digibot import Digibot
from nebula.nebula import Nebula

class Main:
    """
    The main script to start the robot arm drawing digital score work.
    Digibot calls the local interpreter for project specific functions.
    This communicates directly to the pydobot library.
    Nebula kick-starts the AI Factory for generating NNet data and affect flows.
    This script also controls the live mic audio analyser.
    Args:
        duration_of_piece: the duration in seconds of the drawing
        continuous_line: Bool: True = will not jump between points
        speed: int the dynamic tempo of the all processes. 1 = slow, 10 = fast
        pen: bool - True for pen, false for pencil
    """
    def __init__(self, duration_of_piece: int = 120,
                 continuous_line: bool = True,
                 speed: int = 5,
                 staves: int = 1,
                 pen: bool = True):

        # config logging for all modules
        logging.basicConfig(level=logging.INFO)

        # find available ports and locate Dobot (-1)
        available_ports = list_ports.comports()
        print(f'available ports: {[x.device for x in available_ports]}')
        port = available_ports[-1].device

        # start dobot communications
        self.digibot = Digibot(port=port, verbose=False)
        arm_speed = (((speed - 1) * (300 - 50)) / (10 - 1)) + 50
        self.digibot.speed(velocity=arm_speed,
                           acceleration=arm_speed)
        self.digibot.draw_stave(staves=staves)
        self.digibot.go_position_ready()


        # find global speed 0.1 - 1 (reverse of speed)
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        self.global_speed = ((speed - 1) * (0.1 - 1) / (10 - 1)) + 1
        print(f'user def speed = {speed}, global speed = {self.global_speed}')
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
        self.pen = pen

        # start the bot listening and drawing threads
        listener_thread = Thread(target=self.listener)
        dobot_thread = Thread(target=self.dobot_control)

        listener_thread.start()
        dobot_thread.start()

    def listener(self):
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


    ######################
    # DRAWBOT CONTROLS
    ######################

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
        if self.pen:
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
        newy = ((((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175) + self.rnd(100)
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        newx = x + self.rnd(100)
        if newx <= 200 or newx >= 300:
            newx = 250

        # which mode
        if self.continuous_line:
            self.digibot.move_to(newx, newy, 0, r, True)
        else:
            self.digibot.jump_to(newx, newy, 0, r, True)

    def dobot_control(self):
        """Loop thread that controls the robot arm
        responses to the data generated by Nebula."""

        print("Started dobot control thread")
        self.digibot.go_position_draw()

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
                    # if getrandbits(1):
                    #     self.digibot.speed(velocity=((incoming_command * 10) + (self.global_speed * 10)) * 2,
                    #                        acceleration=((incoming_command * 10) + (self.global_speed * 10)) * 2
                    #                        )
                    # else:
                    #     self.digibot.speed(velocity=randrange(30, 200),
                    #                        acceleration=randrange(30, 200)
                    #                        )

                    (x, y, z, r, j1, j2, j3, j4) = self.digibot.pose()
                    logging.debug(f'Current position: x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

                    #
                    # LOW power response from AI Factory
                    #
                    if incoming_command < 2:
                        """do nothing"""
                        # self.move_y()
                        # self.digibot.dot()

                        logging.info('Emission < 2: PASS')
                        break

                    #
                    # HIGH power response from AI Factory
                    # moves to a new random place
                    #
                    elif incoming_command >= 8:
                        """move to a random x, y position"""
                        self.move_y_random()

                        # does this or that
                        # if getrandbits(1):
                        #     self.move_y_random()
                        #     logging.info('Emission >= 8: move Y random')
                        # else:
                            # self.move_y()
                        # self.digibot.arc(x + self.rnd(incoming_command) / 10,
                        #                  y + self.rnd(incoming_command) / 10,
                        #                  z, 0,
                        #                  x + self.rnd(incoming_command) / 10,
                        #                  y + self.rnd(incoming_command) / 10,
                        #                  z, 0,
                        #                  False)
                        logging.info('Emission >= 8: arc')

                    #
                    # MID power response
                    #
                    else:
                        """between 2 and 8 make shapes in situ"""
                        # randomly choose from the following c hoices
                        randchoice = randrange(6)
                        logging.debug(f'randchoice == {randchoice}')

                        # 0= line to somewhere
                        if randchoice == 0:
                            self.digibot.move_to(x + self.rnd(incoming_command),
                                                 y + self.rnd(incoming_command),
                                                 z, 0,
                                                 True)
                            logging.info('Emission 3-8: draw line')

                        # 1 = messy squiggles
                        if randchoice == 1:
                            squiggle_list = []
                            for n in range(randrange(2, 4)):
                                squiggle_list.append((randrange(-5, 5) / 10,
                                                      randrange(-5, 5) / 10,
                                                      randrange(-5, 5) / 10)
                                                     )
                            self.digibot.squiggle(squiggle_list)
                            logging.info('Emission 3-8: small squiggle')

                        # 2 = dot & line
                        elif randchoice == 2:
                            self.digibot.dot()
                            self.digibot.move_to(x + self.rnd(incoming_command),
                                                 y + self.rnd(incoming_command),
                                                 z, 0,
                                                 True)
                            logging.info('Emission 3-8: dot')

                        # 3 = note head
                        elif randchoice == 3:
                            note_size = randrange(5)
                            # note_shape = randrange(20)
                            self.digibot.note_head(size=note_size)
                            logging.info('Emission 3-8: note head')

                        # 4 = note head and line
                        elif randchoice == 4:
                            note_size = randrange(1, 10)
                            self.digibot.note_head(size=note_size)
                            self.digibot.move_to(x + self.rnd(incoming_command),
                                                 y + self.rnd(incoming_command),
                                                 z, 0,
                                                 True)
                            logging.info('Emission 3-8: note head and line')

                        # 5 = dot
                        elif randchoice == 5:
                            self.digibot.dot()
                            # self.move_y_random()
                            logging.info('Emission 3-8: dot and line')

                    # take a breath
                    # sleep(self.global_speed)

                # wait a bit until the new emission is different from current
            # self.move_y()
            sleep(0.1) # self.global_speed)

        logging.info('quitting dobot director thread')


if __name__ == "__main__":
    Main(duration_of_piece=380,
         continuous_line=False,
         speed=5,
         staves=1,
         pen=False)

