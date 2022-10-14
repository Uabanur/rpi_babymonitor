WORKING_DIR=/home/pi/projects/babymonitor
echo "\ntransferring root files"
scp ./* pi@pi1.local:$WORKING_DIR

echo "\ntranferring templates"
TEMPLATES_DIR=$WORKING_DIR/templates
scp ./templates/* pi@pi1.local:$TEMPLATES_DIR

echo "\ntransferring images"
IMAGES_DIR=$WORKING_DIR/images
scp ./images/* pi@pi1.local:$IMAGES_DIR
