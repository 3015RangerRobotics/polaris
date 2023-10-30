from typing import List
import numpy as np
import numpy.typing
from wpimath.geometry import Pose3d, Translation3d, Rotation3d
import math

def openCVPoseToWPILib(tvec: np.typing.NDArray[np.float64], rvec: np.typing.NDArray[np.float64]) -> Pose3d:
    return Pose3d(
        Translation3d(tvec[2][0], -tvec[0][0], -tvec[1][0]),
        Rotation3d(
            numpy.array([rvec[2][0], -rvec[0][0], -rvec[1][0]]),
            math.sqrt(math.pow(rvec[0][0], 2) + math.pow(rvec[1][0], 2) + math.pow(rvec[2][0], 2))
        ))

def wpiLibTranslationToOpenCV(translation: Translation3d) -> List[float]:
    return [-translation.Y(), -translation.Z(), translation.X()]