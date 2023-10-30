from typing import Union
import cv2
import numpy as np
from config.config import ConfigStore
from vision_types import TagImageObservation, TagPoseObservation


class PoseEstimator:
    def solve_tag_pose(self, image_observation: TagImageObservation, config_store: ConfigStore) -> Union[TagPoseObservation, None]:
        raise NotImplementedError


class SquareTargetPoseEstimator(PoseEstimator):
    def solve_tag_pose(self, image_observation: TagImageObservation, config_store: ConfigStore) -> Union[TagPoseObservation, None]:
        tag_size = config_store.remote_config.tag_size_m
        object_points = np.array([[-tag_size / 2.0, tag_size / 2.0, 0.0],
                                  [tag_size / 2.0, tag_size / 2.0, 0.0],
                                  [tag_size / 2.0, -tag_size / 2.0, 0.0],
                                  [-tag_size / 2.0, -tag_size / 2.0, 0.0]])

        try:
            _, rvecs, tvecs, errors = cv2.solvePnPGeneric(object_points, image_observation.corners,
                                                          config_store.local_config.camera_matrix,
                                                          config_store.local_config.distortion_coefficients,
                                                          flags=cv2.SOLVEPNP_IPPE_SQUARE)
        except:
            return None
        return TagPoseObservation(image_observation.tag_id, tvecs[0], rvecs[0], errors[0][0], tvecs[1], rvecs[1], errors[1][0])
