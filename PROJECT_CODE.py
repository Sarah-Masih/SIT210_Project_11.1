#test webhook
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import urllib3
import re
from bs4 import BeautifulSoup
import time
import os
from picamera import PiCamera

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
authorised = 36; #green led pin
unrecognised=37; #red led pin
GPIO.setup(unrecognised, GPIO.OUT)
GPIO.setup(authorised, GPIO.OUT)

reader=SimpleMFRC522()


try:
    
    while True:
        
        #get motion status from Particle cloud through thingspeak.
        
        website= urllib3.PoolManager()
        r= website.request("GET","https://api.thingspeak.com/channels/1418863/fields/1.json?api_key=54I04Y8U06ZS586B&results=2")
     
         #finding motion status and date_time for picture
        #print(r.data[404:405]) 
        status=str(r.data[404:405]) #motion status data
        date_time=str(r.data[365:380])

        motion_detected=status[2] #motion status is stored here: 1 or 0
        
        #checking motion status
        if(motion_detected == "0"):
            print("motion absent")
        else: 
            print("motion present")
            
            print("Capturing image") #take a picture and save it on computer
            camera=PiCamera()
            camera.start_preview(alpha=192)
            time.sleep(1)
            img_file="/home/pi/Desktop/pic"+date_time+".jpg"
            
            camera.capture(img_file)
            camera.stop_preview()

            print("Scanning for key...") #now scan for rfid
            
            id, name = reader.read()
            print(type(id))
            print(id)
            print(name)
            if(id == 551233137661):
                print("Authorised")
                name="Sarah"
                print(name)
                GPIO.output(authorised, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(authorised, GPIO.LOW)
            else:
                print("Unknown key")
                name= ("Unknown key presented");
                GPIO.output(unrecognised, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(unrecognised, GPIO.LOW)
        
            
            
            reader= SimpleMFRC522()
            #post key fob details to webhook, will later be visible to user through gmail and facebook
            r=requests.post("https://maker.ifttt.com/trigger/rfid_swipe/with/key/d0dkshkuDPNl0mVG_eP9OO", params = {"value1": id, "value2" : name, "value3": img_file})
            name=""
            time.sleep(1)
        print("waiting for webhooks to work, motion to stop...") #to allow person to step away before checking again
        time.sleep(45) #wait 45 seconds
        print("checking again...")
    
except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()


