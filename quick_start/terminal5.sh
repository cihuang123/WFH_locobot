#!/bin/bash

source ~/WFH_locobot/environment.sh
source ~/WFH_locobot/set_ip.sh $1 $2
roslaunch rosbridge_server rosbridge_websocket.launch


