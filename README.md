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
> The first prototype however has been successfully tested and is being used during F3Q events of the Belgian national competion.

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
- Power for the Pi: custom 12V to Adjustable 5V switching regulator (The Pi4 is power hungry and requires more than 5.0V, more towards 5.2V @ 3A)
- Custom bread board interface to the GPIO's
- Custom housing made out of bended aluminium sheets

!! Use a USB flash drive in the Pi to run from, it will save you a lot of headaches. The SD card gets easily corrupted when not properly shut down.



# Temporary placeholders
### Manual start
Starting the timerdisplay application:
        sudo python <path/to/>timerdisplay/application/timerdisplay.py (sudo python /home/admin/timerdisplay/application/timerdisplay.py)

### Useful references

Creating the virtual environment:
        python -m venv `<directory>`              (python -m venv venv)

Activating the virtual environment:
        source `<directory>`/bin/activate         (source venv/bin/activate)

Deactivating the virtual environment
        deactivate                              (deactivate)

Deleting the virtual environment
        deactivate                              (deactivate)
        rm -r `<directory>`                       (rm -r venv)

Starting a demo (from ~/rpi-rgb-led-matrix/example-api-use):
        sudo ./demo -D 1 runtext.ppm --led-brightness=20 --led-cols=80 --led-rows=40 --led-slowdown-gpio=4 --led-gpio-mapping=adafruit-hat --led-multiplexing=19

https://www.helping.ninja/how-to-migrate-raspberry-pi-sd-card-to-a-usb-ssd-speedtest/

https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/

sudo systemctl stop timerdisplay
sudo systemctl start timerdisplay
