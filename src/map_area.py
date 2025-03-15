import cv2
from matplotlib import pyplot as plt
import numpy as np
import pyapriltags
from breezyslam.algorithms import RMHC_SLAM
from camera.april_tags_vault import AprilTagsVault, from_tags_detection_to_pos2d
from camera.detector import AprilTagDetector
from lidar.rp_lidar import RPLidarA1
from lidar.slam import RPLidarSLAM
from position.position_extrapolator import PositionExtrapolator, Sensor, SensorType
from serialize.serializable_tag_position import SerializableTagPositions
from util.math import get_position_on_map, get_position_pixels, to_tag_global_position
from util.position import Position2D
from util.visual import render_position
import time
import argparse
import signal


CAMERA_MATRIX = np.array(
    [
        [911.88759056, 0.0, 673.31511011],
        [0.0, 916.14445514, 344.03396501],
        [0.0, 0.0, 1.0],
    ]
)
DIST_COEFF = np.array(
    [-3.34931101e-01, 1.13339771e-01, 3.11012641e-04, 4.06954011e-04, -1.49774804e-02]
)
tag_size = 0.17
map_size_pixels = 800
map_size_meters = 30
port = "/dev/tty.usbserial-110"
baudrate = 256000

SLAM = RMHC_SLAM(
    RPLidarA1(),
    map_size_pixels,
    map_size_meters,
    map_quality=1,
    hole_width_mm=300,
    random_seed=42,
    max_search_iter=1000,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tag_positions_file", type=str, default="out/tag_positions.json"
    )
    args = parser.parse_args()

    is_stopped = False
    april_tag_vault = AprilTagsVault(optimize_every_n_tags=10)

    position_extrapolator = PositionExtrapolator(map_size_pixels, map_size_meters)

    slam = RPLidarSLAM(SLAM, port, baudrate, map_size_pixels, map_size_meters)
    slam.start()

    def on_tag_detected(detection: pyapriltags.Detection):
        nonlocal slam

        position_tag = april_tag_vault.get_estimated_tag_position(detection.tag_id)
        if position_tag is not None:
            position_tag_global = get_position_on_map(
                from_tags_detection_to_pos2d(detection), position_tag
            )
            position_extrapolator.predict()
            position_extrapolator.update(
                Sensor(position_tag_global, SensorType.APRILTAG, np.eye(6) * 0.1)
            )

        pos_slam = slam.get_position_meters()
        april_tag_vault.add_tag_on_field(
            to_tag_global_position(
                from_tags_detection_to_pos2d(detection),
                Position2D(0, 0, 0, 1),
                pos_slam,
                map_size_meters,
            ),
            detection.tag_id,
        )

    detector = AprilTagDetector(
        CAMERA_MATRIX,
        DIST_COEFF,
        on_tag_detected,
        tag_size,
        nthreads=4,
        resolution=(1280, 720),
    )
    detector.start()

    plt.figure(figsize=(10, 10))
    last_update_time = time.time()
    update_interval = 0.01

    def signal_handler(sig, frame):
        nonlocal is_stopped, detector, slam
        print("\nCtrl+C detected, saving and exiting...")
        is_stopped = True

        # Save tag positions
        with open(args.tag_positions_file, "w") as f:
            f.write(
                SerializableTagPositions.from_tag_positions(
                    april_tag_vault.get_all_estimated_tags(),
                    Position2D(map_size_meters / 2, map_size_meters / 2, 0, 1),
                ).model_dump_json(indent=4)
            )

        # Clean up resources
        detector.stop()
        slam.stop()
        plt.close("all")
        cv2.destroyAllWindows()
        exit(0)  # Force exit the program

    signal.signal(signal.SIGINT, signal_handler)

    while not is_stopped:
        current_time = time.time()
        if current_time - last_update_time >= update_interval:
            plt.clf()
            plt.imshow(slam.get_map(), cmap="gray")
            slam_pos = slam.get_position_meters()
            render_position(
                get_position_pixels(slam_pos, map_size_meters, map_size_pixels), "red"
            )
            position_extrapolator.predict()  # Add prediction step
            position_extrapolator.update(
                Sensor(slam_pos, SensorType.LIDAR, np.eye(6) * 0.01)
            )
            render_position(
                get_position_pixels(
                    position_extrapolator.get_position(),
                    map_size_meters,
                    map_size_pixels,
                ),
                "green",
            )

            for tag_id, tag_pos in april_tag_vault.get_all_estimated_tags().items():
                tag_pos_pixels = get_position_pixels(
                    tag_pos, map_size_meters, map_size_pixels
                )
                render_position(tag_pos_pixels, "blue")
                plt.text(tag_pos_pixels.x, tag_pos_pixels.y, str(tag_id), color="blue")

            plt.pause(0.001)
            last_update_time = current_time

        cv2.waitKey(1)  # Keep the window responsive


if __name__ == "__main__":
    main()
