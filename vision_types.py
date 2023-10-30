from dataclasses import dataclass
from typing import List, Union
import numpy as np
import numpy.typing
from wpimath.geometry import Pose3d

@dataclass(frozen=True)
class TagImageObservation:
    tag_id: int
    corners: np.typing.NDArray[np.float64]

@dataclass(frozen=True)
class TagPoseObservation:
    tag_id: int
    tvec_0: np.typing.NDArray[np.float64]
    rvec_0: np.typing.NDArray[np.float64]
    error_0: float
    tvec_1: np.typing.NDArray[np.float64]
    rvec_1: np.typing.NDArray[np.float64]
    error_1: float

@dataclass(frozen=True)
class CameraPoseObservation:
    pose_0: Pose3d
    error_0: float
    pose_1: Union[Pose3d, None]
    error_1: Union[float, None]
    tag_ids: List[int]
