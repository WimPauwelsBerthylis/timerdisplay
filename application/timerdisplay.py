#!/usr/bin/env python

import time
import datetime
import sys
import os
import threading
import RPi.GPIO as GPIO

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../rpi-rgb-led-matrix/bindings/python/'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

# Define state constants
IDLE = 0
TAKEOFF = 1
HOLD = 2
START = 3
INTER1 = 4
INTER2 = 5
INTER3 = 6
FINISH = 7

# Set up GPIO pin number for interrupt
interrupt_pin = 25

# Set up global variables for interrupt flag
interrupt_triggered = False
button_pressed = False
button_bouncetime_active = False
#channel_pressed = None
timezero = 0


# Constants
READTICKPERIOD = 0.1


# Define button press interrupt callback function
def button_press_interrupt_callback(channel):
    global interrupt_triggered
    global button_pressed
    global button_bouncetime_active
    global timezero

    if GPIO.input(channel) == GPIO.LOW and not button_bouncetime_active and not interrupt_triggered:
        timezero = time.perf_counter()
        interrupt_triggered = True
        button_pressed = True
        # Set up timer to reset interrupt flag after debounce period
        button_bouncetime_active = True
        threading.Timer(0.1, reset_interrupt, [channel]).start()

    if GPIO.input(channel) == GPIO.HIGH and not button_bouncetime_active and interrupt_triggered:
        interrupt_triggered = False
        # Set up timer to reset interrupt flag after debounce period
        button_bouncetime_active = True
        threading.Timer(0.1, reset_interrupt, [channel]).start()


# Reset after debouncing period
def reset_interrupt(channel):
    global interrupt_triggered
    global button_bouncetime_active

    button_bouncetime_active = False
    if GPIO.input(channel) != GPIO.LOW:
        interrupt_triggered = False


# Set up GPIO and interrupt
GPIO.setmode(GPIO.BCM)
GPIO.setup(interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(interrupt_pin, GPIO.BOTH, callback=button_press_interrupt_callback)


class MyMatrixBase(object):
    def __init__(self, *args, **kwargs):
        self.options = RGBMatrixOptions()
        self.options.rows = 40
        self.options.cols = 80
        self.options.gpio_slowdown = 4

        self.matrix = RGBMatrix(options=self.options)

    def run(self):
        print("running")

    def start(self):
        try:
            print("Press CTRL-C to stop")
            self.run()
        except KeyboardInterrupt:
            print("\nExiting\n")
            # Clean up GPIO on program exit
            GPIO.cleanup()
            sys.exit(0)


class TimerDisplay(MyMatrixBase):
    def __init__(self, *args, **kwargs):
        super(TimerDisplay, self).__init__(*args, **kwargs)

        # configure the display
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.font1 = graphics.Font()
        self.font2 = graphics.Font()
        self.font3 = graphics.Font()
        self.font4 = graphics.Font()

        # configure variables
        self.current_state = IDLE
        self.state_configured = False
        self.start_time = 0.0
        self.previous_time = 0.0
        self.current_time = 0.0
        self.inter1_time = 0.0
        self.inter2_time = 0.0
        self.inter3_time = 0.0
        self.finish_time = 0.0
        self.checktick = 0.0
        self.pilot = "WPA"

    def run(self):
        print("running timerdisplay")
        global button_pressed
        global interrupt_pin
        global timezero

        # Main loop
        while True:
            self.exec_state()
            self.next_state()

    def exec_state(self):
        global button_pressed
        global timezero

        # Action state machine, each state should be non-blocking
        if self.current_state == IDLE:
            # One-time configure state
            if not self.state_configured:
                print("Current state: IDLE")
                # display
                self.font1.LoadFont("../rpi-rgb-led-matrix/fonts/texgyre-27.bdf")
                self.font2.LoadFont("../rpi-rgb-led-matrix/fonts/6x9.bdf")
                self.textColor1 = graphics.Color(255, 0, 0)
                self.textColor2 = graphics.Color(0, 0, 255)
                # timers
                self.checktick = time.perf_counter()
                self.state_configured = True

            # Recurring actions
            if (time.perf_counter() - self.checktick) >= READTICKPERIOD:
                self.checktick = time.perf_counter()
                self.current_time = datetime.datetime.now()

                if divmod(time.time(), 2)[1] < 1:
                    self.line1 = self.current_time.strftime("%H:%M")
                else:
                    self.line1 = self.current_time.strftime("%H %M")

                self.line2 = self.current_time.strftime("%d-%m-%Y")
                self.offscreen_canvas.Clear()

                graphics.DrawText(self.offscreen_canvas, self.font1, 6, 25, self.textColor1, self.line1)
                graphics.DrawText(self.offscreen_canvas, self.font2, 10, 38, self.textColor2, self.line2)
                self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

        elif self.current_state == TAKEOFF:
            # One-time configure state
            if not self.state_configured:
                print("Current state: TAKEOFF")
                self.font1.LoadFont("../rpi-rgb-led-matrix/fonts/6x9.bdf")
                self.font2.LoadFont("../rpi-rgb-led-matrix/fonts/9x15B.bdf")
                self.textColor1 = graphics.Color(0, 0, 255)
                self.textColor2 = graphics.Color(0, 255, 0)
                self.offscreen_canvas.Clear()
                self.line1 = f"Pilot: {self.pilot:3s}"
                self.line2 = "Takeoff!"
                graphics.DrawText(self.offscreen_canvas, self.font1, 8, 6, self.textColor1, self.line1)
                graphics.DrawText(self.offscreen_canvas, self.font2, 4, 28, self.textColor2, self.line2)
                self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
                self.state_configured = True

        elif self.current_state == HOLD:
            if not self.state_configured:
                print("Current state: HOLD")
                self.checktick = timezero
                self.font1.LoadFont("../rpi-rgb-led-matrix/fonts/6x9.bdf")
                self.font2.LoadFont("../rpi-rgb-led-matrix/fonts/texgyre-27.bdf")
                self.textColor1 = graphics.Color(0, 0, 255)
                self.textColor2 = graphics.Color(0, 255, 0)
                self.downcount = 10
                self.tick = True
                self.state_configured = True

            if self.tick:
                if self.downcount == 0:
                    self.line2 = "GO!"
                    self.xpos = 14
                elif (self.downcount > 0):
                    self.line2 = f"{self.downcount:02d}"
                    self.xpos = 24
                    self.downcount -= 1

                self.offscreen_canvas.Clear()
                graphics.DrawText(self.offscreen_canvas, self.font1, 8, 6, self.textColor1, self.line1)
                graphics.DrawText(self.offscreen_canvas, self.font2, self.xpos, 34, self.textColor2, self.line2)
                self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
                self.tick = False

            if (time.perf_counter() - self.checktick) >= (10-self.downcount):
                self.tick = True 

        elif self.current_state == START:
            if not self.state_configured:
                print("Current state: START")
                self.font1.LoadFont("../rpi-rgb-led-matrix/fonts/6x9.bdf")
                self.font2.LoadFont("../rpi-rgb-led-matrix/fonts/10x20.bdf")
                self.textColor1 = graphics.Color(0, 0, 255)
                self.textColor2 = graphics.Color(0, 255, 0)
                self.line1 = f"Pilot: {self.pilot:3s}"
                self.state_configured = True

            self.current_time = time.perf_counter()
            timediff = self.current_time - self.start_time
            minutes, seconds = divmod(timediff, 60)
            self.line2 = f"{minutes:1.0f}:{seconds:05.2f}"

            self.offscreen_canvas.Clear()
            graphics.DrawText(self.offscreen_canvas, self.font1, 8, 6, self.textColor1, self.line1)
            graphics.DrawText(self.offscreen_canvas, self.font2, 4, 25, self.textColor2, self.line2)
            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
            time.sleep(0.01)

        elif self.current_state == INTER1:
            if not self.state_configured:
                print("Current state: INTER1")
                self.font1.LoadFont("../rpi-rgb-led-matrix/fonts/6x9.bdf")
                self.font2.LoadFont("../rpi-rgb-led-matrix/fonts/10x20.bdf")
                self.font3.LoadFont("../rpi-rgb-led-matrix/fonts/5x8.bdf")
                self.textColor1 = graphics.Color(0, 0, 255)
                self.textColor2 = graphics.Color(0, 255, 0)
                self.textColor3 = graphics.Color(255, 140, 0)
                self.line1 = f"Pilot: {self.pilot:3s}"
                self.state_configured = True

            self.current_time = time.perf_counter()
            timediff = self.current_time - self.start_time
            minutes, seconds = divmod(timediff, 60)
            self.line2 = f"{minutes:1.0f}:{seconds:05.2f}"

            timediff = self.inter1_time - self.start_time
            minutes, seconds = divmod(timediff, 60)
            self.line3 = f"{seconds:04.1f}"

            self.offscreen_canvas.Clear()
            graphics.DrawText(self.offscreen_canvas, self.font1, 8, 6, self.textColor1, self.line1)
            graphics.DrawText(self.offscreen_canvas, self.font2, 4, 25, self.textColor2, self.line2)
            graphics.DrawText(self.offscreen_canvas, self.font3, 5, 40, self.textColor3, self.line3)
            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
            time.sleep(0.01)

        elif self.current_state == INTER2:
            if not self.state_configured:
                print("Current state: INTER2")
                self.font1.LoadFont("../rpi-rgb-led-matrix/fonts/6x9.bdf")
                self.font2.LoadFont("../rpi-rgb-led-matrix/fonts/10x20.bdf")
                self.font3.LoadFont("../rpi-rgb-led-matrix/fonts/5x8.bdf")
                self.textColor1 = graphics.Color(0, 0, 255)
                self.textColor2 = graphics.Color(0, 255, 0)
                self.textColor3 = graphics.Color(255, 140, 0)
                self.line1 = f"Pilot: {self.pilot:3s}"
                self.state_configured = True

            self.current_time = time.perf_counter()
            timediff = self.current_time - self.start_time
            minutes, seconds = divmod(timediff, 60)
            self.line2 = f"{minutes:1.0f}:{seconds:05.2f}"

            timediff = self.inter1_time - self.start_time
            minutes, seconds = divmod(timediff, 60)
            timediff2 = self.inter2_time - self.start_time
            minutes2, seconds2 = divmod(timediff2, 60)
            self.line3 = f"{seconds:04.1f} {seconds2:04.1f}"

            self.offscreen_canvas.Clear()
            graphics.DrawText(self.offscreen_canvas, self.font1, 8, 6, self.textColor1, self.line1)
            graphics.DrawText(self.offscreen_canvas, self.font2, 4, 25, self.textColor2, self.line2)
            graphics.DrawText(self.offscreen_canvas, self.font3, 5, 40, self.textColor3, self.line3)
            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
            time.sleep(0.01)

        elif self.current_state == INTER3:
            if not self.state_configured:
                print("Current state: INTER3")
                self.font1.LoadFont("../rpi-rgb-led-matrix/fonts/6x9.bdf")
                self.font2.LoadFont("../rpi-rgb-led-matrix/fonts/10x20.bdf")
                self.font3.LoadFont("../rpi-rgb-led-matrix/fonts/5x8.bdf")
                self.textColor1 = graphics.Color(0, 0, 255)
                self.textColor2 = graphics.Color(0, 255, 0)
                self.textColor3 = graphics.Color(255, 140, 0)
                self.line1 = f"Pilot: {self.pilot:3s}"
                self.state_configured = True

            self.current_time = time.perf_counter()
            timediff = self.current_time - self.start_time
            minutes, seconds = divmod(timediff, 60)
            self.line2 = f"{minutes:1.0f}:{seconds:05.2f}"

            timediff = self.inter1_time - self.start_time
            minutes, seconds = divmod(timediff, 60)
            timediff2 = self.inter2_time - self.start_time
            minutes2, seconds2 = divmod(timediff2, 60)
            timediff3 = self.inter3_time - self.start_time
            minutes3, seconds3 = divmod(timediff3, 60)
            self.line3 = f"{seconds:04.1f} {seconds2:04.1f} {seconds3:04.1f}"

            self.offscreen_canvas.Clear()
            graphics.DrawText(self.offscreen_canvas, self.font1, 8, 6, self.textColor1, self.line1)
            graphics.DrawText(self.offscreen_canvas, self.font2, 4, 25, self.textColor2, self.line2)
            graphics.DrawText(self.offscreen_canvas, self.font3, 5, 40, self.textColor3, self.line3)
            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
            time.sleep(0.01)

        elif self.current_state == FINISH:
            if not self.state_configured:
                print("Current state: FINISH")
                self.font1.LoadFont("../rpi-rgb-led-matrix/fonts/6x9.bdf")
                self.font2.LoadFont("../rpi-rgb-led-matrix/fonts/10x20.bdf")
                self.font3.LoadFont("../rpi-rgb-led-matrix/fonts/5x8.bdf")
                self.textColor1 = graphics.Color(0, 0, 255)
                self.textColor2 = graphics.Color(0, 255, 0)
                self.textColor3 = graphics.Color(255, 140, 0)
                self.line1 = f"Pilot: {self.pilot:3s}"

                timediff = self.finish_time - self.start_time
                minutes, seconds = divmod(timediff, 60)
                self.line2 = f"{minutes:1.0f}:{seconds:05.2f}"

                timediff = self.inter1_time - self.start_time
                minutes, seconds = divmod(timediff, 60)
                timediff2 = self.inter2_time - self.start_time
                minutes2, seconds2 = divmod(timediff2, 60)
                timediff3 = self.inter3_time - self.start_time
                minutes3, seconds3 = divmod(timediff3, 60)
                self.line3 = f"{seconds:04.1f} {seconds2:04.1f} {seconds3:04.1f}"

                self.offscreen_canvas.Clear()
                graphics.DrawText(self.offscreen_canvas, self.font1, 8, 6, self.textColor1, self.line1)
                graphics.DrawText(self.offscreen_canvas, self.font2, 4, 25, self.textColor2, self.line2)
                graphics.DrawText(self.offscreen_canvas, self.font3, 5, 40, self.textColor3, self.line3)
                self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
                self.state_configured = True

        else:
            print("Unknown state.")

    def next_state(self):
        global button_pressed
        nextstate = self.current_state

        if self.current_state == IDLE:
            if button_pressed:
                self.state_configured = False
                nextstate = TAKEOFF
                button_pressed = False
        elif self.current_state == TAKEOFF:
            if button_pressed:
                self.state_configured = False
                nextstate = HOLD
                button_pressed = False
        elif self.current_state == HOLD:
            if button_pressed:
                self.state_configured = False
                nextstate = START
                self.start_time = timezero
                button_pressed = False
        elif self.current_state == START:
            if button_pressed:
                self.state_configured = False
                nextstate = INTER1
                self.inter1_time = timezero
                button_pressed = False
        elif self.current_state == INTER1:
            if button_pressed:
                self.state_configured = False
                nextstate = INTER2
                self.inter2_time = timezero
                button_pressed = False
        elif self.current_state == INTER2:
            if button_pressed:
                self.state_configured = False
                nextstate = INTER3
                self.inter3_time = timezero
                button_pressed = False
        elif self.current_state == INTER3:
            if button_pressed:
                self.state_configured = False
                nextstate = FINISH
                self.finish_time = timezero
                button_pressed = False
        elif self.current_state == FINISH:
            if button_pressed:
                self.state_configured = False
                nextstate = IDLE
                button_pressed = False
        else:
            print("Unknown state.")

        self.current_state = nextstate        


# main function
if __name__ == "__main__":
    timerdisplay = TimerDisplay()
    timerdisplay.start()
