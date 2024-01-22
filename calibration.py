import datetime
import os
from typing import List
import cv2
import numpy as np
import json

CAMERA_ID = 0
CAMERA_WIDTH = 1600
CAMERA_HEIGHT = 1200

ARUCO_DICT = cv2.aruco.DICT_5X5_1000
BOARD_ROWS = 9
BOARD_COLS = 11
CHECKER_SIZE = 0.02
MARKER_SIZE = 0.015
OUTPUT_FILE = 'calibration.json'

class CalibrationSession:
    _all_charuco_corners: List[np.ndarray] = []
    _all_charuco_ids: List[np.ndarray] = []
    _imsize = None

    def __init__(self) -> None:
        self._aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        self._aruco_params = cv2.aruco.DetectorParameters()
        self._charuco_board = cv2.aruco.CharucoBoard((BOARD_COLS, BOARD_ROWS), CHECKER_SIZE, MARKER_SIZE, self._aruco_dict)
    
    def process_frame(self, image: cv2.Mat, save: bool) -> None:
        if self._imsize is None:
            self._imsize = (image.shape[0], image.shape[1])
        
        corners, ids, _ = cv2.aruco.detectMarkers(image, self._aruco_dict, parameters=self._aruco_params)
        if len(corners) > 0:
            cv2.aruco.drawDetectedMarkers(image, corners)

            retval, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(corners, ids, image, self._charuco_board)
            if retval:
                cv2.aruco.drawDetectedCornersCharuco(image, charuco_corners, charuco_ids)

                if save:
                    self._all_charuco_corners.append(charuco_corners)
                    self._all_charuco_ids.append(charuco_ids)
                    print('Saved calibration frame #' + str(len(self._all_charuco_corners)))
        elif save:
            print('No markers detected in image. Skipping frame.')
    
    def finish(self) -> None:
        if len(self._all_charuco_corners) == 0:
            print('No calibration data')
            return

        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        
        retval, camera_matrix, distortion_coefficients, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(self._all_charuco_corners, self._all_charuco_ids, self._charuco_board, self._imsize, None, None)

        if retval:
            jsonDict = {
                'calibration_date': str(datetime.datetime.now()),
                'img_size': self._imsize[::-1],
                'camera_matrix': camera_matrix.tolist(),
                'distortion_coefficients': distortion_coefficients.tolist(),
                'avg_reprojection_error': retval
            }
            jsonStr = json.dumps(jsonDict, indent=4)

            with open(OUTPUT_FILE, 'w') as output:
                output.write(jsonStr)
        else:
            print('Calibration failed')

def main():
    session = CalibrationSession()

    cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3) # On
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

    can_capture = True

    while True:
        retval, image = cap.read()

        if not retval:
            print('Failed to capture camera frame')
            break

        if retval:
            pressed_key = cv2.waitKey(5)

            if pressed_key == ord('q'):
                session.finish()
                break

            save = (pressed_key == 32) # Space bar
            session.process_frame(image, save)

            cv2.imshow('Calibration', image)

if __name__ == '__main__':
    main()
