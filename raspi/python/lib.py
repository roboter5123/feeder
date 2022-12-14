from gpiozero import Motor
import json
import time
import os

motor_forward_pin = 17
motor_backward_pin = 18

motor = Motor(motor_forward_pin, motor_backward_pin)

def get_settings(_ = None):
    
    if os.path.exists("feeder/raspi/python/settings.json"):
        
        json_settings = open("feeder/raspi/python/settings.json", "r")
        settings = json_settings.read()
        json_settings.close()
    
        return settings
    
    else:
        
        return ""

def set_settings(settings):
    
    settings = json.loads(settings)
    
    if os.path.exists("feeder/raspi/python/settings.json"):
        
        settings_file = open("feeder/raspi/python/settings.json","r")
        settings_file_string = settings_file.read()
        settings_file.close()
        
    else:
        
        _ = open("feeder/raspi/python/settings.json","x")
        _.close()
        settings_file_string = ""
    
    if(settings_file_string == ""):
        
        settings_file = open("feeder/raspi/python/settings.json","w")
        json.dump(settings, settings_file)
        settings_file.close()
        return

    json_settings = json.loads(settings_file_string)
    
    for setting in settings:
        
        if not json_settings.get(setting, False):
            
            json_settings[setting] = settings[setting]
            
    settings_file = open("feeder/raspi/python/settings.json","w")
    json.dump(json_settings, settings_file)
    settings_file.close()
        
    return

def dispense(seconds):

    motor.forward()
    print(f"turning for {seconds} seconds")
    time.sleep(seconds)
    motor.stop()
    print("Stopped turning")
    return 

