from dataclasses import dataclass, fields
from random import random
from threading import Thread
# import tensorflow as tf


class NebulaDataEngine:
    """An AI engine that generates gestural thought trains.
        This is the soul of embodied musicking.

        args:
            speed: general tempo/ feel of Nebula's response (0.5 ~ moderate fast, 1 ~ moderato; 2 ~ presto)"""

    def __init__(self, speed=1):
        print('building engine server')

        # todo - global speed should be linked to bpm
        # Set global vars
        self.interrupt_bang = False
        self.global_speed = speed  # / 10
        self.rnd_stream = 0
        self.rhythm_rate = 1
        self.affect_listen = 0

        # logging on/off switches
        self.net_logging = False
        self.master_logging = False
        self.streaming_logging = False
        self.affect_logging = False

        # build the dataclass and fill with random number
        self.datadict = NebulaDataClass()
        print(f'Data dict initial values are = {self.datadict}')

        # Build the AI factory
        # self.AI_factory_build()



    # todo - build as a class where user only inputs the list of nets required
    def AI_factory_build(self):
        """Builds the individual neural nets that constitute the AI factory.
        This will need modifying if and when a new AI factory design is implemented.
        NB - the list of netnames will also need updating"""

        # instantiate nets as objects and make  models
        print('MoveRNN initialization')
        self.move_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_RNN_skeleton_data.nose.x.h5')
        print('AffectRNN initialization')
        self.affect_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_RNN_bitalino.h5')
        print('MoveAffectCONV2 initialization')
        self.move_affect_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5')
        print('AffectMoveCONV2 initialization')
        self.affect_move_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_affect-move.h5')
        print('MoveAffectCONV2 initialization')
        self.affect_perception = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5')

        # name list for nets that align to factory above
        self.netnames = ['move_rnn',
                         'affect_rnn',
                         'move_affect_conv2',
                         'affect_move_conv2',
                         'self_awareness',  # Net name for self-awareness
                         'master_output']  # input for self-awareness

    def random_dict_fill(self):
        """Fills the working dataclass with random values"""
        for field in fields(self.datadict):
            # print(field.name)
            rnd = random()
            setattr(self.datadict, field.name, rnd)
        print(f'Data dict new random values are = {self.datadict}')


class Affect:

    def __init__(self):
        # names for affect listening
        self.affectnames = ['user_in',
                            'rnd_poetry',
                            'affect_net',
                            'self_awareness']


@dataclass
class NebulaDataClass:
    """Dataclass containing all the data emissions
    and user input to and from Nebula"""

    move_rnn: float = random()
    """Net 1 raw emission"""

    affect_rnn: float = random()
    """Net 2 raw emission"""

    move_affect_conv2: float = random()
    """Net 3 raw emission"""

    affect_move_conv2: float = random()
    """Net 4 raw emission"""

    master_output: float = random()
    """Master output from the affect process"""

    user_in: float = random()
    """Percept input stream from client e.g. live mic level"""

    rnd_poetry: float = random()
    """Random stream to spice things up"""

    # affect_net: float = random()
    # """Net"""

    self_awareness: float = random()
    """Net that has some self awareness - ???"""

    affect_decision: float = random()
    """Current stream chosen by affect process"""

    rhythm_rate: float = 0.1
    """Internal clock/ rhythm sub division"""

