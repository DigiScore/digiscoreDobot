from PyQt5.QtCore import QObject, pyqtSignal

# set up signal based emitter for harmony telemetry
class GotMusicSignal(QObject):
    harmony_str = pyqtSignal(object)

    def __init__(self):
        super(GotMusicSignal, self).__init__()