from BreezySLAM.python.breezyslam.sensors import Laser


class RPLidarA1(Laser):
    """
    A class for the SLAMTEC RPLidar A1
    """

    def __init__(self, detectionMargin=0, offsetMillimeters=0):
        Laser.__init__(self, 360, 5.5, 360, 12000, detectionMargin, offsetMillimeters)