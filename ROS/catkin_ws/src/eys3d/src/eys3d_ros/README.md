# **eYs3D ROS SDK (eYsGlobe) dm_preview**

eYs3D dm_preview is a package for eYs3D Depth camera module.

----------
## Clone this project

Git clone this project to your ROS workspace src folder.

`git clone https://github.com/eYs3D/eys3d_ros.git`

----------

## Support platforms

* Support Linux x64 & ARM aarch64
* Tested on X86 PC and NVIDIA Jetson TX2, with Ubuntu 18.04 (GCC 7.5).  
* Currently only YX8062 camera module supports IMU function.  
* Support Cameras : G100Plus,G100,G62,G53,G50,R50,BMVM0S30A


----------

## Installation ROS Instructions

The following instructions are written for ROS Melodic on Ubuntu 18.04  

- Install [ROS Melodic][1] on Ubuntu 18.04 

- Install the dependency packages    

    `sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libgtk-3-dev libusb-dev`  

    `sudo apt-get install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev libjpeg9`  

----------

## Link libGL.so for TX1/TX2 compile bug (Optional)

  `sudo ln -sf /usr/lib/aarch64-linux-gnu/tegra/libGL.so /usr/lib/aarch64-linux-gnu/libGL.so`

----------

## Build dm_preview

`catkin_make`  

Currently, don't use catkin build, it won't copy `eYs3D_wrapper` to `CMAKE_LIBRARY_OUTPUT_DIRECTORY`.

----------

## Usage Instructions

1. Check serial no. in `multi_cameras.launch`
2. Launch
   
   `roslaunch dm_preview multi_cameras.launch`

 - **Published Topics**  

   The published topics differ according to the device and parameters. After running the above command, the following list of topics will be available.  
   
   (This is a partial list. For full one type rostopic list):  
   
    /dm_preview/depth/camera_info  
    
    /dm_preview/depth/image_raw  
    
    /dm_preview/left/camera_info  
    
    /dm_preview/left/image_color  
    
    /dm_preview/right/camera_info  
    
    /dm_preview/right/image_color  
    
    /dm_preview/points/data_raw  
    
    /dm_preview/imu/data_raw  
    
    /dm_preview/imu/data_raw_processed  

----------

 ## License

This project is licensed under the [Apache License, Version 2.0](/LICENSE). Copyright 2020 eYs3D Microelectronics, Co., Ltd.


  [1]: http://wiki.ros.org/melodic/Installation/Ubuntu
