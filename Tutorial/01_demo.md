# step for WFH-system

## Dope Prep

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
cd /home/catkin_ws/
catkin_make
source devel/setup.bash
```

4. Launch Dope

Put weight in the ~/catkin_ws/src/dope
```bash
roslaunch dope dope.launch
```

## Pipline

### **> Plugout the side_camera**

### 01_start_locobot
```bash
cd WFH_locobot/
source set_ip.sh
source run_locobot.sh
```

### **> Plugin the side_camera**

## 02_start_vr
```bash
cd WFH_locobot/
source set_wfh_workspace_env.sh
source start_vr.sh
```

### Procman
![vr_procman](Figures/vr_procman.png)

### 03_start_dope


### 04_start_unity

