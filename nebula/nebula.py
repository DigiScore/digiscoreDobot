"""
Embodied AI Engine Prototype AKA "Nebula".
This object takes a live signal (such as body tracking,
or real-time sound analysis) and generates a response that
aims to be felt as co-creative. The response is a flow of
neural network emissions data packaged as a dictionary,
and is gestural over time. This, when plugged into a responding
script (such as a sound generator, or QT graphics) gives
the impression of the AI creating in-the-moment with the
human in-the-loop.

© Craig Vear 2022
cvear@dmu.ac.uk

Dedicated to Fabrizio Poltronieri
"""
# import python modules
from dataclasses import dataclass, fields
from random import random, randrange
from threading import Thread
import tensorflow as tf
import numpy as np
from time import sleep

# import Nebula modules
from old_nebula.ai_factory import AIFactory
from old_nebula.affect import Affect
from old_nebula.nebula_dataclass import NebulaDataClass

class Nebula:
    """Nebula is the core "director" of an AI factory.
     It generates data in response to incoming percpts
    from human-in-the-loop interactions, and responds
    in-the-moment to the gestural input of live data.
    There are 4 components:
        Nebula: as "director" it coordinates the overall
            operations of the AI Factory
        AIFactory: builds the neural nets that form the
            factory, coordinates data exchange,
            and liases with the common data dict
        NebulaDataClass: is the central dataclass that
            holds and shares all the  data exchanges
            in the AI factory
        Affect: receives the live percept input from
            the client and produces an affectual response
            to it's energy input, which in turn interferes
            with the data generation.

    Args:
        speed: general tempo/ feel of Nebula's response (0.5 ~ moderate fast, 1 ~ moderato; 2 ~ presto)"""

    def __init__(self, speed=1):
        print('building engine server')

        # Set global vars
        self.interrupt_bang = False
        self.rnd_stream = 0
        self.rhythm_rate = 1
        self.affect_listen = 0

        # build the dataclass and fill with random number
        self.datadict = NebulaDataClass()
        print(f'Data dict initial values are = {self.datadict}')

        # Build the AI factory and pass it the data dict
        self.AI_factory = AIFactory(self.datadict, speed)

        # Start affect listener
        self.affect = Affect(self.datadict)
        self.emission_list = self.affect.emission_list

    def director(self):
        """Starts the server/ AI threads
         and gets the data rolling."""
        print('Starting the Nebula Director')
        # declares all threads
        t1 = Thread(target=self.AI_factory.make_data)
        t2 = Thread(target=self.affect.listener)

        # assigns them a daemon
        t1.daemon = True

        # start them all
        t1.start()
        t2.start()

    #################################
    #
    # High Level I/O for the client
    # will generally be used in a server thread
    #
    #################################

    def user_emission(self):
        """High-level  # This list is highest level comms back to client """
        return self.emission_list

    def user_input(self, user_input_value: float):
        """High-level input from client usually from
        real-time percept.
        Must be normalised 0.0-1.0"""
        setattr(self.datadict, 'user_in', user_input_value)

    def terminate(self):
        self.affect.quit()
        self.AI_factory.quit()

if __name__ == '__main':
    test = Nebula()
    test.director()
    if len(test.emission_list) > 0:
        emission_val = test.emission_list.pop()
        print(emission_val)
    else:
        sleep(0.1)
        test.user_input(random())

