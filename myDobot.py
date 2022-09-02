import pydobot
from .message import Message
from .enums import PTPMode
from .enums.CommunicationProtocolIDs import CommunicationProtocolIDs
from .enums.ControlValues import ControlValues


class MyDobot(pydobot):
    def __init__(self):
        pass

    def arc_to(self, x, y, z, r, wait=False):
        self._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ, wait=wait)