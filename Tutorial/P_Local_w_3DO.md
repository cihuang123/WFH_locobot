# Local mode : wired ethernet connection with VR-3DO mode 

## Application : 
You want to set up the local network, in which your operator site and remote site are under the same domain network, connected by wired ethernet or wifi. And you would like to update the target object pose by using pose-esitmation method (DOPE).


## Hardware and Network setup
![Global_w_VS.](Figures/local_w_3do.PNG)

Operator site : 
- [Machine 1] one PC for running unity (Windows OS) (IP Address: 10.42.0.4)

Remote site : 
- [Machine 2] one NUC for robot control (Ubuntu) (IP Address: 10.42.0.2 - ros master)
- [Machine 3] one PC for running DOPE (Ubuntu) (IP Address: 10.42.0.5)

## Usage

### Machine 1 : Operator site : Unity setting 

#### Step1. Goto the scene (Local_with_VR-3DO_mode sence)

#### Step2. Goto Game Manager > UpdatedIP
- Assign which object needed to update the ros_ip
    - Default setting : 
        - Robot Connector (real) 
        - Robot Connector (human)
        - Camera view_1 
        - Camera view_2 (if you have)
- update the ip address with you ros_master_ip address, in this example, the ros_master_ip is ws://10.42.0.2:9090

### Machine 2 : Remote site : ROS setting 
Remind : 

- suggest run the script for vr script and locobot script separately because of different workspace.
- unplug another D435-camera first if you have one because due to the original script will launch a D435-camera (pyrobot)

#### 1. Clone repo

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
git clone git@github.com:ARG-NCTU/WFH_locobot.git
```

####  2. Pull Docker

``` bash
docker pull yimlaisum2014/locobot:NUC-vr-py2
```
#### 3. Enter Docker
```
NUC $ cd WFH_locobot/Docker/NUC/video_streaming
NUC $ source docker_run.sh
```

#### 4. Start locobot

```bash
Docker $ cd WFH_locobot/
Docker $ source set_ip.sh
Docker $ source run_locobot.sh
```

#### 5. Start WFH-VE procman
```bash
Docker $ cd WFH_locobot/
Docker $ source set_wfh_workspace_env.sh
Docker $ source start_vr.sh
```

### Procman
![vr_procman](Figures/vr_procman.png)

What script needed to launch :
- robridge
- vr_arm
- *side_camera (if you have extra D435 camera)

### Machine 3 : Remote site : DOPE setting

1. Clone repo

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
git clone https://github.com/yimlaisum2014/Deep-Object-Pose.git dope
cd dope/
git checkout devel-exp
```

2. Pull Docker

``` bash
docker pull yimlaisum2014/dope:gpu-noetic
```

3. Enter Docker and make&source workspace

```bash
source docker_run.sh
cd /home/$USER/catkin_ws/
catkin_make
source devel/setup.bash
```

4. Launch Dope

Put weight in the ~/catkin_ws/src/dope and modify the /dope/config/config_pose.yaml
```bash 
roslaunch dope dope.launch
```
