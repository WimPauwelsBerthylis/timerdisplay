# Timerdisplay

<p float="left">
        <img src="media/frontview.png" alt="1st prototype" width="300" height="200" class="image-style"> 
        <p float="top">
                <img src="media/backview.png" alt="1st prototype" width="150" height="100" class="image-style"> 
                <img src="media/3dview.png" alt="1st prototype" width="150" height="100" class="image-style"> 
        </p>
</p>

This project was created as a timer display for F3Q competitions.
(Aero-tow radio controlled soaring models multi-task event, see [FAI site](https://www.fai.org/page/f3-radio-control-soaring) and [Belgian F3Q site](https://www.f3q.be/) for more information)

> **Disclaimer:** 
> This project is far from complete, especially on the documentation side. Visit regularly for updates although they might take a while due to my busy workload. 
> The first prototype however has been successfully tested and is being used during F3Q events of the Belgian national competition.

# In Action
<video controls width="640" height="360">
  <source src="media/workingdemo_web.MOV" type="video/mov">
  Your browser does not support the video tag.
</video>

Alternatively grab it [here: media/workingdemo_web.MOV](https://github.com/WimPauwelsBerthylis/timerdisplay/blob/main/media/workingdemo_web.mov). Apparently it should be <10MB to be viewable here.

# Dependencies
The control of the matrix display uses a [fork](https://github.com/WimPauwelsBerthylis/rpi-rgb-led-matrix) of the original [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) project.

# Hardware components of the prototype
Why these components? Well, some I had lying around and the others were easily obtainable ;-) so I just build it around what I had available, not much further thought went into it.
In the future this might change to some more professional build if I find some time.

- Main controller: [Raspberry Pi 4B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
- Display interface and RTC: [Adafruit RGB Matrix HAT + RTC for RasPi](https://www.adafruit.com/product/2345)
- Display: [LysonLed](https://www.aliexpress.com/item/1005003999341251.html?spm=a2g0o.store_pc_groupList.8148356.5.18594718awFMNa&pdp_npi=3%40dis%21EUR%21%E2%82%AC%2024%2C69%21%E2%82%AC%2023%2C69%21%21%21%21%21%402103204216953291358368969e24c1%2112000027694112048%21sh%21BE%21139410429)
- Power for display: [Daygreen 12/24V to 5V 10A](https://www.aliexpress.com/item/32676859440.html?spm=a2g0o.order_list.order_list_main.46.21ef1802lT2Zrk)
- Speakers: [Mini External USB Stereo Speaker](https://www.adafruit.com/product/3369)
- Power for the Pi: custom 12V to Adjustable 5V switching regulator (The Pi4 is power hungry and requires more than 5.0V, more towards 5.2V @ 3A)
- Custom bread board interface to the GPIO's
- Custom housing made out of bended aluminium sheets

USB speakers are used because the interface for the display has conflicts with the onboard sound.

!! Use a USB flash drive in the Pi to run from, it will save you a lot of headaches. The SD card gets easily corrupted when not properly shut down.


# INSTALL FROM SCRATCH
- Download the Raspberry Pi Imager from [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)
- Install the Raspberry Pi OS lite (32bit) on a USB stick through the imager. Use the advanced options to enable ssh and set a username (use pi), password and hostname (wifi optional).
- Install the USB stick in the Pi and power on, log in through ssh with:  
    ```
    ssh user@host_or_ip
    ```
- Install git: 
    ```
    sudo apt-get install git
    ```
- Clone [rpi-rgb-led-matrix fork](https://github.com/WimPauwelsBerthylis/rpi-rgb-led-matrix) in your home directory: 
    ```
    git clone https://github.com/WimPauwelsBerthylis/rpi-rgb-led-matrix.git
    ```
- Clone [timerdisplay](https://github.com/WimPauwelsBerthylis/timerdisplay):    
    ```
    git clone https://github.com/WimPauwelsBerthylis/timerdisplay.git
    ```
- navigate into timerdisplay: 
    ```
    cd timerdisplay
    ```
- Create a soft link to the rpi-rgb-led-matrix repo: 
    ```
    ln -s ../rpi-rgb-led-matrix
    ```
- navigate to the rgbmatrix python bindings: 
    ```
    cd rpi-rgb-led-matrix/bindings/python
    ```
- now install some packages to build the rgbmatrix and build it:
    ```  
    sudo apt-get update && sudo apt-get install python3-dev  python3-pillow -y  
    make build-python PYTHON=$(command -v python3)  
    sudo make install-python PYTHON=$(command -v python3)  
    ```
- Create a virtual environment
    ```
    python -m venv venv
    ```
- Install raspberry pi packages:
    ```
    pip install RPi.GPIO
    ```
- Install supporting packages:
    ```
    pip install Pillow
    sudo apt-get install libopenjp2-7

    ```
- Install the packages for audio:
    ```
    sudo apt install espeak
    sudo apt install python3-pyaudio
    sudo apt install python3-pip
    pip install pyttsx3
    pip install pyalsaaudio   
    ```  
    disable onboard audio: ```sudo nano /boot/config.txt```
    ```
    dtparam=audio=off
    ```
    Put the USB sound card as the first fixed audio device:
    ```
    sudo nano /etc/modprobe.d/alsa-base.conf
        options snd-usb-audio index=0

    sudo nano /etc/asound.conf
        defaults.pcm.card 0
        defaults.ctl.card 0
    ```
    Add root user to the audio group:
    ```
    sudo adduser root audio
    ```

- enable the Real Time Clock
    ```
    sudo apt install -y i2c-tools python3-smbus
    sudo nano /boot/config.txt
    ```
    edits the pi configuration and add: 
    ```
    dtoverlay=i2c-rtc,ds1307
    ```
    and uncomment:
    ```
    dtparam=i2c_arm=on    
    ```
    reboot and disable "fake hwclock""
    ```
    sudo reboot
    sudo apt-get -y remove fake-hwclock
    sudo update-rc.d -f fake-hwclock remove
    sudo systemctl disable fake-hwclock
    ```
    edit hwclock-set: ```sudo nano /lib/udev/hwclock-set``` 
    and comment the following lines
    ```
    #if [ -e /run/systemd/system ] ; then
    #    exit 0
    #fi

    #/sbin/hwclock --rtc=$dev --systz
    ```
    Plug in Ethernet or WiFi to let the Pi sync the right time from the Internet. Once that's done, run ```sudo hwclock -w``` to write the time, and another ```sudo hwclock -r``` to read the time. Once the time is set, make sure the coin cell battery is inserted so that the time is saved.        
- test the installation, the display should work now and show the current time and date: 
    ```
    sudo python /home/pi/timerdisplay/application/timerdisplay.py
    ```
- last step is to make the timerdisplay start automatically at boot: 
    ```  
    cd /lib/systemd/system  
    sudo ln -s ~/timerdisplay/timerdisplay.service  
    sudo chmod 644 /lib/systemd/system/timerdisplay.service
    sudo chmod +x /home/pi/timerdisplay/application/timerdisplay.py  
    sudo systemctl daemon-reload  
    sudo systemctl enable timerdisplay.service  
    ```  
- now reboot the system and the display should start automatically:      
    ```
    sudo reboot
    ```

# EASY INSTALL
- Download the Raspberry Pi Imager from [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)
- download the image in /rpi4_img
- Install the image on the USB stick with the Imager  

# Temporary placeholders
### Manual start
Starting the timerdisplay application:
    ```
    sudo python <path/to/>timerdisplay/application/timerdisplay.py (sudo python /home/pi/timerdisplay/application/timerdisplay.py)
    sudo -E env PATH=&PATH python <path/to/>timerdisplay/application/timerdisplay.py (sudo -E env PATH=$PATH python /home/pi/timerdisplay/application/timerdisplay.py)
    ```

### Useful references

Creating the virtual environment:
    ```
    python -m venv `<directory>`              (python -m venv venv)
    ```

Activating the virtual environment:
    ```
    source `<directory>`/bin/activate         (source venv/bin/activate)
    ```

Deactivating the virtual environment
    ```
    deactivate                              (deactivate)
    ```

Deleting the virtual environment
    ```
    deactivate                              (deactivate)
    rm -r `<directory>`                     (rm -r venv)
    ```

Starting a demo (from ~/rpi-rgb-led-matrix/example-api-use):
    ```
    sudo ./demo -D 1 runtext.ppm --led-brightness=20 --led-cols=80 --led-rows=40 --led-slowdown-gpio=4 --led-gpio-mapping=adafruit-hat --led-multiplexing=19
    ```

https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/
https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55a42267

    ```
    sudo systemctl stop timerdisplay
    sudo systemctl start timerdisplay
    ```

USB stick backup:
    ```
    sudo dd if=/dev/sda of=/dev/sdb bs=32M status=progress
    ```
