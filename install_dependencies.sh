cd
sudo apt-get install python3 -y
sudo apt-get update -y
sudo apt-get install python3-pip -y
sudo pip3 install RPi.GPIO
sudo pip3 install smbus
cd
sudo apt-get install wiringpi -y
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
cd
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
tar zxvf bcm2835-1.60.tar.gz
cd bcm2835-1.60/
sudo ./configure
sudo make && sudo make check && sudo make install
sudo pip3 install pillow
sudo pip3 install numpy
sudo apt-get install libopenjp2-7 -y
sudo apt install libtiff -y
sudo apt install libtiff5 -y
sudo apt-get install libatlas-base-dev -y
sudo pip3 install requests
sudo pip3 install dotmap
sudo apt install python-is-python3
sudo pip3 install spidev
sudo apt-get install fonts-dejavu-core -y
