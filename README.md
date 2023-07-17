# Timerdisplay

add the blabla

Starting the timerdisplay application:
        sudo python /home/admin/timerdisplay/application/timerdisplay.py



# Useful reference

Creating the virtual environment:
        python -m venv <directory>              (python -m venv venv)

Activating the virtual environment:
        source <directory>/bin/activate         (source venv/bin/activate)

Deactivating the virtual environment
        deactivate                              (deactivate)

Deleting the virtual environment
        deactivate                              (deactivate)
        rm -r <directory>                       (rm -r venv)


Starting a demo (from ~/rpi-rgb-led-matrix/example-api-use):
        sudo ./demo -D 1 runtext.ppm --led-brightness=20 --led-cols=80 --led-rows=40 --led-slowdown-gpio=4 --led-gpio-mapping=adafruit-hat --led-multiplexing=19


https://www.helping.ninja/how-to-migrate-raspberry-pi-sd-card-to-a-usb-ssd-speedtest/

https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/

sudo systemctl stop timerdisplay
sudo systemctl start timerdisplay
