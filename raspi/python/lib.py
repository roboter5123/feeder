from gpiozero import Motor
import json
import time
import schedule
import os

motor_forward_pin = 17
motor_backward_pin = 18

motor = Motor(motor_forward_pin, motor_backward_pin)

def get_settings() -> dict:
    """
    This method gets the settings from feeder/raspi/python/settings.json 
    and returns them as a dict.
    """
    
    if os.path.exists("feeder/raspi/python/settings.json"):
        
        json_settings = open("feeder/raspi/python/settings.json", "r")
        settings = json.load(json_settings)
        json_settings.close()
    
        return settings
    
    else:
        
        return {}

def set_settings(settings: dict) -> None:
    """
    This method sets the settings in feeder/raspi/python/settings.json.
    If the file doesn't exist it creates it.
    If the file exists it parses the settings, replaces unmatching ones and adds in non existent ones.
    """
    
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

    json_settings = settings
    
    for setting in json.loads(settings_file_string):
        
        if not json_settings.get(setting, False) or json_settings.get(setting, False) != settings.get(setting):
            
            json_settings[setting] = settings[setting]
            
    settings_file = open("feeder/raspi/python/settings.json","w")
    json.dump(json_settings, settings_file)
    settings_file.close()
        
    return

def dispense(seconds: int) -> None:

    motor.forward()
    print(f"turning for {seconds} seconds")
    time.sleep(seconds)
    motor.stop()
    print("Stopped turning")
    return 

