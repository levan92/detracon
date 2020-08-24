export WORKSPACE=$HOME/Workspace
export DATA=/media/dh/HDD/

xhost +local:docker
docker run -it --gpus all -v $WORKSPACE:$WORKSPACE -v $DATA:$DATA --net=host --ipc host -e DISPLAY=unix$DISPLAY  --privileged -v /dev/:/dev/ levan92/detracon