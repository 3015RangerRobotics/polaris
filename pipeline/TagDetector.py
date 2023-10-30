from typing import List

import cv2
from config.config import ConfigStore
from vision_types import TagImageObservation


class TagDetector:
    def detect_tags(self, image: cv2.Mat, config_store: ConfigStore) -> List[TagImageObservation]:
        raise NotImplementedError


class ArucoTagDetector(TagDetector):
    def __init__(self, dictionary_id) -> None:
        self._aruco_dict = cv2.aruco.getPredefinedDictionary(dictionary_id)
        self._aruco_params = cv2.aruco.DetectorParameters()
        self._aruco_detector = cv2.aruco.ArucoDetector(self._aruco_dict, self._aruco_params)

    def detect_tags(self, image: cv2.Mat, config_store: ConfigStore) -> List[TagImageObservation]:
        corners, ids, _ = self._aruco_detector.detectMarkers(image)

        if len(corners) == 0:
            return []
        return [TagImageObservation(tag_id[0], corner) for tag_id, corner in zip(ids, corners)]