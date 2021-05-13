from guizero import App,Text, PushButton, TextBox, Combo, Box
from gpiozero import MotionSensor
from gpiozero import CPUTemperature
from datetime import datetime
from tkinter import *
import RPi.GPIO as GPIO
from hx711 import HX711
import time
from PIL import ImageTk, Image
import os
import socket
import sys

# ----------------------------------------------------------------------------------
# Global Variables

#Ints --
choice = 1
bottleNumber = 0
count = 0

#Doubles --
InitialOneWeight = 0.0
InitialTwoWeight = 0.0
InitialThreeWeight = 0.0
InitialFourWeight = 0.0
OneWeight = 0.0
TwoWeight = 0.0
ThreeWeight = 0.0
FourWeight = 0.0
OneFluidLevelPercent = 0.0
TwoFluidLevelPercent = 0.0
ThreeFluidLevelPercent = 0.0
FourFluidLevelPercent = 0.0
cpu = CPUTemperature()

#Strings --
DescriptionText = ""
NameText = ""
FluidText = ""
Time = datetime.now()
user = ["", "pi" ]
passw = ["", "seniordesign"]
timeVar = round(time.time() * 1000)
sanitizerOneName = ""
sanitizerTwoName = ""
sanitizerThreeName = ""
sanitizerFourName = ""
sanitizerOneDescription = ""
sanitizerTwoDescription = ""
sanitizerThreeDescription = ""
sanitizerFourDescription = ""

#Booleans --s
dispenseCapable = True
access = False

# ----------------------------------------------------------------------------------
# Pin Setup
GPIO.setmode(GPIO.BCM) # choose BCM
GPIO.setwarnings(False)
GPIO.setup(22, GPIO.IN)  # set a GPIO22 as an input Motion Sensor Dispenser
GPIO.setup(26, GPIO.OUT) # set a GPIO26 as an Relay Output 1
GPIO.setup(14, GPIO.OUT) # set a GPIO14 as an Relay Output 2
GPIO.setup(15, GPIO.OUT) # set a GPIO15 as an Relay Output 3
GPIO.setup(18, GPIO.OUT) # set a GPIO18 as an Relay Output 4
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(26,0)
GPIO.output(14,0)
GPIO.output(15,0)
GPIO.output(18,0)
hx1 = HX711(23,24) # setup a GPIO23/24 as an HX711 Input 1 / Output
hx2 = HX711(25,8) # setup a GPIO25/8 as an HX711 Input 2 / Output
hx3 = HX711(7,20) # setup a GPIO7/1 as an HX711 Input 3 / Output
hx4 = HX711(12,16) # setup a GPIO12/16 as an HX711 Input 4 / Output
hx1.set_reading_format("MSB", "MSB")
hx1.set_reference_unit(4901)
hx2.set_reading_format("MSB", "MSB")
hx2.set_reference_unit(-3644)
hx3.set_reading_format("MSB", "MSB")
hx3.set_reference_unit(-4057)
hx4.set_reading_format("MSB", "MSB")
hx4.set_reference_unit(-4206)
# -----------------------------------------------------------------------------------
# Functions
def get_ip_address():
    ip_address = ""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = str(s.getsockname()[0])
    s.close()
    return ip_address

def MoveLeftUI():
    global choice
    if(choice > 1):
        choice-= 1
        
def MoveRightUI():
    global choice
    if(choice < 4):       
        choice+= 1
        
def DispenseUI():
    global OneFluidLevelPercent
    global TwoFluidLevelPercent
    global ThreeFluidLevelPercent
    global FourFluidLevelPercent
    global InitialOneWeight
    global InitialTwoWeight
    global InitialThreeWeight 
    global InitialFourWeight
    global choice
    global timeVar

    if(dispenseCapable == True and round(time.time() * 1000) - timeVar >= 4500):
        timeVar = round(time.time() * 1000)
        switchButtonState()
        #if(choice == 1 and OneFluidLevelPercent > 5):
        if(choice == 1):
            SleepDispense(26,2)
            updateFluidLevelsOnDispense(choice)
        #elif(choice == 2 and TwoFluidLevelPercent > 5):
        elif(choice == 2):
            SleepDispense(14,2)
            updateFluidLevelsOnDispense(choice)
        #elif(choice == 3 and ThreeFluidLevelPercent < 5):
        elif(choice == 3):
            SleepDispense(15,2)
            updateFluidLevelsOnDispense(choice)
        #elif(choice == 4 and FourFluidLevelPercent < 5):
        elif(choice == 4):
            SleepDispense(18,2)
            updateFluidLevelsOnDispense(choice)
        
        levels = open("/home/pi/Project/Scripts/CurrentFluidLevels.txt","w+") 
        output = [str(OneWeight)+"\n",str(TwoWeight)+"\n",str(ThreeWeight)+"\n",str(FourWeight)]
        levels.writelines(output)
        levels.close()
        switchButtonState()

def SleepDispense(pinNumber, timeToSleep):
    GPIO.output(pinNumber,1)
    time.sleep(timeToSleep)
    GPIO.output(pinNumber,0)
    time.sleep(1)
    
def Calibrate(bottleNumber):
    global InitialOneWeight
    global InitialTwoWeight
    global InitialThreeWeight
    global InitialFourWeight
    
    if(bottleNumber == 1):
        InitialOneWeight = getWeight(1)
    elif(bottleNumber == 2):
        InitialTwoWeight = getWeight(2)
    elif(bottleNumber == 3):
        InitialThreeWeight = getWeight(3)
    elif(bottleNumber == 4):
        InitialFourWeight = getWeight(4)
    elif(bottleNumber == 5):
        InitialOneWeight = getWeight(1)
        InitialTwoWeight = getWeight(2)
        InitialThreeWeight = getWeight(3)
        InitialFourWeight = getWeight(4)

    Initiallevels = open("/home/pi/Project/Scripts/InitialFluidLevels.txt","w+") 
    initialOutput = [str(InitialOneWeight)+"\n",str(InitialTwoWeight)+"\n",str(InitialThreeWeight)+"\n",str(InitialFourWeight)]
    Initiallevels.writelines(initialOutput)
    Initiallevels.close()

def switchButtonState():
    global dispense
    global left
    global right
    global calibrate
    if(dispenseCapable == True):
        if (dispense['state'] == NORMAL and left['state'] == NORMAL and right['state'] == NORMAL and calibrate['state'] == NORMAL):
            dispense['state'] = DISABLED
            left['state'] = DISABLED
            right['state'] = DISABLED
            calibrate['state'] = DISABLED
        elif(dispense['state'] == DISABLED and left['state'] == DISABLED and right['state'] == DISABLED and calibrate['state'] == DISABLED):
            dispense['state'] = NORMAL
            left['state'] = NORMAL
            right['state'] = NORMAL
            calibrate['state'] = NORMAL
     
def zero(bottleNum):
    if(bottleNum == 1):
        hx1.reset()
        hx1.tare_A()
        hx1.tare_B()
    elif(bottleNum == 2):
        hx2.reset()
        hx2.tare_A()
        hx2.tare_B()
    elif(bottleNum == 3):
        hx3.reset()
        hx3.tare_A()
        hx3.tare_B()
    elif(bottleNum == 4):
        hx4.reset()
        hx4.tare_A()
        hx4.tare_B()
    elif(bottleNum == 5):
        hx1.reset()
        hx1.tare_A()
        hx1.tare_B()
        hx2.reset()
        hx2.tare_A()
        hx2.tare_B()
        hx3.reset()
        hx3.tare_A()
        hx3.tare_B()
        hx4.reset()
        hx4.tare_A()
        hx4.tare_B()
 
def getWeight(bottleNum):
    if(bottleNum == 1):
        val = max(0, int(hx1.get_weight(5)))
        #val = hx1.get_weight(5)
        hx1.power_down()
        hx1.power_up()
        return val
    elif(bottleNum == 2):
        val = max(0, int(hx2.get_weight(5)))
        #val = hx2.get_weight(5)
        hx2.power_down()
        hx2.power_up()
        return val
    elif(bottleNum == 3):
        val = max(0, int(hx3.get_weight(5)))
        #val = hx3.get_weight(5)
        hx3.power_down()
        hx3.power_up()      
        return val
    elif(bottleNum == 4):
        val = max(0, int(hx4.get_weight(5)))
        #val = hx4.get_weight(5)
        hx4.power_down()
        hx4.power_up()
        return val

def updateFluidLevelsOnDispense(bottleNumber):
    global OneFluidLevelPercent
    global TwoFluidLevelPercent
    global ThreeFluidLevelPercent
    global FourFluidLevelPercent
    global InitialOneWeight
    global InitialTwoWeight
    global InitialThreeWeight
    global InitialFourWeight
    global OneWeight
    global TwoWeight
    global ThreeWeight
    global FourWeight

    if (bottleNumber == 1):
        if (InitialOneWeight > 0):
            OneWeight = getWeight(1)
            OneFluidLevelPercent = (OneWeight / InitialOneWeight) * 100
        else:
            OneFluidLevelPercent = 0
    elif (bottleNumber == 2):
        if (InitialTwoWeight > 0):
            TwoWeight = getWeight(2)
            TwoFluidLevelPercent = (TwoWeight / InitialTwoWeight) * 100
        else:
            TwoFluidLevelPercent = 0

    elif (bottleNumber == 3):
        if (InitialThreeWeight > 0):
            ThreeWeight = getWeight(3)
            ThreeFluidLevelPercent = (ThreeWeight / InitialThreeWeight) * 100
        else:
            ThreeFluidLevelPercent = 0

    elif (bottleNumber == 4):
        if (InitialFourWeight > 0):
            FourWeight = getWeight(4)
            FourFluidLevelPercent = (FourWeight / InitialFourWeight) * 100
        else:
            FourFluidLevelPercent = 0

def updateFluidLevelsOnBootup():
    global OneFluidLevelPercent
    global TwoFluidLevelPercent
    global ThreeFluidLevelPercent
    global FourFluidLevelPercent
    global InitialOneWeight
    global InitialTwoWeight
    global InitialThreeWeight
    global InitialFourWeight
    global OneWeight
    global TwoWeight
    global ThreeWeight
    global FourWeight

    levels = open("/home/pi/Project/Scripts/CurrentFluidLevels.txt","r+")
    OneWeight = float((levels.readline()))
    TwoWeight = float((levels.readline()))
    ThreeWeight = float((levels.readline()))
    FourWeight = float((levels.readline()))
    levels.close()

    Initiallevels = open("/home/pi/Project/Scripts/InitialFluidLevels.txt","r+") 
    InitialOneWeight = float((Initiallevels.readline()))
    InitialTwoWeight = float((Initiallevels.readline()))
    InitialThreeWeight = float((Initiallevels.readline()))
    InitialFourWeight = float((Initiallevels.readline()))
    Initiallevels.close()

    if(InitialOneWeight > 0):
        OneFluidLevelPercent = (OneWeight / InitialOneWeight) * 100
    else:
        OneFluidLevelPercent = 0
        
    if(InitialTwoWeight > 0):
        TwoFluidLevelPercent = (TwoWeight / InitialTwoWeight) * 100
    else:
        TwoFluidLevelPercent = 0
    if(InitialThreeWeight > 0):
        ThreeFluidLevelPercent = (ThreeWeight / InitialThreeWeight) * 100
    else:
        ThreeFluidLevelPercent = 0
    if(InitialFourWeight > 0):
        FourFluidLevelPercent = (FourWeight / InitialFourWeight) * 100
    else:
        FourFluidLevelPercent = 0

def update():
    global DescriptionText
    global NameText
    global sanitizerOneDescription
    global sanitizerTwoDescription
    global sanitizerThreeDescription
    global sanitizerFourDescription
    global sanitizerOneName
    global sanitizerTwoName
    global sanitizerThreeName
    global sanitizerFourName
    global desctext
    global fluidtext
    global nametext
    global cpuTemp
    global localIP
    global choice
    global OneFluidLevelPercentString
    global TwoFluidLevelPercentString
    global ThreeFluidLevelPercentString
    global FourFluidLevelPercentString
    global fluidReadings
    global outputs
    global Time
    global cpu

    cpu = CPUTemperature()
    Time = datetime.now()
    current = Time.strftime("%X")

    outputs = str("Fluid 1 Weight: " + str(getWeight(1)) + "\n"
                  "Fluid 2 Weight: " + str(getWeight(2)) + "\n"
                  "Fluid 3 Weight: " + str(getWeight(3)) + "\n"
                  "Fluid 4 Weight: " + str(getWeight(4)))
    temp = "Fluid Level is Below 5% \n Dispensing is disabled" 
    if(choice == 1):
        DescriptionText = sanitizerOneDescription
        NameText = sanitizerOneName
        if(OneFluidLevelPercent < 5):
            OneFluidLevelPercentString = temp
        else:
            OneFluidLevelPercentString = (str(int(OneFluidLevelPercent)))
        fluidtext.set("Fluid Level: " + OneFluidLevelPercentString)
    elif(choice == 2):
        DescriptionText = sanitizerTwoDescription
        NameText = sanitizerTwoName
        if(TwoFluidLevelPercent < 5):
             TwoFluidLevelPercentString = temp
        else:
            TwoFluidLevelPercentString = (str(int(TwoFluidLevelPercent)))
        fluidtext.set("Fluid Level: " + TwoFluidLevelPercentString)
    elif(choice == 3):
        DescriptionText = sanitizerThreeDescription
        NameText = sanitizerThreeName
        if(ThreeFluidLevelPercent < 5):
            ThreeFluidLevelPercentString = temp  
        else:          
            ThreeFluidLevelPercentString = (str(int(ThreeFluidLevelPercent))+ "%")
        fluidtext.set("Fluid Level: " + ThreeFluidLevelPercentString)
    elif(choice == 4):
        DescriptionText = sanitizerFourDescription
        NameText = sanitizerFourName
        if(FourFluidLevelPercent < 5):
            FourFluidLevelPercentString = temp 
        else:
            FourFluidLevelPercentString = (str(int(FourFluidLevelPercent))+ "%")
        fluidtext.set("Fluid Level: " + FourFluidLevelPercentString)
    nametext.set("Product: " + NameText)
    desctext.set(DescriptionText)
    fluidReadings.set(outputs)
    curTime.set(current)
    cpuTemp.set("CPU Temperature: " + str(cpu.temperature) + " Celcius")

    # recursive call
    window.after(50,update)

def CalibrateWindow(window):
    global user
    global passw
    global dispenseCapable

    def destroy():
        global dispenseCapable
        login.destroy()
        dispenseCapable = True

    dispenseCapable = False

    login = Toplevel(window)
    login['bg']='#512888'
    login.attributes('-topmost',1)
    login.attributes('-fullscreen',True)
    login.config(cursor="none")
    
    login.columnconfigure(0, weight=1)
    login.columnconfigure(1, weight=1)
    login.rowconfigure(0, weight=1)
    login.rowconfigure(1, weight=1)
    login.rowconfigure(2, weight=1)
    login.rowconfigure(3, weight=2)
    login.rowconfigure(4, weight=1)
    login.rowconfigure(5, weight=1)
    
    login.title('LOGIN SCREEN')
    title = Label(login, text="Login to Calibrate Load Cells using Keyboard or via VNCVIEWER", font=("Helvetica", 20), fg = 'white',bg = '#512888').grid(row=0,column=0,columnspan = 2, sticky = S)
    Label(login,text = ' Username ',font=("Helvetica", 20), height = 1, width = 20, fg = 'white', bg = '#512888').grid(row=1,column=0, sticky = E)
    username = Entry(login, font=("Helvetica", 20), width = 12)
    username.grid(row=1,column=1, columnspan = 2, sticky = W)

    Label(login,text = ' Password ',font=("Helvetica", 20), height = 1, width = 20, fg = 'white', bg = '#512888').grid(row=2,column=0, sticky = E)
    password = Entry(login, show='*',font=("Helvetica", 20,), width = 12)
    password.grid(row=2,column=1, columnspan = 2, sticky = W)

    IP = Label(login, text = "Remote Login IP: " + str(get_ip_address()), font=("Helvetica", 20), fg = 'white', bg = '#512888').grid(row=3,column=0,columnspan = 2)

    Button(login, text='LOGIN',command=lambda: login_user(login,username,password,window),font=("Helvetica", 15), height = 5, width = 15, fg = '#512888', borderwidth = 3).grid(row=4,column=0)
    Button(login, text='Back',command=lambda: destroy(), font=("Helvetica", 15), height = 5, width = 15, fg = '#512888', borderwidth = 3).grid(row=4,column=1)

def login_user(login,username,password,window):
    global user
    global passw
    global access

    '''Check username and password entered are correct'''
    for x in range(0,1):
            if username.get() == user[x] and password.get() == passw[x]:
                access = True
                break
    if(access == True):
        access = False
        #Destroy the current window
        login.destroy()

        # Open Calibration Window
        global calibrate
        global fluidReadings
        global fluids

        fluidReadings = StringVar()

        calibration = Toplevel(window)
        calibration['bg']='#512888'
        calibration.columnconfigure(0, weight=1)
        calibration.columnconfigure(1, weight=1)
        calibration.columnconfigure(2, weight=2)
        calibration.rowconfigure(0, weight=3)
        calibration.rowconfigure(1, weight=1)
        calibration.rowconfigure(2, weight=1)
        calibration.rowconfigure(3, weight=1)
        calibration.rowconfigure(4, weight=1)
        calibration.rowconfigure(5, weight=1)
        calibration.attributes('-fullscreen',True)
        calibration.attributes('-topmost',1)
        calibration.title('Fluid Calibration')
        calibration.config(cursor="none")

        headerCalibrate = Label(calibration, text="Choose a Liquid to Calibrate/Zero", font=("Helvetica", 20), fg = 'white',bg = '#512888').grid(row=0,column=0,columnspan = 3, sticky = N, ipady = 5)
        ZeroLiquid1 = Button(calibration, text='Zero Liquid 1', command =lambda: zero(1), relief="solid",height = 4, width = 12,font=("Helvetica", 8),highlightthickness = 0, borderwidth=2).grid(row=1,column=0, sticky = N)
        ZeroLiquid2 = Button(calibration, text='Zero Liquid 2', command =lambda: zero(2), relief="solid",height = 4, width = 12,font=("Helvetica", 8),highlightthickness = 0, borderwidth=2).grid(row=2,column=0, sticky = N)
        ZeroLiquid3 = Button(calibration, text='Zero Liquid 3', command =lambda: zero(3), relief="solid",height = 4, width = 12,font=("Helvetica", 8),highlightthickness = 0, borderwidth=2).grid(row=3,column=0, sticky = N)
        ZeroLiquid4 = Button(calibration, text='Zero Liquid 4', command =lambda: zero(4), relief="solid",height = 4, width = 12,font=("Helvetica", 8),highlightthickness = 0, borderwidth=2).grid(row=4,column=0, sticky = N)
        ZeroLiquid5 = Button(calibration, text='Zero All', command =lambda: zero(5), relief="solid",height = 4, width = 12,font=("Helvetica", 8),highlightthickness = 0, borderwidth=2).grid(row=5,column=0, sticky = N)
        Liquid1 = Button(calibration, text='Set Liquid 1', command =lambda: Calibrate(1), relief="solid",height = 4, width = 12,font=("Helvetica", 8),highlightthickness = 0, borderwidth=2).grid(row=1,column=1, sticky = N)
        Liquid2 = Button(calibration, text='Set Liquid 2', command =lambda: Calibrate(2), relief="solid",height = 4, width = 12,font=("Helvetica", 8),highlightthickness = 0, borderwidth=2).grid(row=2,column=1, sticky = N)
        Liquid3 = Button(calibration, text='Set Liquid 3', command =lambda: Calibrate(3), relief="solid",height = 4, width = 12,font=("Helvetica", 8),highlightthickness = 0, borderwidth=2).grid(row=3,column=1, sticky = N)
        Liquid4 = Button(calibration, text='Set Liquid 4', command =lambda: Calibrate(4), relief="solid",height = 4, width = 12,font=("Helvetica", 8),highlightthickness = 0, borderwidth=2).grid(row=4,column=1, sticky = N)
        Liquid5 = Button(calibration, text='Set All', command =lambda: Calibrate(5),relief="solid",height = 4, width = 12,font=("Helvetica", 8),highlightthickness = 0, borderwidth=2).grid(row=5,column=1, sticky = N)

        fluids = Label(calibration, textvariable = fluidReadings,font=("Helvetica", 14),fg = 'white',bg = '#512888').grid(row=2,column=2,rowspan = 3, sticky = N)
        done = Button(calibration, text='Done', command =lambda: ExitCalibration(calibration), borderwidth=2, relief="solid",height = 12, width = 20,font=("Helvetica", 10)).grid(row=4,column=2,rowspan = 2, sticky = N)

    else:
        '''Prompt user that either id or password is wrong'''
        message = Label(login,text = 'Username or Password incorrect. Try again!',fg = 'Red', font=("Helvetica", 12), bg = '#512888')
        message.grid(row=3,column=0, columnspan = 2, sticky = S)

def ExitCalibration(calibration):
    global dispenseCapable
    
    calibration.destroy()
    dispenseCapable = True

# -------------------------------------------------------------------------------------    
# App Setup,Creation,Code
if(count == 0):
    updateFluidLevelsOnBootup()
    count += 1

# Main Window Setup
window = Tk()
window['bg']='#512888'
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=3)
window.rowconfigure(2, weight=3)
window.rowconfigure(3, weight=3)
window.rowconfigure(4, weight=3)
window.rowconfigure(5, weight=3)
window.attributes('-fullscreen',True)
window.attributes('-topmost',1)
window.title('Healthy Hands')
window.config(cursor="none")

# Window Setup
fluidReadings = StringVar()
curTime = StringVar()
desctext = StringVar()
fluidtext = StringVar()
cpuTemp = StringVar()
nametext = StringVar()

global left
global right
global dispense
global calibrate

img = ImageTk.PhotoImage(Image.open("/home/pi/Project/Picture/wildcat.jpg"))
img2 = ImageTk.PhotoImage(Image.open("/home/pi/Project/Picture/download.jpeg"))
imageLabel = Label(image=img,highlightthickness = 0, borderwidth=0).grid(row=0,column=0,rowspan = 7, columnspan = 3, sticky = N)
header = Label(window, text="Sanitizing Station", font=("Helvetica", 18), bg = '#512888', fg = 'white').grid(row=0,column=1, sticky = N)
timeLab = Label(window, textvariable = curTime,font=("Helvetica", 11),fg = 'white', bg = '#512888').grid(row=0,column=2, sticky = N)
cpuLabel = Label(window, textvariable = cpuTemp,font=("Helvetica", 11),fg = 'white', bg = '#512888', padx = 5, pady = 5).grid(row=0,column=0, sticky = NW)
left = Button(window, text='Move Left', command =lambda: MoveLeftUI(),highlightthickness = 0, borderwidth=2, height = 6, width = 12, font=("Helvetica", 30))
left.grid(row=1,column=0,rowspan = 3, sticky = N)
right = Button(window, text='Move Right', command =lambda: MoveRightUI(),highlightthickness = 0, borderwidth=2, height = 6, width = 12, font=("Helvetica", 30))
right.grid(row=1,column=2,rowspan = 3, sticky = N)
name = Label(window, textvariable = nametext,font=("Helvetica", 10), fg = 'white',bg = '#512888',borderwidth=2).grid(row=3,column=1, sticky = N)
desc = Label(window, textvariable = desctext,font=("Helvetica", 8), fg = 'white',bg = '#512888',borderwidth=2).grid(row=4,column=1, sticky = N)
dispense = Button(window, text='Dispense', command =lambda: DispenseUI(), borderwidth=2, relief="solid",font=("Helvetica", 20),height = 3, width = 13)
dispense.grid(row=5,column=2, sticky = N)
calibrate = Button(window, text='Login',command =lambda: [CalibrateWindow(window)], borderwidth=2, relief="solid",font=("Helvetica", 20),height = 3, width = 13)
calibrate.grid(row=5,column=0, sticky = N)
fluidLevel = Label(window, textvariable = fluidtext,font=("Helvetica", 8),fg = 'white', bg = '#512888',borderwidth=2).grid(row=5,column=1)
GPIO.add_event_detect(22, GPIO.RISING, callback=DispenseUI)
update()
window.mainloop()
