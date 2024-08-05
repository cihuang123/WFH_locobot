#!/usr/bin/env bash

ARGS=("$@")

REPOSITORY="argnctu/locobot"
TAG="eys3d_g100"

IMG="${REPOSITORY}:${TAG}"

USER_NAME="user"
REPO_NAME="WFH_locobot"
CONTAINER_NAME="${REPO_NAME}-${TAG}"

CONTAINER_ID=$(docker ps -aqf "ancestor=${IMG}")
if [ $CONTAINER_ID ]; then
  echo "Attach to docker container $CONTAINER_ID"
  xhost +
  docker exec --privileged -e DISPLAY=${DISPLAY} -e LINES="$(tput lines)" -it ${CONTAINER_ID} bash
  xhost -
  return
fi

XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
touch $XAUTH
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -

docker run \
  -it \
  --rm \
  -e DISPLAY \
  -e XAUTHORITY=/home/$(id -un)/.Xauthority \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e HF_TOKEN=$HF_TOKEN \
  -e "TERM=xterm-256color" \
  -e DOCKER_USER_NAME=$(id -un) \
  -e DOCKER_USER_ID=$(id -u) \
  -e DOCKER_USER_GROUP_NAME=$(id -gn) \
  -e DOCKER_USER_GROUP_ID=$(id -g) \
  -v "/home/${USER}/${REPO_NAME}:/home/sam/${REPO_NAME}" \
  -v "/home/${USER}/${REPO_NAME}/Docker/NUC/${TAG}/.bashrc:/home/$(id -un)/.bashrc" \
  -v "/home/${USER}/${REPO_NAME}/Docker/NUC/${TAG}/tmp/.bash_history:/home/$(id -un)/.bash_history" \
  -v "/home/${USER}/${REPO_NAME}/Docker/NUC/${TAG}/tmp/.cache:/home/sam/.cache" \
  -v "/home/${USER}/${REPO_NAME}/Docker/NUC/${TAG}/tmp/.config:/home/sam/.config" \
  -v "/etc/localtime:/etc/localtime:ro" \
  -v "/dev:/dev" \
  -v "/var/run/docker.sock:/var/run/docker.sock" \
  -v $HOME/.Xauthority:/home/$(id -un)/.Xauthority \
  -v "/tmp/.X11-unix:/tmp/.X11-unix:rw" \
  -v $HOME/.ssh:/root/.ssh:ro \
  --workdir "/home/sam/${REPO_NAME}" \
  --name "${CONTAINER_NAME}" \
  --network host \
  --privileged \
  "${IMG}" \
  bash
