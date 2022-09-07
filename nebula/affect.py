# install python libraries
from random import randrange
from time import time
from dataclasses import fields
from random import random
from time import sleep

# install Nebula modules
from old_nebula.nebula_dataclass import NebulaDataClass


class Affect:
    """Accepts realtime data/ percept input from
    human-in-the-loop e.g. live audio analysis,
    skeletal tracking, joystick control.
    By analysing the energy of input this class will
    define which feed of the datadict
    (produced by the AI actory) to emit back to the client.
    Like a thought train it is affected by the energy of a
    percept, and duration of such listening."""

    def __init__(self,
                 datadict: NebulaDataClass
                 ):

        print('Starting the Affect module')

        # names for affect listening
        self.affectnames = ['user_in',
                            'rnd_poetry',
                            'affect_net',
                            'self_awareness']

        # set running vars
        self.affect_logging = True
        self.running = True

        # own the dataclass
        self.datadict = datadict

        # Emission list is the highest level comms back to client
        self.emission_list = []

        # little val for emission control avoiding repeated vals (see below)
        self.old_val = 0

    def listener(self):
        """Listens to the realtime incoming signal that is stored in the dataclass ("user_input")
        and calculates an affectual response based on general bounderies:
            HIGH - if input stream is LOUD (0.8+) then emit, smash a random fill and break out to Daddy cycle...
            MEDIUM - if input energy is 0.3-0.8 then emit, a jump out of child loop
            LOW - nothing happens, continues with cycles
        """
        # 1. daddy cycle: top level cycle lasting 6-26 seconds
        while self.running:
            if self.affect_logging:
                print('\t\t\t\t\t\t\t\t=========AFFECT - Daddy cycle started ===========')

            # flag for breaking on big affect signal
            self.interrupt_bang = True

            # Top level calc master cycle before a change
            master_cycle = randrange(6, 26)  # * self.global_speed
            loop_end = time() + master_cycle

            if self.affect_logging:
                print(f"                 interrupt_listener: started! sleeping now for {master_cycle}...")

            # refill the dicts
            self.random_dict_fill()

            # 2. child cycle: waiting for interrupt  from master clock
            while time() < loop_end:
                if self.affect_logging:
                    print('\t\t\t\t\t\t\t\t=========Hello - child cycle 1 started ===========')

                # if a major break out then go to Daddy cycle
                if not self.interrupt_bang:
                    break

                # randomly pick an input stream for this cycle
                # either user_in, random, net generation or self-awareness
                rnd = randrange(4)
                self.rnd_stream = self.affectnames[rnd]
                setattr(self.datadict, 'affect_decision', self.rnd_stream)
                if self.affect_logging:
                    print(self.rnd_stream)

                # hold this stream for 1-4 secs, unless interrupt bang
                end_time = time() + (randrange(1000, 4000) / 1000)
                if self.affect_logging:
                    print('end time = ', end_time)

                # baby cycle 2 - own time loops
                while time() < end_time:
                    # get current mic level
                    peak = getattr(self.datadict, "user_in")
                    # print('mic level = ', peak)

                    if self.affect_logging:
                        print('\t\t\t\t\t\t\t\t=========Hello - baby cycle 2 ===========')

                    # go get the current value from dict
                    affect_listen = getattr(self.datadict, self.rnd_stream)
                    if self.affect_logging:
                        print('current value =', affect_listen)

                    # make the master output the current value of the affect stream
                    setattr(self.datadict, 'master_output', affect_listen)
                    if self.affect_logging:
                        print(f'\t\t ==============  master move output = {affect_listen}')

                    # emit to the client at various points in the affect cycle
                    # self.emitter(affect_listen)

                    # calc affect on behaviour
                    # LOUD
                    # if input stream is LOUD then smash a random fill and break out to Daddy cycle...
                    if peak > 0.8:
                        if self.affect_logging:
                            print('interrupt > HIGH !!!!!!!!!')

                        # A - refill dict with random
                        self.random_dict_fill()

                        # emit at various points in the affect cycle
                        self.emitter(affect_listen)

                        # B - jumps out of this loop into daddy
                        self.interrupt_bang = False
                        if self.affect_logging:
                            print('interrupt bang = ', self.interrupt_bang)

                        # C break out of this loop, and next (cos of flag)
                        break

                    # MEDIUM
                    # if middle loud fill dict with random, all processes norm
                    elif 0.3 < peak < 0.8:
                        if self.affect_logging:
                            print('interrupt MIDDLE -----------')
                            print('interrupt bang = ', self.interrupt_bang)

                        # emit at various points in the affect cycle
                        self.emitter(affect_listen)

                        # jumps out of current local loop, but not main one
                        break

                    # LOW
                    # nothing happens here
                    elif peak <= 0.3:
                        pass

                    # get current rhythm_rate from datadict
                    rhythm_rate = getattr(self.datadict, 'rhythm_rate')

                    # and wait for a cycle
                    sleep(rhythm_rate)

    def emitter(self, incoming_affect_listen):
        if incoming_affect_listen != self.old_val:
            self.emission_list.append(incoming_affect_listen)
            print(f'//////////////////                   EMITTING value {incoming_affect_listen}')
        self.old_val = incoming_affect_listen

    def random_dict_fill(self):
        """Fills the working dataclass with random values. Generally called when
        affect energy is highest"""
        for field in fields(self.datadict):
            # print(field.name)
            rnd = random()
            setattr(self.datadict, field.name, rnd)
        print(f'Data dict new random values are = {self.datadict}')

    def quit(self):
        self.running = False
