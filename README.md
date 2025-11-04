# Robot Calibrator & Localization System

A multi-sensor robot localization and mapping system that combines LIDAR-based SLAM with AprilTag vision-based positioning using Kalman filter sensor fusion.

## Video Demonstration

https://github.com/user-attachments/assets/your-video-file.mp4

The video demonstrates the core SLAM (Simultaneous Localization and Mapping) functionality using RPLidar A1. Watch as the system:

- Builds a real-time 2D occupancy grid map of the environment
- Tracks the robot's position and orientation as it moves
- Updates the map continuously with LIDAR scan data
- Uses RMHC-SLAM algorithm for accurate localization and mapping

The SLAM system processes 360-degree LIDAR scans at high frequency, interpolating distance measurements and updating both the robot's estimated position and the environment map simultaneously.

## Overview

This project provides a comprehensive solution for robot localization and mapping in indoor environments. It integrates:

- **LIDAR SLAM**: Real-time mapping using RPLidar A1 with BreezySLAM's RMHC-SLAM algorithm
- **AprilTag Vision**: Visual localization using AprilTag fiducial markers
- **Sensor Fusion**: Kalman filter-based position extrapolation combining LIDAR and vision data
- **Map Annotation**: Interactive tool for marking obstacles on generated maps

## Features

- Real-time robot position tracking with multiple sensor inputs
- Automatic AprilTag detection and field mapping
- Interactive map visualization with matplotlib
- Graceful shutdown with automatic data persistence
- Map obstacle annotation tool for post-processing
- Position estimation optimization using weighted averaging

## System Requirements

- Python
  .8+
- RPLidar A1 (or compatible) connected via USB
- Camera with calibrated intrinsic parame
  ers
- AprilTag markers (170mm size by default)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd calibrator
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Dependencies

- `breezyslam` - SLAM algorithms
- `opencv-python` - Computer vision and image processing
- `rplidar-roboticia` - RPLidar driver
- `matplotlib` - Real-time visualization
- `numpy` - Numerical computing
- `scipy` - Scientific computing utilities
- `pyapriltags` - AprilTag detection
- `filterpy` - Kalman filter implementation
- `pydantic` - Data validation
- `pygame` - Additional visualization support

## Project Structure

```
calibrator/
├── src/
│   ├── camera/
│   │   ├── april_tags_vault.py    # AprilTag position tracking
│   │   └── detector.py             # AprilTag detection wrapper
│   ├── lidar/
│   │   ├── rp_lidar.py             # RPLidar sensor wrapper
│   │   └── slam.py                 # SLAM implementation
│   ├── position/
│   │   └── position_extrapolator.py # Kalman filter sensor fusion
│   ├── serialize/
│   │   └── serializable_tag_position.py # Data serialization
│   ├── util/
│   │   ├── math.py                 # Math utilities
│   │   ├── position.py             # Position data structures
│   │   └── visual.py               # Visualization utilities
│   ├── map_area.py                 # Main localization application
│   └── annotate_map_obstacles.py   # Map annotation tool
├── out/                            # Output directory for maps and data
├── BreezySLAM/                     # SLAM libra
y
└── requirements.txt
```

## Usage

### 1. Main Localization System

Run the main localization and mapping application:

```bash
python src/map_area.py
```

**Optional arguments:**

- `--tag_positions
file`: Path to save AprilTag positions (default: `out/tag_positions.json`)
- `--map_output_file`: Path to save the generated map (def
  ult: `out/map.npy`)

Example with custom output:

```bash
python src/map_area.py --tag_positions_file out/my_tags.json --map_output_file out/my_map.npy
```

**Visualization Legend:**

- **Red**: LIDAR-based SLAM po
  ition
- **Green**: Kalman filter fused position estimate
- **Blue**: Detected AprilTag positions (with tag IDs)

**Exiting:**
Press `Ctrl+C` to gracefully stop the system. This will:

- Save AprilTag positions to JSON
- Save the generated map as a numpy array
- Clean up camera and LIDAR res
  urces

### 2. Map Annotation Tool

After generating a map, use the annotation tool to mark obstacles:

```bash
python src/annotate_map_obstacles.p

```

The tool will prompt you for:

1. Path to your map image
2. Square size in meters (physical world dimension)
3. Grid size in pixels (for annotation grid overlay)

**Controls:**

- **Click and drag**: Toggle obstacle squares
- **S key**: Save annotations and exit
- **Q key**: Quit without saving

Annotations are saved to `out/<image_name>_annotations.json`.

## Configuration

### Camera Calibration

Update the camera matrix and distortion coefficients in `src/map_area.py`:

```python
CAMERA_MATRIX = np.array([
    [911.88759056, 0.0, 673.31511011],
    [0.0, 916.14445514, 344.03396501],
    [0.0, 0.0, 1.0],
])

DIST_COEFF = np.array([
    -3.34931101e-01, 1.13339771e-01, 3.11012641e-04,
    4.06954011e-04, -1.49774804e-02
])
```

### LIDAR Configuration

Adjust LIDAR connection settings:

```python
port = "/dev/cu.usbserial-110"  # Update for your system
baudrate = 256000
```

### Map Parameters

Configure map dimensions and AprilTag size:

```python
tag_size = 0.17              # AprilTag size in meters
map_size_pixels = 800        # Map resolution in pixels
map_size_meters = 30         # Physical map size in meters
```

### SLAM Parameters

Tune SLAM algorithm parameters:

```python
SLAM = RMHC_SLAM(
    RPLidarA1(),
    map_size_pixels,
    map_size_meters,
    map_quality=1,
    hole_width_mm=300,
    random_seed=42,
    max_search_iter=1000,
)
```

## How It Works

### Sensor Fusion Pipeline

1. **LIDAR SLAM**: RPLidar continuously scans the environment, building a 2D occupancy grid map and estimating the robot's position
2. **AprilTag Detection**: Camera detects AprilTag markers and estimates their 3D pose relative to the camera
3. **Tag Mapping**: Detected tags are mapped to global coordinates using SLAM position estimates
4. **Position Fusion**: Kalman filter fuses LIDAR and AprilTag measurements to produce optimal po
   ition estimates
5. **Visualization**: Real-time display shows the map, robot position, and detected tags

### Data Structures

**Position2D**: Represents 2D position with ori
ntation

- `x`, `y`: Position coordinates
- `sin`, `cos`: Orientation as unit vector
- `vx`, `vy`: Optional velocity components

**Sensor**: Wraps position measurem
nts with metadata

- `position`: Position2D measurement
- `type
  : Sensor type (LIDAR, AprilTag, MU)
- `noise_matrix`: Measurement covarian e

## Output iles

### Tag Positions JSON

Contains estimat d global positions of al
detected AprilTags:

```json
{
  "tags": {
    "1": { "x": 5.2, "y": 3.1, "sin": 0.0, "cos": 0.0 },
    "2": { "x": 8.7, "y": 6.4, "sin": 0.707, "cos": 0.707 }
  }
}
```

### Map NPY

Binary numpy array containing the occupancy grid map (grayscale, 0-255).

### Annotation JSON

Contains o stacle informat on for a notated maps:

``json
{
"image_path": "map.png",
"square_size_meters": 0.5,
"grid_size_pixels": 50,

"pixels_per_meter": 100.0,
"obstacles": [
{ "x": 10, "y": 5 },
{ "x": 11, "y": 5 }
]
}

```

## Troubleshooting

### LIDAR Connection Issues

If the LIDAR fails to connect:

1. Check the USB connection and port name
2. Verify baudrate matches your device (typically 115200 or 256000)
3. Ensure no other process is using the serial p
rt
4. Try unplugging and reconnecting the device

The system automatically retries connection if initial attempts fail.

### Camera Issues

If camera/AprilTag detection isn't working:

1. Verify camera is connected and accessible
2. Check c
mera calibration parameters are correct
3. Ensure adequate lighting for tag detection
4. Verify AprilTag size matches configuration

### Performance Issues

If the system runs slowly:

1. Reduce `map_size_pixels` for faster SLAM
2. Lower camera resolution in detec
or initialization
3. Reduce `nthreads` for AprilTag detector if CPU limited
4. Increase `update_interval` in the main loop

## Contributing

When contributing to this project, please:

1. Follow the existing code style
2. Add docstrings to new functions and classes
3. Update this README if adding new features
4. Test with actual hardware when possible

## License

See LICENSE.md for details.

## Acknowledgments

- [BreezySLAM](https://github.com/simondlevy/BreezySLAM) - SLAM library
- [RPLidar Python Library](https://github.com/Roboticia/RPLidar) - LIDAR driver
- [PyAprilTags](https://github.com/AprilRobotics/apriltag) - AprilTag detection
- [FilterPy](https://github.com/rlabbe/filterpy) - Kalman filtering
```
