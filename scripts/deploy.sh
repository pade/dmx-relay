#!/bin/sh

WORK_DIR=$HOME/dmx-relay
BRANCH=main

if [ ! -d $WORK_DIR ] ; then
    git clone https://github.com/pade/dmx-relay.git $WORK_DIR
else
    git -C $WORK_DIR pull
fi
git -C $WORK_DIR checkout $BRANCH

cd $WORK_DIR && pipenv install
sudo cp $WORK_DIR/scripts/dmx-relay.service /etc/systemd/system
sudo systemctl stop dmx-relay.service
sudo systemctl enable dmx-relay.service
sudo systemctl start dmx-relay.service
sudo systemctl daemon-reload

# Deploy shutdown script
sudo cp shutdown.py /usr/local/bin/
sudo chmod +x /usr/local/bin/shutdown.py

sudo cp scripts/shutdown-pi.sh /etc/init.d/
sudo chmod +x /etc/init.d/listen-for-shutdown.sh

sudo update-rc.d shutdown-pi.sh defaults
sudo /etc/init.d/shutdown-pi.sh start
