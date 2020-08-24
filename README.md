# detracon

## Installation

- Build docker image `docker build -t detracon .` or pull docker image `docker pull levan92/detracon`
- Run docker image with mapped volume for code dev as`start_docker.sh`

## Usage

- Edit `.env` accordingly
- Run ` python3 run.py`
  - add flags: 
    - `--nodisplay` to not display
    - `time` to time

## Explanation

- The Object detection utilises the Detectron2 framework, model is a Faster-RCNN with FPN (Resnet50 backbone).
- Multi-object tracking done with DeepSort
- Control system/PID system is implemented with `simple_pid` Python module. This repo assumes a Hikvision Pan-Tilt-Zoom camera that can be controlled with the `hikvisionapi` Python API.
  
- We want to move the PTZ camera to make sure the selected bounding box in the middle of the frame at a suitable zoom level (aka zoom in when it is too small/far)
- To select a bounding box, mouse left click within the bounding box on the `cv2.imshow` window. To deselect, click anywhere without a box.
- Manual override is possible by using the additional `tkinter` UI buttons that will appear if ran in display mode.
