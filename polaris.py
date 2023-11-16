import sys
import time

import cv2
import ntcore

from config.config import ConfigStore, LocalConfig, RemoteConfig
from config.ConfigSource import ConfigSource, FileConfigSource, NTConfigSource
from output.OutputPublisher import NT4OutputPublisher, OutputPublisher
from output.overlay_util import *
from output.StreamServer import MjpegServer
from pipeline.CameraPoseEstimator import MultiTargetCameraPoseEstimator
from pipeline.Capture import GStreamerCapture, DefaultCapture
from pipeline.TagDetector import ArucoTagDetector

def main():
    config = ConfigStore(LocalConfig(), RemoteConfig())
    local_config_source: ConfigSource = FileConfigSource()
    remote_config_source: ConfigSource = NTConfigSource()

    capture = GStreamerCapture()
    tag_detector = ArucoTagDetector(cv2.aruco.DICT_APRILTAG_16h5) # TODO: Change to 36h11 for 2024
    pose_estimator = MultiTargetCameraPoseEstimator()
    output_publisher: OutputPublisher = NT4OutputPublisher()
    stream_server = MjpegServer()

    local_config_source.update(config)

    if not config.local_config.has_calibration:
        print('No calibration found')
        exit(1)

    ntcore.NetworkTableInstance.getDefault().setServer(config.local_config.server_ip)
    ntcore.NetworkTableInstance.getDefault().startClient4(config.local_config.device_id)
    stream_server.start(config)

    frame_count = 0
    last_print = 0

    while True:
        remote_config_source.update(config)
        timestamp = time.time()
        success, image = capture.get_frame(config)

        if not success:
            time.sleep(0.5)
            continue

        fps = None
        frame_count += 1
        if time.time() - last_print > 1:
            last_print = time.time()
            fps = frame_count
            print('Running at', frame_count, 'fps')
            frame_count = 0

        image_observations = tag_detector.detect_tags(image, config)
        pose_observation = pose_estimator.solve_camera_pose(image_observations, config)

        for obs in image_observations:
            overlay_image_observation(image, obs)

        output_publisher.send(config, timestamp, pose_observation, fps)

        stream_server.set_frame(image)


if __name__ == '__main__':
    main()