# mb_1r2t_ros2 (Patched & Stable)

ROS 2 driver for the **MB-1R2T LiDAR** (Patched for firmware compatibility and `slam_toolbox` support).

This repository is a modified and stabilized fork based on [g0mb4/mb_1r2t_ros2](https://github.com/g0mb4/mb_1r2t_ros2). It has been heavily refactored to resolve serial data dropouts, firmware packet parsing issues, and scan size mismatches.

---

## 🛠️ Key Bug Fixes in this Fork

If you use the original driver, you will likely encounter serial crashes or mapping errors. This fork resolves them out-of-the-box:

1. **Firmware Packet Agnostic (Bitwise Check):** Fixed the `Unknown packet type` crash by replacing strict packet type validations with a dynamic bitwise check (`type & 0x01`). Works with all firmware versions (showing headers like `0x97`, `0x95`, `0x8F`, etc.).
2. **Robust Serial Read Loop:** Resolved data packet drops due to fragmented serial reads (*split-reads*). Implemented a POSIX-compliant blocking read loop with a 100ms timeout (`VTIME=1`) in `serial_device_linux.cpp`.
3. **Fixed-Binning LaserScan (720 Beams):** Projects variable points from physical rotation into exactly 720 fixed angular bins (0.5° resolution). This completely resolves the `LaserRangeScan contains X range readings, expected Y` rejection error in `slam_toolbox`.
4. **Real-time SLAM Parameter Updates:** Pre-configured `slam_toolbox_params.yaml` with travel thresholds set to `0.0`, allowing immediate real-time map updates even when the LiDAR is hand-rotated or static.

---

## 📋 Folder Structure

* **`config/`**: Contains the optimized parameter file `slam_toolbox_params.yaml` for SLAM mapping.
* **`include/`**: C++ header declarations (`mb_1r2t.hpp`, `serial_device_linux.hpp`).
* **`launch/`**: Python launch scripts (`start.launch.py`, `rviz.launch.py`, `slam_toolbox.launch.py`).
* **`rviz/`**: Pre-configured RViz visualization file.
* **`src/`**: Driver source files.

---

## 🚀 Installation & Building

Make sure you are in a ROS 2 Foxy or Humble environment on WSL2 (Ubuntu) or native Linux.

1. **Create/Open your ROS 2 Workspace:**
   ```bash
   mkdir -p ~/ros2_ws/src
   cd ~/ros2_ws/src
   ```

2. **Clone this repository:**
   ```bash
   git clone <YOUR_GITHUB_FORK_URL> mb_1r2t_ros2
   ```

3. **Build the package:**
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select mb_1r2t
   ```

4. **Source the workspace:**
   ```bash
   source ~/ros2_ws/install/setup.bash
   ```

---

## 💻 Usage & Launch Instructions

### 1. Run LiDAR Node Only
Launches the raw driver node publishing `/laser_scan` and `/point_cloud`:
```bash
ros2 launch mb_1r2t start.launch.py
```
*   **Default port:** `/dev/ttyUSB0` (can be changed in the launch file).
*   **Default frame:** `lidar`.

### 2. Run LiDAR Node with RViz2
Starts the driver and opens the pre-configured RViz2 GUI:
```bash
ros2 launch mb_1r2t rviz.launch.py
```

### 3. Run SLAM 2D Mapping (slam_toolbox)
Runs the LiDAR driver, publishes static TFs (`odom` -> `base_link` -> `lidar`), and starts the `slam_toolbox` node for real-time room mapping:
```bash
# Terminal 1: Launch SLAM
ros2 launch mb_1r2t slam_toolbox.launch.py
```

### 4. Connect to Foxglove Studio
To visualize the mapping progress on Foxglove Studio, start the WebSocket Bridge:
```bash
# Terminal 2: Start Websocket Bridge
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

#### Foxglove Configuration:
1. Open **Foxglove Studio** on your host PC.
2. Select **Rosbridge** connection mode and connect to: `ws://localhost:9090` (or your WSL IP).
3. In the 3D Panel:
   * Change **Custom Frame** to: **`map`** (press Enter).
   * Check the `/map` and `/laser_scan` topics in the list.

### 5. Save the Generated Map
Once mapping is complete, save your map:
```bash
# Terminal 3: Save Map
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/map_ruangan
```

---

## 📊 Node Interfaces

### Published Topics
* `/laser_scan` (`sensor_msgs/msg/LaserScan`): The filtered 720-beam scan data.
* `/point_cloud` (`sensor_msgs/msg/PointCloud`): The raw 3D point cloud of the environment.

### Frame Tree
When running SLAM, the TF tree is organized as follows:
`map` ➔ `odom` ➔ `base_link` ➔ `lidar`
