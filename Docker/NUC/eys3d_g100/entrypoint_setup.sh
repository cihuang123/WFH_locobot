#! /bin/bash

check_envs() {
    DOCKER_CUSTOM_USER_OK=true
    if [ -z ${DOCKER_USER_NAME+x} ]; then
        DOCKER_CUSTOM_USER_OK=false
        return
    fi

    if [ -z ${DOCKER_USER_ID+x} ]; then
        DOCKER_CUSTOM_USER_OK=false
        return
    else
        if ! [ -z "${DOCKER_USER_ID##[0-9]*}" ]; then
            echo -e "\033[1;33mWarning: User-ID should be a number. Falling back to defaults.\033[0m"
            DOCKER_CUSTOM_USER_OK=false
            return
        fi
    fi

    if [ -z ${DOCKER_USER_GROUP_NAME+x} ]; then
        DOCKER_CUSTOM_USER_OK=false
        return
    fi

    if [ -z ${DOCKER_USER_GROUP_ID+x} ]; then
        DOCKER_CUSTOM_USER_OK=false
        return
    else
        if ! [ -z "${DOCKER_USER_GROUP_ID##[0-9]*}" ]; then
            echo -e "\033[1;33mWarning: Group-ID should be a number. Falling back to defaults.\033[0m"
            DOCKER_CUSTOM_USER_OK=false
            return
        fi
    fi
}

setup_env_user() {
    USER=$1
    USER_ID=$2
    GROUP=$3
    GROUP_ID=$4

    ## Create user
    useradd -m $USER

    ## Copy zsh/sh configs
    cp /root/.profile /home/$USER/

    # Copy SSH keys & fix owner
    if [ -d "/root/.ssh" ]; then
        cp -rf /root/.ssh /home/$USER/
        chown -R $USER_ID:$GROUP_ID /home/$USER/.ssh
    fi

    ## Fix owner
    chown -R $USER_ID:$GROUP_ID /home/$USER
    chown -R $USER_ID:$GROUP_ID /home/$USER/.config
    chown -R $USER_ID:$GROUP_ID /home/$USER/.cache
    chown $USER_ID:$GROUP_ID /home/$USER/.profile
    chown $USER_ID:$GROUP_ID /home/$USER/.bashrc

    ## This a trick to keep the evnironmental variables of root which is important!
    echo "if ! [ \"$DOCKER_USER_NAME\" = \"$(id -un)\" ]; then" >>/root/.bashrc
    echo "    exec su $DOCKER_USER_NAME" >>/root/.bashrc
    echo "fi" >>/root/.bashrc

    ## Setup Password-file
    PASSWDCONTENTS=$(grep -v "^${USER}:" /etc/passwd)
    GROUPCONTENTS=$(grep -v -e "^${GROUP}:" -e "^docker:" /etc/group)

    (echo "${PASSWDCONTENTS}" && echo "${USER}:x:$USER_ID:$GROUP_ID::/home/$USER:/bin/bash") >/etc/passwd
    (echo "${GROUPCONTENTS}" && echo "${GROUP}:x:${GROUP_ID}:") >/etc/group
    (if test -f /etc/sudoers; then echo "${USER}  ALL=(ALL)   NOPASSWD: ALL" >>/etc/sudoers; fi)
}

# ---Main---

# Create new user
## Check Inputs
check_envs

## Determine user & Setup Environment
if [ $DOCKER_CUSTOM_USER_OK == true ]; then
    echo -e "\033[0;32m  -->DOCKER_USER Input is set to '$DOCKER_USER_NAME:$DOCKER_USER_ID:$DOCKER_USER_GROUP_NAME:$DOCKER_USER_GROUP_ID'\033[0m"
    echo -e "\033[0;32mSetting up environment for user=$DOCKER_USER_NAME\033[0m"
    setup_env_user $DOCKER_USER_NAME $DOCKER_USER_ID $DOCKER_USER_GROUP_NAME $DOCKER_USER_GROUP_ID
else
    echo -e "\033[0;32m  -->DOCKER_USER* variables not set. You need to set all four! Using 'root'.\033[0m"
    echo -e "\033[0;32mSetting up environment for user=root\033[0m"
    DOCKER_USER_NAME="root"
fi

# Run CMD from Docker
"$@"
