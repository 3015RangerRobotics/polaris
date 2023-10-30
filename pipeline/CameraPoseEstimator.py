from typing import List, Union

import cv2
import numpy as np
from config.config import ConfigStore
from vision_types import CameraPoseObservation, TagImageObservation
from wpimath.geometry import *

from pipeline.coordinate_systems import (openCVPoseToWPILib,
                                         wpiLibTranslationToOpenCV)


class CameraPoseEstimator:
    def solve_camera_pose(self, image_observations: List[TagImageObservation], config_store: ConfigStore) -> Union[CameraPoseObservation, None]:
        raise NotImplementedError


class MultiTargetCameraPoseEstimator(CameraPoseEstimator):
    def solve_camera_pose(self, image_observations: List[TagImageObservation], config_store: ConfigStore) -> Union[CameraPoseObservation, None]:
        # Exit if no tag layout available
        if config_store.remote_config.tag_layout is None:
            return None

        # Exit if no observations available
        if len(image_observations) == 0:
            return None

        # Create set of object and image points
        tag_size = config_store.remote_config.tag_size_m
        object_points = []
        image_points = []
        tag_ids = []
        tag_poses = []
        for observation in image_observations:
            tag_pose = None
            for tag_data in config_store.remote_config.tag_layout['tags']:
                if tag_data['ID'] == observation.tag_id:
                    tag_pose = Pose3d(
                        Translation3d(
                            tag_data['pose']['translation']['x'],
                            tag_data['pose']['translation']['y'],
                            tag_data['pose']['translation']['z']
                        ),
                        Rotation3d(Quaternion(
                            tag_data['pose']['rotation']['quaternion']['W'],
                            tag_data['pose']['rotation']['quaternion']['X'],
                            tag_data['pose']['rotation']['quaternion']['Y'],
                            tag_data['pose']['rotation']['quaternion']['Z']
                        )))
            if tag_pose is not None:
                # Add object points by transforming from the tag center
                corner_0 = tag_pose + Transform3d(Translation3d(0, tag_size / 2.0, -tag_size / 2.0), Rotation3d())
                corner_1 = tag_pose + Transform3d(Translation3d(0, -tag_size / 2.0, -tag_size / 2.0), Rotation3d())
                corner_2 = tag_pose + Transform3d(Translation3d(0, -tag_size / 2.0, tag_size / 2.0), Rotation3d())
                corner_3 = tag_pose + Transform3d(Translation3d(0, tag_size / 2.0, tag_size / 2.0), Rotation3d())
                object_points += [
                    wpiLibTranslationToOpenCV(corner_0.translation()),
                    wpiLibTranslationToOpenCV(corner_1.translation()),
                    wpiLibTranslationToOpenCV(corner_2.translation()),
                    wpiLibTranslationToOpenCV(corner_3.translation())
                ]

                # Add image points from observation
                image_points += [
                    [observation.corners[0][0][0], observation.corners[0][0][1]],
                    [observation.corners[0][1][0], observation.corners[0][1][1]],
                    [observation.corners[0][2][0], observation.corners[0][2][1]],
                    [observation.corners[0][3][0], observation.corners[0][3][1]]
                ]

                # Add tag ID and pose
                tag_ids.append(observation.tag_id)
                tag_poses.append(tag_pose)

        # Single tag, return two poses
        if len(tag_ids) == 1:
            object_points = np.array([[-tag_size / 2.0, tag_size / 2.0, 0.0],
                                      [tag_size / 2.0, tag_size / 2.0, 0.0],
                                      [tag_size / 2.0, -tag_size / 2.0, 0.0],
                                      [-tag_size / 2.0, -tag_size / 2.0, 0.0]])
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(object_points, np.array(image_points),
                                                              config_store.local_config.camera_matrix,
                                                              config_store.local_config.distortion_coefficients,
                                                              flags=cv2.SOLVEPNP_IPPE_SQUARE)
            except:
                return None

            # Calculate WPILib camera poses
            field_to_tag_pose = tag_poses[0]
            camera_to_tag_pose_0 = openCVPoseToWPILib(tvecs[0], rvecs[0])
            camera_to_tag_pose_1 = openCVPoseToWPILib(tvecs[1], rvecs[1])
            camera_to_tag_0 = Transform3d(camera_to_tag_pose_0.translation(), camera_to_tag_pose_0.rotation())
            camera_to_tag_1 = Transform3d(camera_to_tag_pose_1.translation(), camera_to_tag_pose_1.rotation())
            field_to_camera_0 = field_to_tag_pose.transformBy(camera_to_tag_0.inverse())
            field_to_camera_1 = field_to_tag_pose.transformBy(camera_to_tag_1.inverse())
            field_to_camera_pose_0 = Pose3d(field_to_camera_0.translation(), field_to_camera_0.rotation())
            field_to_camera_pose_1 = Pose3d(field_to_camera_1.translation(), field_to_camera_1.rotation())

            # Return result
            return CameraPoseObservation(field_to_camera_pose_0, errors[0][0], field_to_camera_pose_1, errors[1][0],
                                         tag_ids)

        # Multi-tag, return one pose
        else:
            # Run SolvePNP with all tags
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(np.array(object_points), np.array(image_points),
                                                              config_store.local_config.camera_matrix,
                                                              config_store.local_config.distortion_coefficients,
                                                              flags=cv2.SOLVEPNP_SQPNP)
            except:
                return None

            # Calculate WPILib camera pose
            camera_to_field_pose = openCVPoseToWPILib(tvecs[0], rvecs[0])
            camera_to_field = Transform3d(camera_to_field_pose.translation(), camera_to_field_pose.rotation())
            field_to_camera = camera_to_field.inverse()
            field_to_camera_pose = Pose3d(field_to_camera.translation(), field_to_camera.rotation())

            # Return result
            return CameraPoseObservation(field_to_camera_pose, errors[0][0], None, None, tag_ids)
