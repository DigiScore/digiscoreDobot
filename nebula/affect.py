# install python libraries
from random import randrange
from time import time
from dataclasses import fields
from random import random
from time import sleep

# install Nebula modules
from nebula.nebula_dataclass import NebulaDataClass


class Affect:
    """Accepts realtime data/ percept input from
    human-in-the-loop e.g. live audio analysis,
    skeletal tracking, joystick control.
    By analysing the energy of input this class will
    define which feed of the datadict
    (produced by the AI factory) to emit back to the client.
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
        self.affect_logging = False
        self.running = True

        # own the dataclass
        self.datadict = datadict

        # Emission list is the highest level comms back to client
        # self.emission_list = []
        self.live_emission_data = 0.0

        # little val for emission control avoiding repeated vals (see below)
        self.old_val = 0

    def listener(self):
        """Listens to the realtime incoming signal that is stored in the dataclass ("user_input")
        and calculates an affectual response based on general boundaries:
            HIGH - if input stream is LOUD (0.8+) then emit, smash a random fill and break out to Daddy cycle...
            MEDIUM - if input energy is 0.3-0.8 then emit, a jump out of child loop
            LOW - nothing happens, continues with cycles
        """
        # 1. daddy cycle: top level cycle lasting 6-26 seconds
        while self.running:
            # flag for breaking on big affect signal
            self.interrupt_bang = True

            # Top level calc master cycle before a change
            master_cycle = randrange(600, 2600) / 100  # * self.global_speed
            loop_end = time() + master_cycle

            if self.affect_logging:
                print('\t\t\t\t\t\t\t\t=========AFFECT - Daddy cycle started ===========')
                print(f"                 interrupt_listener: started! Duration =  {master_cycle} seconds")

            # 2. child cycle: waiting for interrupt  from master clock
            while time() < loop_end:
                # if a major break out then go to Daddy cycle and restart
                if not self.interrupt_bang:
                    break

                if self.affect_logging:
                    print('\t\t\t\t\t\t\t\t=========Hello - child cycle 1 started ===========')

                # randomly pick an input stream for this cycle
                # either user_in, random, net generation or self-awareness
                rnd = randrange(4)
                self.rnd_stream = self.affectnames[rnd]
                setattr(self.datadict, 'affect_decision', self.rnd_stream)
                if self.affect_logging:
                    print(f'Random stream choice = {self.rnd_stream}')

                # hold this stream for 1-4 secs, unless interrupt bang
                end_time = time() + (randrange(1000, 4000) / 1000)
                if self.affect_logging:
                    print('end time = ', end_time)

                # 3. baby cycle - own time loops
                while time() < end_time:
                    if self.affect_logging:
                        print('\t\t\t\t\t\t\t\t=========Hello - baby cycle 2 ===========')

                    # make the master output the current value of the affect stream
                    # 1. go get the current value from dict
                    affect_listen = getattr(self.datadict, self.rnd_stream)
                    if self.affect_logging:
                        print(f'Affect stream current input value from {self.rnd_stream} == {affect_listen}')

                    # 2. send to Master Output
                    setattr(self.datadict, 'master_output', affect_listen)
                    if self.affect_logging:
                        print(f'\t\t ==============  master move output = {affect_listen}')

                    # 3. emit to the client at various points in the affect cycle
                    self.emitter(affect_listen)

                    ###############################################
                    #
                    # test realtime input against the affect matrix
                    # behave as required
                    #
                    ###############################################

                    # 1. get current mic level
                    peak = getattr(self.datadict, "user_in")
                    if self.affect_logging:
                        print('testing current mic level for affect = ', peak)

                    # 2. calc affect on behaviour
                    # LOUD
                    # if input stream is LOUD then smash a random fill and break out to Daddy cycle...
                    if peak > 0.8:
                        if self.affect_logging:
                            print('interrupt > HIGH !!!!!!!!!')

                        # A - refill dict with random
                        self.random_dict_fill()

                        # B - jumps out of this loop into daddy
                        self.interrupt_bang = False

                        # C break out of this loop, and next (cos of flag)
                        break

                    # MEDIUM
                    # if middle loud fill dict with random, all processes norm
                    elif 0.3 < peak < 0.8:
                        if self.affect_logging:
                            print('interrupt MIDDLE -----------')

                        # A. jumps out of current local loop, but not main one
                        break

                    # LOW
                    # nothing happens here
                    elif peak <= 0.3:
                        if self.affect_logging:
                            print('interrupt LOW ----------- no action')

                    # get current rhythm_rate from datadict
                    rhythm_rate = getattr(self.datadict, 'rhythm_rate')

                    # and wait for a cycle
                    sleep(rhythm_rate)

    def emitter(self, incoming_affect_listen):
        if incoming_affect_listen != self.old_val:
            # self.emission_list.append(incoming_affect_listen)
            self.live_emission_data = incoming_affect_listen
            # if self.affect_logging:
            print(f'//////////////////                   EMITTING value {self.live_emission_data}')
        self.old_val = incoming_affect_listen

    def random_dict_fill(self):
        """Fills the working dataclass with random values. Generally called when
        affect energy is highest"""
        for field in fields(self.datadict):
            # print(field.name)
            rnd = random()
            setattr(self.datadict, field.name, rnd)
        if self.affect_logging:
            print(f'Data dict new random values are = {self.datadict}')

    def quit(self):
        self.running = False
