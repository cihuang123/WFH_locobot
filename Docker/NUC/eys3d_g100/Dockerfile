FROM osrf/ros:melodic-desktop-full-bionic

ARG DEBIAN_FRONTEND=noninteractive

###################################### basic-tool #####################################
RUN apt-get update && \
    apt-get install -q -y --no-install-recommends \
    tzdata \
    dirmngr \
    gnupg2 \
    git \
    vim \
    less \
    curl \
    wget \
    sudo \
    cmake \
    g++ \
    clang \
    make \
    ninja-build \
    unzip \
    net-tools \
    lsb-release \
    build-essential \
    bash-completion \
    software-properties-common \
    libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libgtk-3-dev libusb-dev \
    python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev libjpeg9 \
    && rm -rf /var/lib/apt/lists/*

# RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/4.9.0.zip \
#     && unzip opencv.zip \
#     && mkdir -p opencv-4.9.0/build \
#     && cd opencv-4.9.0/build \
#     && cmake -GNinja .. \
#     && ninja

# RUN cd opencv-4.9.0/build \
#     && ninja install

COPY entrypoint_setup.sh /
ENTRYPOINT ["/entrypoint_setup.sh"]