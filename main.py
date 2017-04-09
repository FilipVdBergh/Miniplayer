import Adafruit_CharLCD
import RPi.GPIO as GPIO
import libPiInput.libPiInput as input
import interface
from player_variables import *

RotaryEncoder = input.RotaryEncoder.Worker(RE_A, RE_B)
RotaryEncoderButton = input.Button.Worker(Button_RE)
Button = input.Button.Worker(Button_Left)
PowerButton = input.Button.Worker(Button_Power)

RotaryEncoder.start()
RotaryEncoderButton.start()
Button.start()
PowerButton.start()

lcd = Adafruit_CharLCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,lcd_columns, lcd_rows, lcd_red, lcd_green, lcd_blue, enable_pwm=True)
lcd.set_color(LCD_red, LCD_green, LCD_blue)

miniplayer = interface.Interface(lcd, lms_server, lms_player)
#miniplayer.start()

miniplayer.ui.optimize_redraw = True
miniplayer.ui.print_all()


while True:
    if Button.get_response():
        miniplayer.user_input(1, True)
    if PowerButton.get_response():
        miniplayer.user_input(9, True)
        print("Power")
    RE_delta = RotaryEncoder.get_delta()
    if RE_delta != 0:
        miniplayer.user_input(3, RE_delta)
    if RotaryEncoderButton.get_response():
        miniplayer.user_input(2, True)
    miniplayer.redraw()
