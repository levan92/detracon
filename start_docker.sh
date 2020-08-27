export WORKSPACE=/drive/spot/detracon
export DATA=/drive/spot/detracon

xhost +local:docker
#local docker build
docker run -it --gpus all -v $WORKSPACE:$WORKSPACE -v $DATA:$DATA --net=host --ipc host -e DISPLAY=unix$DISPLAY  --privileged -v /dev/:/dev/ detracon
#levan
#docker run -it --gpus all -v $WORKSPACE:$WORKSPACE -v $DATA:$DATA --net=host --ipc host -e DISPLAY=unix$DISPLAY  --privileged -v /dev/:/dev/ levan92/detracon