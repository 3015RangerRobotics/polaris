from dataclasses import dataclass
import numpy as np
import numpy.typing


@dataclass
class LocalConfig:
    device_id: str = ''
    server_ip: str = ''
    stream_port: int = 8080
    has_calibration: bool = False
    camera_matrix: np.typing.NDArray[np.float64] = np.array([])
    distortion_coefficients: np.typing.NDArray[np.float64] = np.array([])

@dataclass
class RemoteConfig:
    camera_id: int = -1
    camera_resolution_width: int = 0
    camera_resolution_height: int = 0
    camera_auto_exposure: int = 0
    camera_exposure: int = 0
    camera_gain: int = 0
    tag_size_m: float = 0
    tag_layout: any = None

@dataclass
class ConfigStore:
    local_config: LocalConfig
    remote_config: RemoteConfig
